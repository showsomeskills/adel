import discord
from discord.ext import commands
from perms import has_role_permission

@commands.command(name='ban')
@has_role_permission('ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, user_arg=None, *, reason=None):
    if user_arg is None:
        await ctx.send("Please specify a user to ban. Usage: .ban <user> [reason]", delete_after=3)
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

    if member == ctx.author:
        await ctx.send("You cannot ban yourself.", delete_after=3)
        return

    if member == guild.owner:
        await ctx.send("I cannot ban the server owner.", delete_after=3)
        return

    if member.top_role >= guild.me.top_role:
        await ctx.send("I cannot ban this user because their highest role is equal or higher than mine.", delete_after=3)
        return

    try:
        # Attempt to DM user the ban reason before banning
        if reason:
            try:
                dm_message = f"You have been banned from **{guild.name}**"
                dm_message += f" for the following reason:\n{reason}"
                await member.send(dm_message)
            except discord.Forbidden:
                # User DM closed or blocked bot, silently continue
                pass

        await member.ban(reason=reason)

        if reason:
            await ctx.send(f"Banned **{member.display_name}** for reason: {reason}")
        else:
            await ctx.send(f"Banned **{member.display_name}**.")

    except discord.Forbidden:
        await ctx.send("I don't have permission to ban that user.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to ban user. Error: **{e}**", delete_after=3)


def setup(bot):
    bot.add_command(ban)
