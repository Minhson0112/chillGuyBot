import discord

from bot.config.config import DONATE_REWARD_ROLES
from bot.config.database import getDbSession
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository


class DonateRewardService:
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

        return await self.updateDonateRewardRole(guild, senderMember)