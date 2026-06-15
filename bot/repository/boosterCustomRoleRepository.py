from bot.enums.boosterCustomRoleStatus import BoosterCustomRoleStatus
from bot.models.boosterCustomRole import BoosterCustomRole


class BoosterCustomRoleRepository:
    def __init__(self, session):
        self.session = session

    def findById(self, boosterCustomRoleId: int):
        return (
            self.session.query(BoosterCustomRole)
            .filter(BoosterCustomRole.id == boosterCustomRoleId)
            .first()
        )

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

    def findActiveByTargetUserId(self, targetUserId: int):
        return (
            self.session.query(BoosterCustomRole)
            .filter(
                BoosterCustomRole.target_user_id == targetUserId,
                BoosterCustomRole.status == BoosterCustomRoleStatus.ACTIVE.value,
            )
            .all()
        )

    def findActiveTargetUserIds(self):
        rows = (
            self.session.query(BoosterCustomRole.target_user_id)
            .filter(BoosterCustomRole.status == BoosterCustomRoleStatus.ACTIVE.value)
            .distinct()
            .all()
        )

        return [row[0] for row in rows]

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

    def markRemoved(self, boosterCustomRole, removedReason: str, removedAt):
        boosterCustomRole.status = BoosterCustomRoleStatus.REMOVED.value
        boosterCustomRole.removed_reason = removedReason
        boosterCustomRole.removed_at = removedAt

        self.session.flush()

        return boosterCustomRole
