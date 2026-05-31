from datetime import datetime

import discord

from bot.config.database import getDbSession
from bot.repository.anonymousMatchSessionRepository import AnonymousMatchSessionRepository
from bot.services.anonymousMatch.anonymousMatchCacheService import AnonymousMatchCacheService


class AnonymousMatchStopService:
    def __init__(self):
        self.anonymousMatchCacheService = AnonymousMatchCacheService()

    async def stopMatch(self, bot, user: discord.User):
        with getDbSession() as session:
            sessionRepository = AnonymousMatchSessionRepository(session)
            anonymousMatchSession = sessionRepository.findActiveByUserId(user.id)

            if anonymousMatchSession is None:
                return {
                    "success": False,
                    "message": "Bạn không có phiên matching nào đang hoạt động.",
                }

            partnerUserId = self.getPartnerUserId(anonymousMatchSession, user.id)

            if self.hasUserRequestedEnd(anonymousMatchSession, user.id):
                return {
                    "success": True,
                    "ended": False,
                    "alreadyRequested": True,
                    "partnerUserId": partnerUserId,
                    "message": "Bạn đã yêu cầu kết thúc phiên này rồi. Đang chờ đối tác xác nhận bằng `cg stop`.",
                }

            sessionRepository.requestEnd(anonymousMatchSession, user.id)

            if anonymousMatchSession.end_requested_by_a and anonymousMatchSession.end_requested_by_b:
                sessionRepository.endSession(anonymousMatchSession, datetime.now())
                session.commit()
                self.anonymousMatchCacheService.removeByUserId(user.id)

                return {
                    "success": True,
                    "ended": True,
                    "alreadyRequested": False,
                    "partnerUserId": partnerUserId,
                    "message": "Phiên matching đã kết thúc. Bạn có thể dùng `cg match` để tìm người mới.",
                }

            session.commit()

            return {
                "success": True,
                "ended": False,
                "alreadyRequested": False,
                "partnerUserId": partnerUserId,
                "message": "Đã ghi nhận yêu cầu kết thúc. Phiên sẽ kết thúc khi đối tác cũng dùng `cg stop`.",
            }

    async def endMatchByMemberLeave(self, bot, userId):
        with getDbSession() as session:
            sessionRepository = AnonymousMatchSessionRepository(session)
            anonymousMatchSession = sessionRepository.findActiveByUserId(userId)

            if anonymousMatchSession is None:
                return False

            partnerUserId = self.getPartnerUserId(anonymousMatchSession, userId)

            if anonymousMatchSession.user_a_id == userId:
                anonymousMatchSession.end_requested_by_a = True

            if anonymousMatchSession.user_b_id == userId:
                anonymousMatchSession.end_requested_by_b = True

            sessionRepository.endSession(anonymousMatchSession, datetime.now())
            session.commit()

            self.anonymousMatchCacheService.removeByUserId(userId)

        await self.sendDm(
            bot=bot,
            userId=partnerUserId,
            message="Đối tác của bạn đã rời khỏi Chill Station nên phiên matching đã tự động kết thúc. Bạn có thể dùng `cg match` để tìm người mới.",
        )

        return True

    async def notifyPartnerStopRequested(self, bot, partnerUserId):
        await self.sendDm(
            bot=bot,
            userId=partnerUserId,
            message="Đối tác của bạn muốn kết thúc phiên matching. Nếu bạn cũng muốn kết thúc, hãy dùng `cg stop`.",
        )

    async def notifyPartnerEnded(self, bot, partnerUserId):
        await self.sendDm(
            bot=bot,
            userId=partnerUserId,
            message="Phiên matching đã kết thúc. Bạn có thể dùng `cg match` để tìm người mới.",
        )

    async def sendDm(self, bot, userId, message):
        try:
            user = bot.get_user(userId) or await bot.fetch_user(userId)
            await user.send(message)
            return True
        except discord.HTTPException:
            return False

    def getPartnerUserId(self, anonymousMatchSession, userId):
        if anonymousMatchSession.user_a_id == userId:
            return anonymousMatchSession.user_b_id

        return anonymousMatchSession.user_a_id

    def hasUserRequestedEnd(self, anonymousMatchSession, userId):
        if anonymousMatchSession.user_a_id == userId:
            return anonymousMatchSession.end_requested_by_a

        return anonymousMatchSession.end_requested_by_b
