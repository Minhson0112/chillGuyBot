import discord
from discord import app_commands

from bot.config.config import MOD_ADMIN_USER_IDS, MOD_ROLE_IDS
from bot.enums.moderationActionType import ModerationActionType


def hasModerationPermission(actionType: ModerationActionType):
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise app_commands.CheckFailure("Lệnh này chỉ dùng được trong server.")

        member = interaction.user
        if not isinstance(member, discord.Member):
            raise app_commands.CheckFailure("Không xác định được member trong server.")

        memberRoleIds = {role.id for role in member.roles}

        staffRoleId = MOD_ROLE_IDS["staff"]
        modRoleId = MOD_ROLE_IDS["mod"]
        adminRoleId = MOD_ROLE_IDS["admin"]
        ownerRoleId = MOD_ROLE_IDS["owner"]

        if actionType == ModerationActionType.MUTE:
            allowedRoleIds = {staffRoleId, modRoleId, adminRoleId, ownerRoleId}
        elif actionType == ModerationActionType.UNMUTE:
            allowedRoleIds = {staffRoleId, modRoleId, adminRoleId, ownerRoleId}
        elif actionType == ModerationActionType.KICK:
            allowedRoleIds = {modRoleId, adminRoleId, ownerRoleId}
        elif actionType == ModerationActionType.BAN:
            allowedRoleIds = {adminRoleId, ownerRoleId}
        elif actionType == ModerationActionType.PN:
            allowedRoleIds = {adminRoleId, ownerRoleId}
        elif actionType == ModerationActionType.DELMSG:
            allowedRoleIds = {staffRoleId, modRoleId, adminRoleId, ownerRoleId}
        else:
            raise app_commands.CheckFailure("Loại quyền moderation không hợp lệ.")

        if memberRoleIds.isdisjoint(allowedRoleIds):
            raise app_commands.CheckFailure("Bạn không có quyền sử dụng lệnh này.")

        return True

    return app_commands.check(predicate)