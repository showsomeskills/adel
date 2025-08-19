import discord
from discord.ext import commands
import asyncio
import re
from perms import has_role_permission

@commands.command(name='mute')
@has_role_permission('mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, user_arg=None, time_arg=None):
    if not user_arg or not time_arg:
        await ctx.send("Usage: .mute <user> <duration> (like .mute @user 10m or .mute userid 2h)", delete_after=3)
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

    match = re.match(r"^(\d+)([mh])$", time_arg)
    if not match:
        await ctx.send("Please provide duration like **10m** or **1h** (m=minutes, h=hours).", delete_after=3)
        return

    count = int(match.group(1))
    unit = match.group(2)
    seconds = count * 60 if unit == "m" else count * 60 * 60

    muted_role = discord.utils.get(guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await guild.create_role(name="Muted", reason="Needed for muting")
            for channel in guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
        except discord.Forbidden:
            await ctx.send("Can't create **Muted** role (missing permissions).", delete_after=3)
            return

    if muted_role in member.roles:
        await ctx.send(f"**{member.display_name}** is already muted.", delete_after=3)
        return

    try:
        await member.add_roles(muted_role, reason=f"Muted by {ctx.author} for {count}{unit}")
        await ctx.send(f"Muted **{member.display_name}** for **{count}{unit}**.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign the Muted role.", delete_after=3)
        return

    # Wait the duration, then unmute automatically
    await asyncio.sleep(seconds)
    if muted_role in member.roles:
        try:
            await member.remove_roles(muted_role, reason="Mute time expired")
            try:
                await ctx.send(f"Unmuted **{member.display_name}** (mute time over).")
            except:
                pass  # Cannot send message (channel deleted or missing perms)
        except:
            pass  # Role already removed or missing permission


def setup(bot):
    bot.add_command(mute)
