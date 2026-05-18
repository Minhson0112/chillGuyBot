from bot.models.userTool import UserTool
from sqlalchemy.orm import joinedload

class UserToolRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        toolTemplateId: int,
        currentDurability: int,
        status: str,
    ):
        userTool = UserTool(
            user_id=userId,
            item_id=itemId,
            tool_template_id=toolTemplateId,
            current_durability=currentDurability,
            status=status,
        )

        self.session.add(userTool)
        self.session.flush()

        return userTool
    
    def countByUserId(self, userId: int):
        return (
            self.session.query(UserTool)
            .filter(UserTool.user_id == userId)
            .count()
        )

    def findByUserIdAndPage(
        self,
        userId: int,
        page: int,
        perPage: int,
    ):
        offset = (page - 1) * perPage

        return (
            self.session.query(UserTool)
            .options(
                joinedload(UserTool.item),
                joinedload(UserTool.tool_template),
                joinedload(UserTool.farm_tool_equipment),
            )
            .filter(UserTool.user_id == userId)
            .order_by(UserTool.id.asc())
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def findByIdWithRelations(self, userToolId: int):
        return (
            self.session.query(UserTool)
            .options(
                joinedload(UserTool.item),
                joinedload(UserTool.tool_template),
                joinedload(UserTool.farm_tool_equipment),
            )
            .filter(UserTool.id == userToolId)
            .first()
        )
    
    def updateStatus(self, userTool, status: str):
        userTool.status = status

        self.session.flush()

        return userTool