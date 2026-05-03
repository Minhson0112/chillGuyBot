import random
from datetime import datetime, timedelta, timezone

from bot.cache.userDailyTaskCache import userDailyTaskCache
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.dailyTaskMasterRepository import DailyTaskMasterRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userDailyTaskRepository import UserDailyTaskRepository


class DailyTaskService:
    TASK_COUNT_PER_DAY = 5
    GMT7 = timezone(timedelta(hours=7))

    TASK_TYPE_CHAT_MESSAGE = "chat_message"

    def getOrCreateTodayTasks(self, userId: int):
        today = self.getTodayDate()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)
            dailyTaskMasterRepository = DailyTaskMasterRepository(session)
            userDailyTaskRepository = UserDailyTaskRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            todayTasks = userDailyTaskRepository.findByUserIdAndTaskDate(
                userId=userId,
                taskDate=today,
            )

            isNew = False

            if not todayTasks:
                taskMasters = dailyTaskMasterRepository.findActiveTasksByFarmLevel(farm.farm_level)

                if len(taskMasters) < self.TASK_COUNT_PER_DAY:
                    return {
                        "success": False,
                        "message": (
                            f"Không đủ daily task master để random. "
                            f"Cần **{self.TASK_COUNT_PER_DAY}**, hiện có **{len(taskMasters)}**."
                        ),
                    }

                selectedTaskMasters = self.weightedSampleWithoutReplacement(
                    taskMasters,
                    self.TASK_COUNT_PER_DAY,
                )

                for index, taskMaster in enumerate(selectedTaskMasters):
                    userDailyTaskRepository.createFromMaster(
                        userId=userId,
                        taskDate=today,
                        slotNo=index + 1,
                        taskMaster=taskMaster,
                    )

                session.commit()

                isNew = True

                todayTasks = userDailyTaskRepository.findByUserIdAndTaskDate(
                    userId=userId,
                    taskDate=today,
                )

            cachedTaskMap = self.buildCachedTaskMap(
                userId=userId,
                taskDate=today,
            )

            return {
                "success": True,
                "message": self.buildTaskMessage(
                    tasks=todayTasks,
                    isNew=isNew,
                    cachedTaskMap=cachedTaskMap,
                ),
            }

    def buildCachedTaskMap(
        self,
        userId: int,
        taskDate,
    ):
        cacheKey = (userId, taskDate)
        cachedTasks = userDailyTaskCache.get(cacheKey, [])

        return {
            cachedTask["id"]: cachedTask
            for cachedTask in cachedTasks
        }

    def weightedSampleWithoutReplacement(
        self,
        taskMasters,
        count: int,
    ):
        selectedTaskMasters = []
        remainingTaskMasters = list(taskMasters)

        while len(selectedTaskMasters) < count and remainingTaskMasters:
            totalWeight = sum(taskMaster.weight for taskMaster in remainingTaskMasters)
            randomPoint = random.uniform(0, totalWeight)
            currentWeight = 0

            for taskMaster in remainingTaskMasters:
                currentWeight += taskMaster.weight

                if currentWeight >= randomPoint:
                    selectedTaskMasters.append(taskMaster)
                    remainingTaskMasters.remove(taskMaster)
                    break

        return selectedTaskMasters

    def buildTaskMessage(
        self,
        tasks,
        isNew: bool,
        cachedTaskMap=None,
    ):
        if cachedTaskMap is None:
            cachedTaskMap = {}

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expEmoji = FARM_GAME_EMOJI["exp"]

        title = "Daily task hôm nay"

        if isNew:
            title += "\nBạn đã nhận 5 task mới cho hôm nay."

        lines = [title]

        for task in tasks:
            progressValue = self.getDisplayProgressValue(task, cachedTaskMap)
            status = self.getDisplayStatus(task, cachedTaskMap)
            statusText = "Hoàn thành" if status == "completed" else "Đang làm"

            lines.append(
                "\n"
                f"**{task.slot_no}. {task.task_name}**\n"
                f"{task.description}\n"
                f"Tiến độ: **{self.formatProgress(task, progressValue)}**\n"
                f"Phần thưởng: **{self.formatNumber(task.reward_chill_coin)}** {chillCoinEmoji} "
                f"+ **{self.formatNumber(task.reward_exp)}** {expEmoji}\n"
                f"Trạng thái: **{statusText}**"
            )

        return "\n".join(lines)

    def getDisplayProgressValue(
        self,
        task,
        cachedTaskMap,
    ):
        cachedTask = cachedTaskMap.get(task.id)

        if cachedTask is None:
            return task.progress_value

        if task.task_type != self.TASK_TYPE_CHAT_MESSAGE:
            return task.progress_value

        return cachedTask.get("progress_value", task.progress_value)

    def getDisplayStatus(
        self,
        task,
        cachedTaskMap,
    ):
        cachedTask = cachedTaskMap.get(task.id)

        if cachedTask is None:
            return task.status

        if task.task_type != self.TASK_TYPE_CHAT_MESSAGE:
            return task.status

        return cachedTask.get("status", task.status)

    def formatProgress(
        self,
        task,
        progressValue: int,
    ):
        if task.task_type == "voice_time":
            return (
                f"{self.formatDuration(progressValue)}"
                f"/{self.formatDuration(task.required_value)}"
            )

        return (
            f"{self.formatNumber(progressValue)}"
            f"/{self.formatNumber(task.required_value)}"
        )

    def formatDuration(self, seconds: int):
        minutes = seconds // 60
        remainSeconds = seconds % 60

        if minutes <= 0:
            return f"{remainSeconds}s"

        if remainSeconds <= 0:
            return f"{minutes}m"

        return f"{minutes}m{remainSeconds:02d}s"

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()

    def formatNumber(self, number: int):
        return f"{number:,}"