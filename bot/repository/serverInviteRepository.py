from sqlalchemy import func

from bot.models.serverInvite import ServerInvite


class ServerInviteRepository:
    def __init__(self, session):
        self.session = session

    def findByInviteCode(self, inviteCode: str):
        return (
            self.session.query(ServerInvite)
            .filter(ServerInvite.invite_code == inviteCode)
            .first()
        )

    def create(self, inviteData: dict):
        serverInvite = ServerInvite(**inviteData)

        self.session.add(serverInvite)
        self.session.flush()

        return serverInvite

    def updateIfChanged(self, serverInvite: ServerInvite, inviteData: dict):
        isChanged = False

        for key, value in inviteData.items():
            if key == "last_fetched_at":
                continue

            if getattr(serverInvite, key) != value:
                setattr(serverInvite, key, value)
                isChanged = True

        serverInvite.last_fetched_at = inviteData["last_fetched_at"]
        self.session.flush()

        return isChanged

    def upsertByInviteCode(self, inviteCode: str, inviteData: dict):
        serverInvite = self.findByInviteCode(inviteCode)

        if serverInvite is None:
            return self.create(inviteData), True, False

        isUpdated = self.updateIfChanged(serverInvite, inviteData)

        return serverInvite, False, isUpdated

    def findTopInviters(self, limit: int = 10):
        totalUses = func.sum(ServerInvite.uses).label("totalUses")
        inviteCount = func.count(ServerInvite.id).label("inviteCount")

        return (
            self.session.query(
                ServerInvite.inviter_user_id.label("inviterUserId"),
                totalUses,
                inviteCount,
            )
            .filter(ServerInvite.inviter_user_id.isnot(None))
            .group_by(ServerInvite.inviter_user_id)
            .having(func.sum(ServerInvite.uses) > 0)
            .order_by(totalUses.desc(), ServerInvite.inviter_user_id.asc())
            .limit(limit)
            .all()
        )
