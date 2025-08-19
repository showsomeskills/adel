import discord
from discord.ext import commands
from perms import has_role_permission

@commands.command(name='unmute')
@has_role_permission('unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, *, user_arg=None):
    if not user_arg:
        await ctx.send("Usage: .unmute <user> (mention or ID)", delete_after=3)
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
        return member  # No fuzzy matching here

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=3)
        return

    muted_role = discord.utils.get(guild.roles, name="Muted")
    if not muted_role:
        await ctx.send("There is no **Muted** role on this server.", delete_after=3)
        return

    if muted_role not in member.roles:
        await ctx.send(f"**{member.display_name}** is not muted.", delete_after=3)
        return

    if muted_role >= guild.me.top_role:
        await ctx.send("I cannot remove the Muted role because it is higher or equal to my top role.", delete_after=3)
        return

    try:
        await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
        await ctx.send(f"Unmuted **{member.display_name}** successfully.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove the Muted role.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to unmute user. Error: **{e}**", delete_after=3)


def setup(bot):
    bot.add_command(unmute)
