from datetime import datetime, timedelta, timezone

import discord

from bot.config.roles import DONATE_REWARD_ROLES
from bot.config.database import getDbSession
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository
from bot.services.donate.monthlyDonatorRoleService import MonthlyDonatorRoleService


class DonateRewardService:
    GMT7 = timezone(timedelta(hours=7))
    MINIMUM_MONTHLY_DONATE_FOR_MONTH_ROLE = 100_000

    def __init__(self):
        self.monthlyDonatorRoleService = MonthlyDonatorRoleService()

    def getHighestMatchedRewardRole(self, totalDonate):
        highestMatchedRewardRole = None

        for donateRewardRole in DONATE_REWARD_ROLES:
            if totalDonate >= donateRewardRole["minimumTotalDonate"]:
                highestMatchedRewardRole = donateRewardRole

        return highestMatchedRewardRole

    def getAllDonateRewardRoleIds(self):
        return [donateRewardRole["roleId"] for donateRewardRole in DONATE_REWARD_ROLES]

    def createDonateHistory(self, senderUserId, receiverUserId, cowoncyAmount):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)

            donateHistory = owoDonateHistoryRepository.create({
                "sender_user_id": senderUserId,
                "receiver_user_id": receiverUserId,
                "cowoncy_amount": cowoncyAmount,
            })

            session.commit()
            return donateHistory

    def getTotalDonateBySenderUserId(self, senderUserId):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTotalDonateBySenderUserId(senderUserId)

    def getCurrentMonthDonateBySenderUserId(self, senderUserId):
        nowGmt7 = datetime.now(self.GMT7)

        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTotalDonateBySenderUserIdAndMonth(
                senderUserId=senderUserId,
                year=nowGmt7.year,
                month=nowGmt7.month,
            )

    async def updateCurrentMonthDonatorRole(self, guild: discord.Guild, member: discord.Member):
        currentMonthDonate = self.getCurrentMonthDonateBySenderUserId(member.id)

        if currentMonthDonate >= self.MINIMUM_MONTHLY_DONATE_FOR_MONTH_ROLE:
            return await self.monthlyDonatorRoleService.assignCurrentMonthRole(guild, member)

        return None

    async def updateDonateRewardRole(self, guild: discord.Guild, member: discord.Member):
        totalDonate = self.getTotalDonateBySenderUserId(member.id)
        highestMatchedRewardRole = self.getHighestMatchedRewardRole(totalDonate)
        donateRewardRoleIds = self.getAllDonateRewardRoleIds()

        rolesToRemove = []
        roleToAdd = None

        for roleId in donateRewardRoleIds:
            role = guild.get_role(roleId)
            if role is None:
                continue

            if highestMatchedRewardRole is not None and role.id == highestMatchedRewardRole["roleId"]:
                roleToAdd = role
                continue

            if role in member.roles:
                rolesToRemove.append(role)

        if rolesToRemove:
            await member.remove_roles(*rolesToRemove)

        if roleToAdd is not None and roleToAdd not in member.roles:
            await member.add_roles(roleToAdd)

        return {
            "totalDonate": totalDonate,
            "rewardRole": roleToAdd,
        }

    async def processDonateReward(self, guild: discord.Guild, senderMember: discord.Member, receiverMember: discord.Member, cowoncyAmount: int):
        self.createDonateHistory(
            senderUserId=senderMember.id,
            receiverUserId=receiverMember.id,
            cowoncyAmount=cowoncyAmount,
        )

        donateRewardResult = await self.updateDonateRewardRole(guild, senderMember)
        await self.updateCurrentMonthDonatorRole(guild, senderMember)

        return donateRewardResult
