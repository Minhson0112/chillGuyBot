from datetime import datetime, timedelta, timezone

from bot.cache.userDailyTaskCache import (
    userDailyTaskCache,
    userDailyTaskLoadedCache,
    userDailyTaskProgressDeltaCache,
)
from bot.config.database import getDbSession
from bot.repository.userDailyTaskRepository import UserDailyTaskRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class DailyTaskChatCacheService:
    DAILY_TASK_TYPE_CHAT_MESSAGE = "chat_message"
    GMT7 = timezone(timedelta(hours=7))

    def addChatProgress(self, message):
        if message.author.bot:
            return None

        if message.guild is None:
            return None

        userId = message.author.id
        channelId = message.channel.id
        today = self.getTodayDate()

        self.loadTodayTasksIfNeeded(userId, today)

        cacheKey = (userId, today)
        tasks = userDailyTaskCache.get(cacheKey, [])

        completedMessages = []

        for task in tasks:
            if task["status"] == "completed":
                continue

            if task["task_type"] != self.DAILY_TASK_TYPE_CHAT_MESSAGE:
                continue

            if task["target_channel_id"] is not None and task["target_channel_id"] != channelId:
                continue

            task["progress_value"] = min(
                task["progress_value"] + 1,
                task["required_value"],
            )

            userDailyTaskProgressDeltaCache[task["id"]] = (
                userDailyTaskProgressDeltaCache.get(task["id"], 0) + 1
            )

            if task["progress_value"] >= task["required_value"]:
                completedMessage = self.completeTask(
                    userId=userId,
                    taskId=task["id"],
                )

                if completedMessage is not None:
                    task["status"] = "completed"
                    completedMessages.append(completedMessage)

        if not completedMessages:
            return None

        return "\n\n".join(completedMessages)

    def loadTodayTasksIfNeeded(
        self,
        userId: int,
        today,
    ):
        loadedKey = (userId, today)

        if loadedKey in userDailyTaskLoadedCache:
            return

        with getDbSession() as session:
            userDailyTaskRepository = UserDailyTaskRepository(session)

            tasks = userDailyTaskRepository.findByUserIdAndTaskDate(
                userId=userId,
                taskDate=today,
            )

            userDailyTaskCache[(userId, today)] = [
                {
                    "id": task.id,
                    "task_type": task.task_type,
                    "target_item_id": task.target_item_id,
                    "target_crop_id": task.target_crop_id,
                    "target_channel_id": task.target_channel_id,
                    "required_value": task.required_value,
                    "progress_value": task.progress_value,
                    "status": task.status,
                }
                for task in tasks
            ]

            userDailyTaskLoadedCache.add(loadedKey)

    def completeTask(
        self,
        userId: int,
        taskId: int,
    ):
        with getDbSession() as session:
            dailyTaskProgressService = DailyTaskProgressService(session)

            completedTasks = dailyTaskProgressService.completeTaskById(
                userId=userId,
                taskId=taskId,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedTasks,
            )

            session.commit()

            userDailyTaskProgressDeltaCache.pop(taskId, None)

            return dailyTaskMessage

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()