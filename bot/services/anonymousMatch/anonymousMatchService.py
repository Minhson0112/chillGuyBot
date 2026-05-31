from datetime import datetime

import discord

from bot.config.database import getDbSession
from bot.enums.anonymousMatchSessionStatus import AnonymousMatchSessionStatus
from bot.repository.anonymousMatchQueueRepository import AnonymousMatchQueueRepository
from bot.repository.anonymousMatchSessionRepository import AnonymousMatchSessionRepository
from bot.repository.memberRepository import MemberRepository
from bot.services.anonymousMatch.anonymousMatchCacheService import AnonymousMatchCacheService


class AnonymousMatchService:
    def __init__(self):
        self.anonymousMatchCacheService = AnonymousMatchCacheService()

    async def registerMatch(self, bot, user: discord.User):
        now = datetime.now()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            queueRepository = AnonymousMatchQueueRepository(session)
            sessionRepository = AnonymousMatchSessionRepository(session)

            member = memberRepository.findByUserId(user.id)
            if member is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có dữ liệu member trong Chill Station nên chưa thể dùng matching.",
                }

            activeSession = sessionRepository.findActiveByUserId(user.id)
            if activeSession is not None:
                return {
                    "success": False,
                    "message": "Bạn đang ở trong một phiên matching rồi. Dùng `cg stop` để kết thúc trước.",
                }

            waitingQueue = queueRepository.findWaitingByUserId(user.id)
            if waitingQueue is not None:
                return {
                    "success": True,
                    "matched": False,
                    "message": "Bạn đã ở trong hàng chờ matching rồi.",
                }

            currentQueue = queueRepository.create(user.id)
            matchedQueue = self.findMatchableQueue(
                queueRepository=queueRepository,
                sessionRepository=sessionRepository,
                userId=user.id,
            )

            if matchedQueue is None:
                session.commit()
                return {
                    "success": True,
                    "matched": False,
                    "message": "Đã đăng ký matching, tôi sẽ ghép đôi khi có người phù hợp.",
                }

            userAAlias = self.buildAlias(matchedQueue.id)
            userBAlias = self.buildAlias(currentQueue.id)
            anonymousMatchSession = sessionRepository.create({
                "user_a_id": matchedQueue.user_id,
                "user_b_id": currentQueue.user_id,
                "user_a_alias": userAAlias,
                "user_b_alias": userBAlias,
                "status": AnonymousMatchSessionStatus.ACTIVE.value,
            })

            queueRepository.markMatched(matchedQueue, now)
            queueRepository.markMatched(currentQueue, now)
            session.commit()
            self.anonymousMatchCacheService.setMatch(anonymousMatchSession)

            return {
                "success": True,
                "matched": True,
                "message": "Đã ghép đôi thành công.",
                "sessionId": anonymousMatchSession.id,
                "firstUserId": matchedQueue.user_id,
                "secondUserId": currentQueue.user_id,
                "firstAlias": userAAlias,
                "secondAlias": userBAlias,
            }

    def findMatchableQueue(self, queueRepository, sessionRepository, userId):
        waitingCandidates = queueRepository.findWaitingCandidates(userId)

        for candidate in waitingCandidates:
            candidateActiveSession = sessionRepository.findActiveByUserId(candidate.user_id)
            if candidateActiveSession is not None:
                continue

            if not self.isLatestMatchPair(
                sessionRepository=sessionRepository,
                firstUserId=userId,
                secondUserId=candidate.user_id,
            ):
                return candidate

        return None

    def isLatestMatchPair(self, sessionRepository, firstUserId, secondUserId):
        firstLatestSession = sessionRepository.findLatestByUserId(firstUserId)
        secondLatestSession = sessionRepository.findLatestByUserId(secondUserId)

        if firstLatestSession is None or secondLatestSession is None:
            return False

        return (
            firstLatestSession.id == secondLatestSession.id
            and self.isSessionPair(firstLatestSession, firstUserId, secondUserId)
        )

    def isSessionPair(self, anonymousMatchSession, firstUserId, secondUserId):
        return (
            anonymousMatchSession.user_a_id == firstUserId
            and anonymousMatchSession.user_b_id == secondUserId
        ) or (
            anonymousMatchSession.user_a_id == secondUserId
            and anonymousMatchSession.user_b_id == firstUserId
        )

    async def sendMatchedMessages(self, bot, matchResult):
        firstMessageSent = await self.sendMatchedMessage(
            bot=bot,
            userId=matchResult["firstUserId"],
            alias=matchResult["firstAlias"],
        )
        secondMessageSent = await self.sendMatchedMessage(
            bot=bot,
            userId=matchResult["secondUserId"],
            alias=matchResult["secondAlias"],
        )

        return firstMessageSent and secondMessageSent

    async def sendMatchedMessage(self, bot, userId, alias):
        try:
            user = bot.get_user(userId) or await bot.fetch_user(userId)
            await user.send(self.buildMatchedMessage(alias))
            return True
        except discord.HTTPException:
            return False

    def buildAlias(self, queueId):
        return f"use{queueId}"

    def buildMatchedMessage(self, alias):
        return (
            f"Đã gép đôi thành công, tên của bạn trong phiên này là {alias}, "
            "từ giờ mọi tin nhắn trực tiếp với tôi sẽ được chuyển tới đối tác của bạn. "
            "bạn cũng có thể kết thúc cuộc chò chuyện bằng cg stop"
        )
