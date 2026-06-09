import re

import discord

from bot.config.emoji import WELCOME
from bot.config.roles import ADMIN_ROLE_ID, MODERATOR_ROLE_ID, OWNER_ROLE_ID
from bot.enums.ticketType import TicketType
from bot.views.ticketCloseButtonView import TicketCloseButtonView


class TicketChannelService:
    TICKET_SUPPORT_ROLE_IDS = {
        TicketType.REPORT: [
            OWNER_ROLE_ID,
            MODERATOR_ROLE_ID,
            ADMIN_ROLE_ID,
        ],
        TicketType.GIVEAWAY_REWARD: [
            OWNER_ROLE_ID,
        ],
        TicketType.PARTNER: [
            OWNER_ROLE_ID,
            MODERATOR_ROLE_ID,
            ADMIN_ROLE_ID,
        ],
        TicketType.CREATE_GIVEAWAY: [
            OWNER_ROLE_ID,
            MODERATOR_ROLE_ID,
            ADMIN_ROLE_ID,
        ],
        TicketType.FARM_GAME_CHILL_COIN: [
            OWNER_ROLE_ID,
        ],
        TicketType.STAFF_APPLICATION: [
            OWNER_ROLE_ID,
        ],
        TicketType.OTHER: [
            OWNER_ROLE_ID,
            MODERATOR_ROLE_ID,
            ADMIN_ROLE_ID,
        ],
    }

    async def createTicketChannel(
        self,
        guild: discord.Guild,
        member: discord.Member,
        ticketType: TicketType,
    ):
        channelName = self.buildTicketChannelName(
            ticketType=ticketType,
            userName=member.name,
        )

        ticketChannel = await guild.create_text_channel(
            name=channelName,
            overwrites=self.buildPermissionOverwrites(
                guild=guild,
                member=member,
                ticketType=ticketType,
            ),
            reason=f"Create {ticketType.value} ticket for {member}",
        )

        await ticketChannel.send(
            content=f"@here {member.mention} cần giúp đỡ về vấn đề **{ticketType.label}**",
            embed=self.buildTicketControllerEmbed(),
            view=TicketCloseButtonView(),
            allowed_mentions=discord.AllowedMentions(
                everyone=True,
                users=True,
                roles=False,
            ),
        )

        return ticketChannel

    def buildTicketChannelName(
        self,
        ticketType: TicketType,
        userName: str,
    ):
        safeUserName = re.sub(r"[^a-zA-Z0-9_-]+", "_", userName).strip("_")

        if len(safeUserName) == 0:
            safeUserName = "user"

        channelName = f"{ticketType.value}_{safeUserName}_ticket"

        return channelName[:100]

    def buildPermissionOverwrites(
        self,
        guild: discord.Guild,
        member: discord.Member,
        ticketType: TicketType,
    ):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
            ),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
            ),
        }

        botMember = guild.me

        if botMember is not None:
            overwrites[botMember] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
            )

        for roleId in self.TICKET_SUPPORT_ROLE_IDS[ticketType]:
            role = guild.get_role(roleId)

            if role is None:
                continue

            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
            )

        return overwrites

    def buildTicketControllerEmbed(self):
        return discord.Embed(
            title="Chill Station Ticket Controller",
            description=f"{WELCOME} hãy đợi một xíu nhé, sẽ mất một lúc cho đến khi có ai đó trả lời.",
            color=discord.Color.blue(),
        )
