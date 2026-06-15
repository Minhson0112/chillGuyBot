from datetime import datetime, timedelta, timezone

import discord

from bot.config.roles import DONATE_REWARD_ROLES
from bot.config.database import getDbSession
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class DonateRewardService:
    GMT7 = timezone(timedelta(hours=7))

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

    def buildCurrentMonthDonatorRoleName(self):
        nowGmt7 = datetime.now(self.GMT7)
        return f"{nowGmt7.year}_{nowGmt7.month:02d}_donator"

    async def findOrCreateCurrentMonthDonatorRole(self, guild: discord.Guild):
        roleName = self.buildCurrentMonthDonatorRoleName()
        role = discord.utils.get(guild.roles, name=roleName)

        if role is not None:
            return role

        return await guild.create_role(
            name=roleName,
            permissions=discord.Permissions.none(),
            color=discord.Color.default(),
            hoist=False,
            mentionable=False,
            reason="Create monthly donator role",
        )

    async def updateCurrentMonthDonatorRole(self, guild: discord.Guild, member: discord.Member):
        currentMonthDonatorRole = await self.findOrCreateCurrentMonthDonatorRole(guild)

        if currentMonthDonatorRole not in member.roles:
            await member.add_roles(
                currentMonthDonatorRole,
                reason="Monthly donator reward",
            )

        return currentMonthDonatorRole

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
