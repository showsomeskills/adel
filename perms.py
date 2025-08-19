# perms.py

from discord.ext import commands
from roles_config import ROLE_PERMISSIONS

def has_role_permission(command_name):
    async def predicate(ctx):
        allowed_roles = ROLE_PERMISSIONS.get(command_name, [])
        if not allowed_roles:
            return ctx.author.guild_permissions.administrator
        if ctx.author.guild_permissions.administrator:
            return True
        user_role_ids = [role.id for role in ctx.author.roles]
        return any(role_id in allowed_roles for role_id in user_role_ids)
    return commands.check(predicate)
