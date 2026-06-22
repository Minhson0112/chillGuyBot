import discord

class AvatarView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=180)
        self.member = member

    def buildAvatarEmbed(self, avatarType: str):
        if avatarType == "global":
            avatar = self.member.avatar or self.member.default_avatar
            title = f"Global avatar của {self.member.display_name}"
        else:
            avatar = self.member.guild_avatar or self.member.display_avatar
            title = f"Server avatar của {self.member.display_name}"

        embed = discord.Embed(title=title)
        embed.set_image(url=avatar.url)

        return embed

    @discord.ui.button(label="Server", style=discord.ButtonStyle.primary)
    async def serverAvatarButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.edit_message(
            embed=self.buildAvatarEmbed("server"),
            view=self,
        )

    @discord.ui.button(label="Global", style=discord.ButtonStyle.secondary)
    async def globalAvatarButton(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.edit_message(
            embed=self.buildAvatarEmbed("global"),
            view=self,
        )
