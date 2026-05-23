import random
from datetime import datetime, timedelta, timezone

from bot.cache.userDailyTaskCache import userDailyTaskCache, userDailyTaskLoadedCache
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
    TASK_TYPE_VOICE_TIME = "voice_time"

    STATUS_COMPLETED = "completed"

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

            self.syncTodayTasksToCache(
                userId=userId,
                taskDate=today,
                tasks=todayTasks,
            )

            cachedTaskMap = self.buildCachedTaskMap(
                userId=userId,
                taskDate=today,
            )

            return {
                "success": True,
                "embedData": self.buildTaskEmbedData(
                    tasks=todayTasks,
                    taskDate=today,
                    isNew=isNew,
                    cachedTaskMap=cachedTaskMap,
                ),
            }

    def syncTodayTasksToCache(
        self,
        userId: int,
        taskDate,
        tasks,
    ):
        cacheKey = (userId, taskDate)
        existingCachedTaskMap = self.buildCachedTaskMap(
            userId=userId,
            taskDate=taskDate,
        )

        userDailyTaskCache[cacheKey] = [
            self.buildCacheTaskData(
                task=task,
                existingCachedTask=existingCachedTaskMap.get(task.id),
            )
            for task in tasks
        ]

        userDailyTaskLoadedCache.add(cacheKey)

    def buildCacheTaskData(
        self,
        task,
        existingCachedTask,
    ):
        progressValue = task.progress_value
        status = task.status

        if task.task_type == self.TASK_TYPE_CHAT_MESSAGE and existingCachedTask is not None:
            progressValue = max(
                progressValue,
                existingCachedTask.get("progress_value", progressValue),
            )

            if existingCachedTask.get("status") == self.STATUS_COMPLETED:
                status = self.STATUS_COMPLETED

        return {
            "id": task.id,
            "task_type": task.task_type,
            "target_item_id": task.target_item_id,
            "target_crop_id": task.target_crop_id,
            "target_channel_id": task.target_channel_id,
            "required_value": task.required_value,
            "progress_value": progressValue,
            "status": status,
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

            if totalWeight <= 0:
                break

            randomPoint = random.uniform(0, totalWeight)
            currentWeight = 0

            for taskMaster in remainingTaskMasters:
                currentWeight += taskMaster.weight

                if currentWeight >= randomPoint:
                    selectedTaskMasters.append(taskMaster)
                    remainingTaskMasters.remove(taskMaster)
                    break

        return selectedTaskMasters

    def buildTaskEmbedData(
        self,
        tasks,
        taskDate,
        isNew: bool,
        cachedTaskMap=None,
    ):
        if cachedTaskMap is None:
            cachedTaskMap = {}

        completedCount = self.countCompletedTasks(tasks, cachedTaskMap)
        totalCount = len(tasks)

        title = "Daily Task"

        descriptionLines = [
            f"Ngày: **{taskDate.strftime('%d/%m/%Y')}**",
            f"Tiến độ hôm nay: **{completedCount}/{totalCount}** task đã hoàn thành",
        ]

        if isNew:
            descriptionLines.append("Bạn đã nhận **5 task mới** cho hôm nay.")

        fields = []

        for task in tasks:
            fields.append(
                {
                    "name": self.buildTaskFieldName(task, cachedTaskMap),
                    "value": self.buildTaskFieldValue(task, cachedTaskMap),
                }
            )

        return {
            "title": title,
            "description": "\n".join(descriptionLines),
            "fields": fields,
            "footer": "Dùng cg task để xem lại tiến độ daily task hôm nay.",
        }

    def buildTaskFieldName(
        self,
        task,
        cachedTaskMap,
    ):
        status = self.getDisplayStatus(task, cachedTaskMap)

        if status == self.STATUS_COMPLETED:
            statusText = "Hoàn thành"
        else:
            statusText = "Đang làm"

        return f"{task.slot_no}. {task.task_name} — {statusText}"

    def buildTaskFieldValue(
        self,
        task,
        cachedTaskMap,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expEmoji = FARM_GAME_EMOJI["exp"]

        progressValue = self.getDisplayProgressValue(task, cachedTaskMap)
        progressText = self.formatProgress(task, progressValue)
        progressBar = self.buildProgressBar(
            progressValue=progressValue,
            requiredValue=task.required_value,
        )

        rewardText = (
            f"**{self.formatNumber(task.reward_chill_coin)}** {chillCoinEmoji} "
            f"+ **{self.formatNumber(task.reward_exp)}** {expEmoji}"
        )

        return (
            f"{task.description}\n"
            f"`{progressBar}` **{progressText}**\n"
            f"Phần thưởng: {rewardText}"
        )

    def countCompletedTasks(
        self,
        tasks,
        cachedTaskMap,
    ):
        completedCount = 0

        for task in tasks:
            status = self.getDisplayStatus(task, cachedTaskMap)

            if status == self.STATUS_COMPLETED:
                completedCount += 1

        return completedCount

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
        if task.task_type == self.TASK_TYPE_VOICE_TIME:
            return (
                f"{self.formatDuration(progressValue)}"
                f"/{self.formatDuration(task.required_value)}"
            )

        return (
            f"{self.formatNumber(progressValue)}"
            f"/{self.formatNumber(task.required_value)}"
        )

    def buildProgressBar(
        self,
        progressValue: int,
        requiredValue: int,
    ):
        totalBlock = 10

        if requiredValue <= 0:
            return "░" * totalBlock

        progressRate = min(progressValue / requiredValue, 1)
        filledBlock = int(progressRate * totalBlock)
        emptyBlock = totalBlock - filledBlock

        return "█" * filledBlock + "░" * emptyBlock

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
