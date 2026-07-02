import random
from datetime import datetime, timedelta, timezone

from bot.helper.numberFormatHelper import formatNumber
from bot.cache.userDailyTaskCache import userDailyTaskCache, userDailyTaskLoadedCache
from bot.config.database import getDbSession
from bot.helper.timeFormatHelper import formatCompactDuration
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
                "imageData": self.buildTaskImageData(
                    tasks=todayTasks,
                    taskDate=today,
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

    def buildTaskImageData(
        self,
        tasks,
        taskDate,
        cachedTaskMap=None,
    ):
        if cachedTaskMap is None:
            cachedTaskMap = {}

        taskData = []

        for task in tasks:
            progressValue = self.getDisplayProgressValue(task, cachedTaskMap)
            taskData.append(
                {
                    "taskName": task.task_name,
                    "description": task.description or "",
                    "progressValue": progressValue,
                    "requiredValue": task.required_value,
                    "progressText": self.formatProgress(task, progressValue),
                    "rewardChillCoin": task.reward_chill_coin,
                    "rewardExp": task.reward_exp,
                }
            )

        return {
            "taskDate": taskDate,
            "tasks": taskData,
        }

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

    def formatProgress(
        self,
        task,
        progressValue: int,
    ):
        if task.task_type == self.TASK_TYPE_VOICE_TIME:
            return (
                f"{formatCompactDuration(progressValue)}"
                f"/{formatCompactDuration(task.required_value)}"
            )

        return (
            f"{formatNumber(progressValue)}"
            f"/{formatNumber(task.required_value)}"
        )

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()
