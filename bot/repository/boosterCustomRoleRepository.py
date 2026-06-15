from bot.enums.boosterCustomRoleStatus import BoosterCustomRoleStatus
from bot.models.boosterCustomRole import BoosterCustomRole


class BoosterCustomRoleRepository:
    def __init__(self, session):
        self.session = session

    def findActiveByTargetUserIdAndRoleId(self, targetUserId: int, roleId: int):
        return (
            self.session.query(BoosterCustomRole)
            .filter(
                BoosterCustomRole.target_user_id == targetUserId,
                BoosterCustomRole.role_id == roleId,
                BoosterCustomRole.status == BoosterCustomRoleStatus.ACTIVE.value,
            )
            .first()
        )

    def createActive(self, grantedByUserId: int, targetUserId: int, roleId: int):
        boosterCustomRole = BoosterCustomRole(
            granted_by_user_id=grantedByUserId,
            target_user_id=targetUserId,
            role_id=roleId,
            status=BoosterCustomRoleStatus.ACTIVE.value,
        )

        self.session.add(boosterCustomRole)
        self.session.flush()

        return boosterCustomRole
