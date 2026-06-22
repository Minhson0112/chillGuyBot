from datetime import datetime, timedelta, timezone

from bot.helper.numberFormatHelper import formatNumber
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userDailyTaskRepository import UserDailyTaskRepository


class DailyTaskProgressService:
    GMT7 = timezone(timedelta(hours=7))

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"

    def __init__(self, session):
        self.session = session

    def addProgress(
        self,
        userId: int,
        taskType: str,
        amount: int = 1,
        targetItemId: int = None,
        targetCropId: int = None,
        targetChannelId: int = None,
        taskDate=None,
    ):
        if amount <= 0:
            return []

        if taskDate is None:
            taskDate = self.getTodayDate()

        userDailyTaskRepository = UserDailyTaskRepository(self.session)
        memberRepository = MemberRepository(self.session)
        farmRepository = FarmRepository(self.session)

        tasks = userDailyTaskRepository.findInProgressTasksByUserDateAndType(
            userId=userId,
            taskDate=taskDate,
            taskType=taskType,
        )

        if not tasks:
            return []

        member = memberRepository.findByUserId(userId)
        farm = farmRepository.findByUserId(userId)

        completedTasks = []

        for task in tasks:
            if not self.isTaskMatched(
                task=task,
                targetItemId=targetItemId,
                targetCropId=targetCropId,
                targetChannelId=targetChannelId,
            ):
                continue

            task.progress_value = min(
                task.progress_value + amount,
                task.required_value,
            )

            if task.progress_value < task.required_value:
                continue

            now = datetime.now()

            task.status = self.STATUS_COMPLETED
            task.completed_at = now
            task.reward_received_at = now

            if member is not None:
                member.chill_coin += task.reward_chill_coin

            if farm is not None:
                farmRepository.increaseFarmExp(
                    farm=farm,
                    exp=task.reward_exp,
                )

            completedTasks.append(task)

        self.session.flush()

        return completedTasks

    def isTaskMatched(
        self,
        task,
        targetItemId: int = None,
        targetCropId: int = None,
        targetChannelId: int = None,
    ):
        if task.target_item_id is not None and task.target_item_id != targetItemId:
            return False

        if task.target_crop_id is not None and task.target_crop_id != targetCropId:
            return False

        if task.target_channel_id is not None and task.target_channel_id != targetChannelId:
            return False

        return True

    def buildCompletedTaskMessage(self, completedTasks):
        if not completedTasks:
            return None

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expEmoji = FARM_GAME_EMOJI["exp"]

        messages = []

        for task in completedTasks:
            messages.append(
                f"Hoàn thành daily task: **{task.task_name}**\n"
                f"Nhận được **{formatNumber(task.reward_chill_coin)}** {chillCoinEmoji} "
                f"+ **{formatNumber(task.reward_exp)}** {expEmoji}"
            )

        return "\n\n".join(messages)
    
    def completeTaskById(
        self,
        userId: int,
        taskId: int,
    ):
        userDailyTaskRepository = UserDailyTaskRepository(self.session)
        memberRepository = MemberRepository(self.session)
        farmRepository = FarmRepository(self.session)

        task = userDailyTaskRepository.findInProgressByIdAndUserId(
            taskId=taskId,
            userId=userId,
        )

        if task is None:
            return []

        now = datetime.now()

        task.progress_value = task.required_value
        task.status = self.STATUS_COMPLETED
        task.completed_at = now
        task.reward_received_at = now

        member = memberRepository.findByUserId(userId)

        if member is not None:
            member.chill_coin += task.reward_chill_coin

        farm = farmRepository.findByUserId(userId)

        if farm is not None:
            farmRepository.increaseFarmExp(
                farm=farm,
                exp=task.reward_exp,
            )

        self.session.flush()

        return [task]

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()
