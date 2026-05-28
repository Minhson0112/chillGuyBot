import discord

from bot.config.database import getDbSession
from bot.config.decoration import FOOTER_DECORATION_IMG_URL
from bot.config.emoji import CHILL_COIN, COWONCCY, JOIN_BUTTON, VND, WING_L, WING_R
from bot.enums.giveawayStatus import GiveawayStatus
from bot.enums.giveawayType import GiveawayType
from bot.repository.giveawayParticipantRepository import GiveawayParticipantRepository
from bot.repository.giveawayRepository import GiveawayRepository
from bot.services.discordTimestampService import discordTimestampService


class GiveawayMessageService:
    REWARD_UNIT_CHILL_COIN = "chill coin"
    REWARD_UNIT_COWONCY = "cowoncy"
    REWARD_UNIT_VND = "VND"

    def buildGiveawayEmbed(
        self,
        giveaway,
        guild: discord.Guild,
        participantCount: int,
    ):
        guildIconUrl = self.resolveGuildIconUrl(guild)
        embed = discord.Embed(
            title=f"{WING_L} {giveaway.title} {WING_R}",
            description=(
                f"- Tổ chức bởi: <@{giveaway.created_by_user_id}>\n"
                f"- Phần thưởng: {self.buildRewardText(giveaway)}\n"
                f"- quay thưởng⏰: {discordTimestampService.formatShortDateTime(giveaway.draw_at)}\n"
                f"- số người tham gia: **{participantCount}**"
            ),
            color=discord.Color.gold(),
        )

        if guildIconUrl is None:
            embed.set_author(name="Chill Station Giveaway")
        else:
            embed.set_author(
                name="Chill Station Giveaway",
                icon_url=guildIconUrl,
            )
            embed.set_thumbnail(url=guildIconUrl)

        embed.set_image(url=FOOTER_DECORATION_IMG_URL)
        embed.set_footer(text=f"Chill Station | {giveaway.winner_count} người thắng")

        return embed

    def buildRewardText(self, giveaway):
        rewardEmoji = self.resolveRewardEmoji(giveaway.type)
        rewardUnit = self.resolveRewardUnit(giveaway.type)
        rewardAmount = self.resolveRewardAmount(giveaway)

        if giveaway.type == GiveawayType.CUSTOM.value:
            return giveaway.reward_text or "Custom"

        return f"{rewardEmoji} **{self.formatNumber(rewardAmount)}** {rewardUnit}"

    def resolveRewardEmoji(self, giveawayType: str):
        if giveawayType == GiveawayType.CHILL_COIN.value:
            return CHILL_COIN

        if giveawayType == GiveawayType.COWONCY.value:
            return COWONCCY

        if giveawayType == GiveawayType.VND.value:
            return VND

        return ""

    def resolveRewardUnit(self, giveawayType: str):
        if giveawayType == GiveawayType.CHILL_COIN.value:
            return self.REWARD_UNIT_CHILL_COIN

        if giveawayType == GiveawayType.COWONCY.value:
            return self.REWARD_UNIT_COWONCY

        if giveawayType == GiveawayType.VND.value:
            return self.REWARD_UNIT_VND

        return ""

    def resolveRewardAmount(self, giveaway):
        if giveaway.type == GiveawayType.CHILL_COIN.value:
            return giveaway.reward_chill_coin

        if giveaway.type == GiveawayType.COWONCY.value:
            return giveaway.reward_cowoncy

        if giveaway.type == GiveawayType.VND.value:
            return giveaway.reward_vnd

        return None

    def resolveGuildIconUrl(self, guild: discord.Guild):
        if guild.icon is None:
            return None

        return guild.icon.url

    def formatNumber(self, number: int | None):
        if number is None:
            return "0"

        return f"{number:,}"

    def buildGiveawayEmbedById(self, giveawayId: int, guild: discord.Guild):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)

            if giveaway is None:
                return None

            participantCount = participantRepository.countActiveParticipants(giveawayId)

            return self.buildGiveawayEmbed(
                giveaway=giveaway,
                guild=guild,
                participantCount=participantCount,
            )

    def joinGiveaway(self, giveawayId: int, userId: int):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)

            if giveaway is None:
                return {
                    "success": False,
                    "message": "Giveaway không tồn tại.",
                }

            if giveaway.status != GiveawayStatus.ACTIVE.value:
                return {
                    "success": False,
                    "message": "Giveaway này không còn hoạt động.",
                }

            existingParticipant = participantRepository.findByGiveawayIdAndUserId(
                giveawayId=giveawayId,
                userId=userId,
            )

            if existingParticipant is not None:
                return {
                    "success": True,
                    "alreadyJoined": True,
                    "message": "Bạn đã tham gia giveaway này rồi.",
                }

            participantRepository.create(
                giveawayId=giveawayId,
                userId=userId,
            )
            participantCount = participantRepository.countActiveParticipants(giveawayId)
            session.commit()

            return {
                "success": True,
                "alreadyJoined": False,
                "message": "Bạn đã tham gia giveaway thành công.",
                "participantCount": participantCount,
            }

    def findActiveParticipants(self, giveawayId: int):
        with getDbSession() as session:
            participantRepository = GiveawayParticipantRepository(session)
            participants = participantRepository.findActiveParticipantsByGiveawayId(giveawayId)

            return [
                {
                    "userId": participant.user_id,
                    "joinedAt": participant.joined_at,
                }
                for participant in participants
            ]
