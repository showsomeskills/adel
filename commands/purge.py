import discord
from discord.ext import commands
import random
from perms import has_role_permission

@commands.command(name='purge')
@has_role_permission('purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, target: str = None, amount: str = None):
    """Purge messages.
    
    Usage:
    .purge <amount>            - deletes <amount> recent messages
    .purge <user> <amount>     - deletes <amount> recent messages from that user
    .purge bots <amount>       - deletes <amount> recent messages from bots only
    """

    if target is None:
        await ctx.send("Please specify the number of messages to delete (1-100), a user and number, or 'bots' and number.", delete_after=5)
        return

    if target.lower() == "bots":
        # Purge messages from bots only
        if amount is None:
            await ctx.send("Please specify how many bot messages to purge (1-100).", delete_after=5)
            return
        try:
            number = int(amount)
            if number < 1 or number > 100:
                await ctx.send("Please provide a number between 1 and 100.", delete_after=5)
                return
        except ValueError:
            await ctx.send("That doesn't look like a valid number. Please enter a number between 1 and 100.", delete_after=5)
            return

        deleted_messages = []
        fetch_limit = 500  # limit max messages to search
        try:
            async for message in ctx.channel.history(limit=fetch_limit):
                if message.author.bot:
                    deleted_messages.append(message)
                    if len(deleted_messages) >= number:
                        break
            if not deleted_messages:
                await ctx.send("No bot messages found to delete.", delete_after=5)
                return
            await ctx.channel.delete_messages(deleted_messages)
            await ctx.send(f"Removed **{len(deleted_messages)}** messages from bots.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.", delete_after=5)
        except discord.HTTPException as e:
            await ctx.send(f"Failed to delete messages: **{e}**", delete_after=5)
        return

    # Check if target is user or number (amount)
    if amount is None:
        # Only one argument was given
        # If target is a number => purge that many messages from everyone
        if target.isdigit():
            try:
                number = int(target)
                if number < 1 or number > 100:
                    await ctx.send("Please provide a number between 1 and 100.", delete_after=5)
                    return
                deleted = await ctx.channel.purge(limit=number + 1)  # +1 to include command message
                count = len(deleted) - 1
                replies = [
                    f"Removed **{count}** messages as you asked.",
                    f"Purged **{count}** messages successfully.",
                ]
                await ctx.send(random.choice(replies), delete_after=5)
                return
            except ValueError:
                await ctx.send("That doesn't look like a valid number. Please enter a number between 1 and 100.", delete_after=5)
                return
        else:
            await ctx.send("Please specify the number of messages to delete (1-100), a user and number, or 'bots' and number.", delete_after=5)
            return

    # Here we assume two arguments: target=user, amount=number

    user_arg = target
    number_arg = amount

    def find_member(search):
        member = None
        # Mention
        if search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = ctx.guild.get_member(user_id)
            except:
                pass
        # ID
        elif search.isdigit():
            member = ctx.guild.get_member(int(search))
        return member  # No fuzzy matching

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=5)
        return

    try:
        number = int(number_arg)
        if number < 1 or number > 100:
            await ctx.send("Please provide a number between 1 and 100 for messages to purge.", delete_after=5)
            return
    except ValueError:
        await ctx.send("That doesn't look like a valid number. Please enter a number between 1 and 100.", delete_after=5)
        return

    deleted_messages = []
    fetch_limit = 500  # max messages to scan

    try:
        async for message in ctx.channel.history(limit=fetch_limit):
            if message.author == member:
                deleted_messages.append(message)
                if len(deleted_messages) >= number:
                    break

        if not deleted_messages:
            await ctx.send(f"No messages found from **{member.display_name}** to delete.", delete_after=5)
            return

        await ctx.channel.delete_messages(deleted_messages)
        await ctx.send(f"Removed **{len(deleted_messages)}** messages from **{member.display_name}**.", delete_after=5)

    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to delete messages: **{e}**", delete_after=5)


def setup(bot):
    bot.add_command(purge)
