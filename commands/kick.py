import discord
from discord.ext import commands
from perms import has_role_permission

@commands.command(name='kick')
@has_role_permission('kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, user_arg=None, *, reason=None):
    if not user_arg:
        await ctx.send("Usage: .kick <user> [reason]", delete_after=5)
        return

    guild = ctx.guild

    def find_member(search):
        member = None
        # Mention
        if search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = guild.get_member(user_id)
            except:
                pass
        # ID
        elif search.isdigit():
            member = guild.get_member(int(search))
        return member  # No fuzzy matching

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=3)
        return

    if member == guild.owner:
        await ctx.send("Cannot kick the server owner.", delete_after=3)
        return

    if member.top_role >= guild.me.top_role:
        await ctx.send("I cannot kick a user with an equal or higher role than mine.", delete_after=3)
        return

    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked **{member.display_name}**. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick this user.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to kick user. Error: **{e}**", delete_after=3)


def setup(bot):
    bot.add_command(kick)
