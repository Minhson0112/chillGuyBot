from sqlalchemy import asc
from sqlalchemy.orm import joinedload

from bot.models.userDailyTask import UserDailyTask


class UserDailyTaskRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndTaskDate(
        self,
        userId: int,
        taskDate,
    ):
        return (
            self.session.query(UserDailyTask)
            .options(
                joinedload(UserDailyTask.targetItem),
                joinedload(UserDailyTask.targetCrop),
            )
            .filter(UserDailyTask.user_id == userId)
            .filter(UserDailyTask.task_date == taskDate)
            .order_by(asc(UserDailyTask.slot_no))
            .all()
        )

    def createFromMaster(
        self,
        userId: int,
        taskDate,
        slotNo: int,
        taskMaster,
    ):
        userDailyTask = UserDailyTask(
            user_id=userId,
            task_date=taskDate,
            slot_no=slotNo,
            task_master_id=taskMaster.id,
            task_code=taskMaster.task_code,
            task_name=taskMaster.task_name,
            description=taskMaster.description,
            task_type=taskMaster.task_type,
            target_item_id=taskMaster.target_item_id,
            target_crop_id=taskMaster.target_crop_id,
            target_channel_id=taskMaster.target_channel_id,
            required_value=taskMaster.required_value,
            progress_value=0,
            reward_chill_coin=taskMaster.reward_chill_coin,
            reward_exp=taskMaster.reward_exp,
            status="in_progress",
        )

        self.session.add(userDailyTask)
        self.session.flush()

        return userDailyTask
    
    def findInProgressTasksByUserDateAndType(
        self,
        userId: int,
        taskDate,
        taskType: str,
    ):
        return (
            self.session.query(UserDailyTask)
            .filter(UserDailyTask.user_id == userId)
            .filter(UserDailyTask.task_date == taskDate)
            .filter(UserDailyTask.task_type == taskType)
            .filter(UserDailyTask.status == "in_progress")
            .order_by(asc(UserDailyTask.slot_no))
            .all()
        )
    
    def findInProgressByIdAndUserId(
        self,
        taskId: int,
        userId: int,
    ):
        return (
            self.session.query(UserDailyTask)
            .filter(UserDailyTask.id == taskId)
            .filter(UserDailyTask.user_id == userId)
            .filter(UserDailyTask.status == "in_progress")
            .first()
        )