from datetime import datetime, timedelta, timezone

import discord


class MonthlyDonatorRoleService:
    GMT7 = timezone(timedelta(hours=7))

    def buildCurrentMonthRoleName(self):
        nowGmt7 = datetime.now(self.GMT7)
        return f"{nowGmt7.year}_{nowGmt7.month:02d}_donator"

    def buildPreviousMonthRoleName(self):
        nowGmt7 = datetime.now(self.GMT7)
        targetYear = nowGmt7.year
        targetMonth = nowGmt7.month - 1

        if nowGmt7.month == 1:
            targetYear = nowGmt7.year - 1
            targetMonth = 12

        return f"{targetYear}_{targetMonth:02d}_donator"

    async def findOrCreateCurrentMonthRole(self, guild: discord.Guild):
        roleName = self.buildCurrentMonthRoleName()
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

    async def assignCurrentMonthRole(self, guild: discord.Guild, member: discord.Member):
        currentMonthDonatorRole = await self.findOrCreateCurrentMonthRole(guild)

        if currentMonthDonatorRole not in member.roles:
            await member.add_roles(
                currentMonthDonatorRole,
                reason="Monthly donator reward",
            )

        return currentMonthDonatorRole

    async def deletePreviousMonthRole(self, guild: discord.Guild):
        roleName = self.buildPreviousMonthRoleName()
        role = discord.utils.get(guild.roles, name=roleName)

        if role is None:
            return False

        await role.delete(reason="Cleanup previous month donator role")
        return True
