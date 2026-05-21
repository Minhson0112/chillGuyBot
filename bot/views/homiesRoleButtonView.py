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

        primaryGuild = await self.resolvePrimaryGuild(interaction)

        if primaryGuild is None:
            await interaction.followup.send(
                "Bạn cần để tag server của Chill Station trên profile để nhận role Homies error1.",
                ephemeral=True,
            )
            return

        identityGuildId = getattr(primaryGuild, "identity_guild_id", None)
        identityEnabled = getattr(primaryGuild, "identity_enabled", None)

        if identityGuildId != CHILL_STATION_GUILD_ID or identityEnabled is not True:
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

    async def resolvePrimaryGuild(self, interaction: discord.Interaction):
        primaryGuild = getattr(interaction.user, "primary_guild", None)

        if primaryGuild is not None:
            return primaryGuild

        try:
            user = await interaction.client.fetch_user(interaction.user.id)
        except discord.HTTPException:
            return None

        return getattr(user, "primary_guild", None)

    def buildReceivedHomiesRoleEmbed(self, role: discord.Role):
        embed = discord.Embed(
            title="Bạn đã nhận được role Homies",
            description=(
                f"Role: {role.mention}\n\n"
                "Nếu bỏ tag server Chill Station khỏi profile, bạn sẽ mất role sau 1 ngày."
            ),
            color=discord.Color.green(),
        )

        return embed