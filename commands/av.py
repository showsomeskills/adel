import discord
from discord.ext import commands
from perms import has_role_permission

@commands.command(name='av')
@has_role_permission('av')
async def av(ctx, *, user_arg=None):
    guild = ctx.guild

    def find_member(search):
        member = None
        # Mention: <@123> or <@!123>
        if search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = guild.get_member(user_id)
            except:
                pass
        # ID
        elif search.isdigit():
            member = guild.get_member(int(search))
        return member  # Only mentions and IDs!

    # Command logic
    if user_arg:
        member = find_member(user_arg)
        if not member:
            await ctx.send(f"Could not find a user matching **{user_arg}**. Please mention or provide a user ID.", delete_after=3)
            return
    else:
        member = ctx.author

    avatar_url = member.display_avatar.url
    embed = discord.Embed(title=f"Avatar of **{member.display_name}**")
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    await ctx.send(embed=embed)

def setup(bot):
    bot.add_command(av)
