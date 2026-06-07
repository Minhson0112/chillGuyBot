from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.enums.serverInviteStatus import ServerInviteStatus
from bot.repository.memberRepository import MemberRepository
from bot.repository.serverInviteRepository import ServerInviteRepository


class ServerInviteSyncService:
    def normalizeDatetime(self, value):
        if value is None:
            return None

        return value.replace(tzinfo=None)

    def buildExpiredAt(self, discordCreatedAt, maxAge: int):
        if discordCreatedAt is None:
            return None

        if maxAge <= 0:
            return None

        return discordCreatedAt + timedelta(seconds=maxAge)

    def resolveInviterUserId(self, memberRepository: MemberRepository, invite):
        inviter = getattr(invite, "inviter", None)

        if inviter is None:
            return None

        inviterUserId = inviter.id
        inviterMember = memberRepository.findByUserId(inviterUserId)

        if inviterMember is None:
            return None

        return inviterUserId

    def buildInviteData(self, memberRepository: MemberRepository, invite, fetchedAt):
        discordCreatedAt = self.normalizeDatetime(invite.created_at)
        maxAge = invite.max_age or 0

        return {
            "invite_code": invite.code,
            "invite_url": invite.url,
            "channel_id": invite.channel.id if getattr(invite, "channel", None) is not None else None,
            "inviter_user_id": self.resolveInviterUserId(memberRepository, invite),
            "uses": invite.uses or 0,
            "max_uses": invite.max_uses or 0,
            "max_age": maxAge,
            "temporary": invite.temporary,
            "status": ServerInviteStatus.ACTIVE.value,
            "discord_created_at": discordCreatedAt,
            "expired_at": self.buildExpiredAt(discordCreatedAt, maxAge),
            "deleted_at": None,
            "last_fetched_at": fetchedAt,
        }

    def buildDeletedInviteData(self, memberRepository: MemberRepository, invite, deletedAt):
        discordCreatedAt = self.normalizeDatetime(getattr(invite, "created_at", None))
        maxAge = getattr(invite, "max_age", None) or 0

        return {
            "invite_code": invite.code,
            "invite_url": invite.url,
            "channel_id": invite.channel.id if getattr(invite, "channel", None) is not None else None,
            "inviter_user_id": self.resolveInviterUserId(memberRepository, invite),
            "uses": getattr(invite, "uses", None) or 0,
            "max_uses": getattr(invite, "max_uses", None) or 0,
            "max_age": maxAge,
            "temporary": getattr(invite, "temporary", False),
            "status": ServerInviteStatus.DELETED.value,
            "discord_created_at": discordCreatedAt,
            "expired_at": self.buildExpiredAt(discordCreatedAt, maxAge),
            "deleted_at": deletedAt,
            "last_fetched_at": deletedAt,
        }

    def syncCreatedInvite(self, invite):
        fetchedAt = datetime.now()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            serverInviteRepository = ServerInviteRepository(session)
            inviteData = self.buildInviteData(
                memberRepository=memberRepository,
                invite=invite,
                fetchedAt=fetchedAt,
            )
            _, isCreated, isUpdated = serverInviteRepository.upsertByInviteCode(
                inviteCode=invite.code,
                inviteData=inviteData,
            )

            session.commit()

        return {
            "created": isCreated,
            "updated": isUpdated,
        }

    def markDeletedInvite(self, invite):
        deletedAt = datetime.now()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            serverInviteRepository = ServerInviteRepository(session)
            serverInvite = serverInviteRepository.findByInviteCode(invite.code)

            if serverInvite is None:
                inviteData = self.buildDeletedInviteData(
                    memberRepository=memberRepository,
                    invite=invite,
                    deletedAt=deletedAt,
                )
                serverInviteRepository.create(inviteData)
                session.commit()

                return {
                    "created": True,
                    "updated": False,
                }

            isUpdated = serverInviteRepository.markDeleted(serverInvite, deletedAt)
            session.commit()

        return {
            "created": False,
            "updated": isUpdated,
        }

    async def syncGuildInvites(self, guild):
        fetchedAt = datetime.now()
        createdCount = 0
        updatedCount = 0
        unchangedCount = 0

        invites = await guild.invites()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            serverInviteRepository = ServerInviteRepository(session)

            for invite in invites:
                inviteData = self.buildInviteData(
                    memberRepository=memberRepository,
                    invite=invite,
                    fetchedAt=fetchedAt,
                )
                _, isCreated, isUpdated = serverInviteRepository.upsertByInviteCode(
                    inviteCode=invite.code,
                    inviteData=inviteData,
                )

                if isCreated:
                    createdCount += 1
                elif isUpdated:
                    updatedCount += 1
                else:
                    unchangedCount += 1

            session.commit()

        return {
            "fetchedCount": len(invites),
            "createdCount": createdCount,
            "updatedCount": updatedCount,
            "unchangedCount": unchangedCount,
        }
