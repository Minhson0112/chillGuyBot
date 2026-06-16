import discord


class BannerView(discord.ui.View):
    def __init__(self, member: discord.Member, globalBanner: discord.Asset | None):
        super().__init__(timeout=180)
        self.member = member
        self.globalBanner = globalBanner

    def buildBannerEmbed(self, bannerType: str):
        if bannerType == "global":
            banner = self.globalBanner
            title = f"Global banner của {self.member.display_name}"
            emptyMessage = f"{self.member.display_name} không có global banner."
        else:
            banner = self.member.guild_banner
            title = f"Server banner của {self.member.display_name}"
            emptyMessage = f"{self.member.display_name} không có server banner."

        embed = discord.Embed(title=title)

        if banner is None:
            embed.description = emptyMessage
            return embed

        embed.set_image(url=banner.url)

        return embed

    @discord.ui.button(label="Server", style=discord.ButtonStyle.primary)
    async def serverBannerButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.edit_message(
            embed=self.buildBannerEmbed("server"),
            view=self,
        )

    @discord.ui.button(label="Global", style=discord.ButtonStyle.secondary)
    async def globalBannerButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.edit_message(
            embed=self.buildBannerEmbed("global"),
            view=self,
        )
