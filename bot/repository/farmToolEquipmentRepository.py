from sqlalchemy.orm import joinedload

from bot.models.farmToolEquipment import FarmToolEquipment
from bot.models.userTool import UserTool


class FarmToolEquipmentRepository:
    def __init__(self, session):
        self.session = session

    def findByFarmIdAndToolType(
        self,
        farmId: int,
        toolType: str,
    ):
        return (
            self.session.query(FarmToolEquipment)
            .options(joinedload(FarmToolEquipment.user_tool))
            .filter(
                FarmToolEquipment.farm_id == farmId,
                FarmToolEquipment.tool_type == toolType,
            )
            .first()
        )

    def create(
        self,
        farmId: int,
        toolType: str,
        userToolId: int,
    ):
        farmToolEquipment = FarmToolEquipment(
            farm_id=farmId,
            tool_type=toolType,
            user_tool_id=userToolId,
        )

        self.session.add(farmToolEquipment)
        self.session.flush()

        return farmToolEquipment

    def updateUserTool(
        self,
        farmToolEquipment,
        userToolId: int,
    ):
        farmToolEquipment.user_tool_id = userToolId

        self.session.flush()

        return farmToolEquipment
    
    def findByFarmIdWithToolData(self, farmId: int):
        return (
            self.session.query(FarmToolEquipment)
            .options(
                joinedload(FarmToolEquipment.user_tool).joinedload(UserTool.item),
                joinedload(FarmToolEquipment.user_tool).joinedload(UserTool.tool_template),
            )
            .filter(FarmToolEquipment.farm_id == farmId)
            .all()
        )
    
    def findByFarmIdAndToolTypeWithToolData(
        self,
        farmId: int,
        toolType: str,
    ):
        return (
            self.session.query(FarmToolEquipment)
            .options(
                joinedload(FarmToolEquipment.user_tool).joinedload(UserTool.item),
                joinedload(FarmToolEquipment.user_tool).joinedload(UserTool.tool_template),
            )
            .filter(
                FarmToolEquipment.farm_id == farmId,
                FarmToolEquipment.tool_type == toolType,
            )
            .first()
        )