from datetime import datetime, time, timedelta, timezone

import discord

from bot.cache.coupleCache import activeCoupleIdByUserPair
from bot.config.database import getDbSession
from bot.repository.coupleDailyVoiceActivityRepository import CoupleDailyVoiceActivityRepository
from bot.repository.coupleRepository import CoupleRepository


class CoupleVoiceActivityService:
    INTIMACY_POINTS_PER_HOUR = 10
    SECONDS_PER_INTIMACY_REWARD = 3600

    def __init__(self):
        self.gmt7 = timezone(timedelta(hours=7))

    def refreshActiveCoupleCache(self):
        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            activeCouples = coupleRepository.findActiveCouples()

            activeCoupleIdByUserPair.clear()

            for couple in activeCouples:
                activeCoupleIdByUserPair[self.buildUserPairKey(
                    couple.user_1_id,
                    couple.user_2_id,
                )] = couple.id

    def collectSameVoiceCoupleIds(self, guilds):
        memberChannelByUserId = self.collectMemberChannelByUserId(guilds)
        sameVoiceCoupleIds = []

        for userPair, coupleId in activeCoupleIdByUserPair.items():
            user1Id, user2Id = userPair
            user1ChannelId = memberChannelByUserId.get(user1Id)
            user2ChannelId = memberChannelByUserId.get(user2Id)

            if user1ChannelId is None or user2ChannelId is None:
                continue

            if user1ChannelId == user2ChannelId:
                sameVoiceCoupleIds.append(coupleId)

        return sameVoiceCoupleIds

    def collectMemberChannelByUserId(self, guilds):
        memberChannelByUserId = {}

        for guild in guilds:
            for voiceChannel in guild.voice_channels:
                if not isinstance(voiceChannel, discord.VoiceChannel):
                    continue

                for member in voiceChannel.members:
                    if member.bot:
                        continue

                    memberChannelByUserId[member.id] = voiceChannel.id

        return memberChannelByUserId

    def addVoiceSecondsToCouples(
        self,
        coupleIds,
        startedAt,
        endedAt,
    ):
        if not coupleIds:
            return

        if endedAt <= startedAt:
            return

        with getDbSession() as session:
            coupleDailyVoiceActivityRepository = CoupleDailyVoiceActivityRepository(session)
            coupleRepository = CoupleRepository(session)

            for coupleId in coupleIds:
                self.addVoiceSecondsToCouple(
                    coupleId=coupleId,
                    startedAt=startedAt,
                    endedAt=endedAt,
                    coupleDailyVoiceActivityRepository=coupleDailyVoiceActivityRepository,
                    coupleRepository=coupleRepository,
                )

            session.commit()

    def addVoiceSecondsToCouple(
        self,
        coupleId: int,
        startedAt,
        endedAt,
        coupleDailyVoiceActivityRepository: CoupleDailyVoiceActivityRepository,
        coupleRepository: CoupleRepository,
    ):
        currentStart = startedAt

        while currentStart.date() < endedAt.date():
            nextDay = datetime.combine(
                currentStart.date() + timedelta(days=1),
                time.min,
                tzinfo=self.gmt7,
            )

            self.incrementCoupleDailyVoice(
                coupleId=coupleId,
                activityDate=currentStart.date(),
                voiceSeconds=int((nextDay - currentStart).total_seconds()),
                coupleDailyVoiceActivityRepository=coupleDailyVoiceActivityRepository,
                coupleRepository=coupleRepository,
            )
            currentStart = nextDay

        self.incrementCoupleDailyVoice(
            coupleId=coupleId,
            activityDate=currentStart.date(),
            voiceSeconds=int((endedAt - currentStart).total_seconds()),
            coupleDailyVoiceActivityRepository=coupleDailyVoiceActivityRepository,
            coupleRepository=coupleRepository,
        )

    def incrementCoupleDailyVoice(
        self,
        coupleId: int,
        activityDate,
        voiceSeconds: int,
        coupleDailyVoiceActivityRepository: CoupleDailyVoiceActivityRepository,
        coupleRepository: CoupleRepository,
    ):
        if voiceSeconds <= 0:
            return

        activity, previousVoiceSeconds = coupleDailyVoiceActivityRepository.incrementVoiceSeconds(
            coupleId=coupleId,
            activityDate=activityDate,
            voiceSecondsIncrement=voiceSeconds,
        )
        earnedPoints = self.calculateEarnedIntimacyPoints(
            previousVoiceSeconds=previousVoiceSeconds,
            currentVoiceSeconds=activity.voice_seconds,
        )

        if earnedPoints <= 0:
            return

        couple = coupleRepository.findById(coupleId)

        if couple is not None:
            coupleRepository.addIntimacyPoints(couple, earnedPoints)

    def calculateEarnedIntimacyPoints(
        self,
        previousVoiceSeconds: int,
        currentVoiceSeconds: int,
    ):
        previousRewardCount = previousVoiceSeconds // self.SECONDS_PER_INTIMACY_REWARD
        currentRewardCount = currentVoiceSeconds // self.SECONDS_PER_INTIMACY_REWARD
        rewardDiff = currentRewardCount - previousRewardCount

        return rewardDiff * self.INTIMACY_POINTS_PER_HOUR

    def buildUserPairKey(self, user1Id: int, user2Id: int):
        if user1Id < user2Id:
            return user1Id, user2Id

        return user2Id, user1Id
