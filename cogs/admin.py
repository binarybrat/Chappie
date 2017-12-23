from discord.ext import commands
from .helpers import point_system
from .helpers.checks import embed_perms, find_channel, find_role
import discord
import asyncio


class Admin:
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def on_command_error(cls, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send(
                'ON_COMMAND_ERROR, Sorry either you don\'t have permission for command or something went wrong.')

    @classmethod
    async def check_if_is_panic_channel(cls, ctx):
        guild = ctx.guild
        channel = find_channel(guild.channels, 'support-panic-attacks')
        return ctx.message.channel.id == channel.id

    @commands.command(hidden=True)
    @commands.has_any_role('Staff')
    @commands.check(check_if_is_panic_channel)
    async def solved(self, ctx):
        """Purges the last 100 messages in the panic room channel."""

        guild = ctx.guild
        role = find_channel(guild.roles, '@everyone')

        await ctx.channel.purge(limit=100)
        await ctx.channel.send('To use this chat room please type in **!panic** in a different chat room first. '
                               'This will alert anyone online to help you. '
                               'This room is for **panic attacks**, if you\'re looking for support please use '
                               'our support chat rooms for that.')

        await ctx.channel.set_permissions(role, send_messages=False)

    @commands.command(hidden=True)
    async def count_messages(self, ctx):
        """Counts messages for every person in the server since the beginning of time."""

        print('Counting messages from all channels...')
        d = {}
        guild = ctx.guild
        for channel in guild.text_channels:
            async for message in channel.history(limit=100000):
                if not message.author.bot:
                    key = str(message.author)
                    if not key in d:
                        value = 1
                        d[key] = value
                    else:
                        value = d[key]
                        d[key] = value + 1
        print('Counting all messages were successful...')
        for k, v in d.items():
            pt = point_system
            if not pt.check_if_user_in_table_new_MSG(k, guild):
                pt.insert_user_in_table_new_MSG(k, v, guild)
            else:
                pt.update_table_new_MSG(k, v, guild)
        print('All points have been updated in the database...')


def setup(bot):
    bot.add_cog(Admin(bot))
