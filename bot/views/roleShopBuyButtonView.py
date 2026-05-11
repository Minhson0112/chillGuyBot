import discord

from bot.services.roleShop.roleShopPurchaseService import RoleShopPurchaseService


ROLE_SHOP_BUY_BUTTON_CUSTOM_ID = "<a:CS_kimcuong:1460648386628944106>"
ROLE_SHOP_SELECT_CUSTOM_ID = "<a:CS_TYM1:1463045403665633364>"
ROLE_SHOP_PAYMENT_CHANNEL_URL = "https://discord.com/channels/1356994231918530690/1502964209619697765"


class RoleShopBuyButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Mua role",
        style=discord.ButtonStyle.primary,
        emoji="<a:CS_kimcuong:1460648386628944106>",
        custom_id=ROLE_SHOP_BUY_BUTTON_CUSTOM_ID,
    )
    async def buyRoleButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh mua role chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        roleShopPurchaseService = RoleShopPurchaseService()
        roleShops = roleShopPurchaseService.findActiveRoleShops()

        options = []

        for roleShop in roleShops:
            role = interaction.guild.get_role(roleShop["roleId"])

            if role is None:
                continue

            options.append(
                discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id),
                    description=self.buildPriceDescription(roleShop),
                )
            )

        if len(options) == 0:
            await interaction.response.send_message(
                "Hiện tại chưa có role nào đang được bán.",
                ephemeral=True,
            )
            return

        options = options[:25]

        await interaction.response.send_message(
            "Vui lòng chọn role bạn muốn mua.",
            view=RoleShopSelectView(options),
            ephemeral=True,
        )

    def buildPriceDescription(self, roleShop: dict):
        prices = []

        if roleShop["priceCowoncy"] is not None and roleShop["priceCowoncy"] > 0:
            prices.append(f"{roleShop['priceCowoncy']:,} owo")

        if roleShop["priceChillCoin"] is not None and roleShop["priceChillCoin"] > 0:
            prices.append(f"{roleShop['priceChillCoin']:,} chill coin")

        return " hoặc ".join(prices)[:100]


class RoleShopSelectView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(timeout=180)
        self.add_item(RoleShopSelect(options))


class RoleShopSelect(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            custom_id=ROLE_SHOP_SELECT_CUSTOM_ID,
            placeholder="Chọn role muốn mua",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh mua role chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        roleId = int(self.values[0])
        role = interaction.guild.get_role(roleId)

        if role is None:
            await interaction.response.send_message(
                "Role này không còn tồn tại trong server.",
                ephemeral=True,
            )
            return

        roleShopPurchaseService = RoleShopPurchaseService()
        result = roleShopPurchaseService.createPendingPurchase(
            userId=interaction.user.id,
            roleId=roleId,
        )

        if not result["success"]:
            pendingRoleId = result.get("pendingRoleId")

            if pendingRoleId is not None:
                pendingRole = interaction.guild.get_role(pendingRoleId)

                if pendingRole is not None:
                    await interaction.response.send_message(
                        f"{result['message']}\n"
                        f"Role đang chờ thanh toán: {pendingRole.mention}",
                        ephemeral=True,
                    )
                    return

            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        priceText = self.buildPaymentText(result)

        await interaction.response.send_message(
            f"Bạn đã đăng kí mua role {role.mention} thành công.\n"
            f"Để hoàn tất giao dịch, bạn hãy chuyển phí giao dịch cho chúng tôi ở kênh:\n"
            f"{ROLE_SHOP_PAYMENT_CHANNEL_URL}\n\n"
            f"Số tiền cần chuyển: {priceText}\n\n"
            f"Để hủy giao dịch hãy dùng lệnh `cg cancelbuyrole`",
            ephemeral=True,
        )

    def buildPaymentText(self, result: dict):
        prices = []

        if result["priceCowoncy"] is not None and result["priceCowoncy"] > 0:
            prices.append(f"**{result['priceCowoncy']:,}** <:OwO:1503021935724859473> owo")

        if result["priceChillCoin"] is not None and result["priceChillCoin"] > 0:
            prices.append(f"**{result['priceChillCoin']:,}** <:cs_coin:1495116560191324383> chill coin")

        return " hoặc ".join(prices)