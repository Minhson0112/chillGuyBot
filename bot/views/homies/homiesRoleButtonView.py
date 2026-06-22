import discord

from bot.config.roles import HOMIES_ROLE_ID


CHILL_STATION_GUILD_ID = 1356994231918530690
HOMIES_ROLE_BUTTON_CUSTOM_ID = "homies_role_button"


class HomiesRoleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Nhận role Homies",
        style=discord.ButtonStyle.primary,
        custom_id=HOMIES_ROLE_BUTTON_CUSTOM_ID,
    )
    async def receiveHomiesRoleButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        member = interaction.user

        if not isinstance(member, discord.Member):
            await interaction.followup.send(
                "Không thể xác định thông tin member của bạn.",
                ephemeral=True,
            )
            return

        hasChillStationTag = await self.hasChillStationTag(interaction)

        if not hasChillStationTag:
            await interaction.followup.send(
                "Bạn cần để tag server của Chill Station trên profile để nhận role Homies.",
                ephemeral=True,
            )
            return

        role = interaction.guild.get_role(HOMIES_ROLE_ID)

        if role is None:
            await interaction.followup.send(
                "Không tìm thấy role Homies trong server. Vui lòng liên hệ quản trị viên.",
                ephemeral=True,
            )
            return

        if role in member.roles:
            await interaction.followup.send(
                "Bạn đã có role Homies rồi.",
                ephemeral=True,
            )
            return

        try:
            await member.add_roles(
                role,
                reason="User has Chill Station guild tag",
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "Bot không có quyền cấp role Homies. Vui lòng kiểm tra lại vị trí role của bot.",
                ephemeral=True,
            )
            return
        except discord.HTTPException:
            await interaction.followup.send(
                "Đã xảy ra lỗi khi cấp role Homies. Vui lòng thử lại sau.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            embed=self.buildReceivedHomiesRoleEmbed(role),
            allowed_mentions=discord.AllowedMentions.none(),
            ephemeral=True,
        )

    async def hasChillStationTag(self, interaction: discord.Interaction):
        primaryGuild = await self.resolvePrimaryGuild(interaction)

        if primaryGuild is None:
            return False

        identityGuildId = self.getPrimaryGuildId(primaryGuild)

        if identityGuildId is None:
            return False

        return identityGuildId == CHILL_STATION_GUILD_ID

    async def resolvePrimaryGuild(self, interaction: discord.Interaction):
        try:
            user = await interaction.client.fetch_user(interaction.user.id)
            primaryGuild = getattr(user, "primary_guild", None)

            if primaryGuild is not None:
                return primaryGuild
        except discord.HTTPException:
            pass

        return getattr(interaction.user, "primary_guild", None)

    def getPrimaryGuildId(self, primaryGuild):
        identityGuildId = self.getPrimaryGuildValue(
            primaryGuild=primaryGuild,
            keyList=[
                "identity_guild_id",
                "guild_id",
                "id",
            ],
        )

        if identityGuildId is None:
            return None

        try:
            return int(identityGuildId)
        except (TypeError, ValueError):
            return None

    def getPrimaryGuildValue(
        self,
        primaryGuild,
        keyList: list[str],
    ):
        if isinstance(primaryGuild, dict):
            for key in keyList:
                value = primaryGuild.get(key)

                if value is not None:
                    return value

            return None

        for key in keyList:
            value = getattr(primaryGuild, key, None)

            if value is not None:
                return value

        return None

    def buildReceivedHomiesRoleEmbed(self, role: discord.Role):
        embed = discord.Embed(
            title="Bạn đã nhận được role  ⋆｡‧˚ʚ 𝐡𝐨𝐦𝐢𝐞𝐬 ɞ˚‧｡⋆",
            description=(
                f"Role: {role.mention}\n\n"
                "Nếu bỏ tag server Chill Station khỏi profile, bạn sẽ mất role sau 1 ngày."
            ),
            color=discord.Color.green(),
        )

        return embed