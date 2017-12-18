from discord.ext import commands
from cogs.helpers import utils, point_system
import discord
import asyncio
from .helpers.checks import embed_perms


class Admin:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send('ON_COMMAND_ERROR, Sorry either you don\'t have permission for command or something went wrong.')

    async def check_if_is_panic_channel(ctx):
        guild = ctx.guild
        channel = await utils.findChannelObject(guild, 'support-panic-attacks')
        return ctx.message.channel.id == channel.id

    def check_approved_server(ctx):
        return ctx.guild.name == "Health Anxiety Community"

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_any_role('Staff')
    @commands.check(check_approved_server)
    async def purge(self, ctx):
        """Purges the last 100 messages in a channel"""
        await ctx.channel.purge(limit=100)

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_any_role('Staff')
    @commands.check(check_if_is_panic_channel)
    @commands.check(check_approved_server)
    async def solved(self, ctx):
        """Purges the last 100 messages in the panic room channel"""
        guild = ctx.guild
        channel = await utils.findChannelObject(guild, 'support-panic-attacks')
        role = await utils.findRoleObject(guild, '@everyone')

        await ctx.channel.purge(limit=100)
        await ctx.channel.send('To use this chat room please type in **!panic** in a different chat room first. '
                               'This will alert anyone online to help you. '
                               'This room is for **panic attacks**, if you\'re looking for support please use '
                               'our support chat rooms for that.')

        await ctx.guild.get_channel(channel.id).set_permissions(role, send_messages=False)

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_any_role('Admins')
    @commands.check(check_approved_server)
    async def mute(self, ctx, member: discord.Member):
        """Turn off member messaging"""
        guild = member.guild
        role = await utils.findRoleObject(guild, 'HRU')
        await member.add_roles(role)

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_any_role('Admins')
    @commands.check(check_approved_server)
    async def unmute(self, ctx, member: discord.Member):
        """Turn on member messaging"""
        guild = member.guild
        role = await utils.findRoleObject(guild, 'HRU')
        await member.remove_roles(role)

    @commands.command(hidden=True)
    @commands.guild_only()
    async def top5(self, ctx):
        pt = point_system

        top = pt.get_top_5(ctx.guild)
        em = discord.Embed(timestamp=ctx.message.created_at, colour=0x708DD0)
        avi = 'http://www.humanengineers.com/wp-content/uploads/2017/09/tog.png'
        for user in top:
            if embed_perms(ctx.message):
                em.add_field(name='User ID', value=user.username, inline=True)
                em.add_field(name='Points', value=user.num_points, inline=True)
        em.set_thumbnail(url=avi)
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    @commands.guild_only()
    async def collect_messages(self, ctx):
        d = {}
        guild = ctx.guild
        for channel in guild.text_channels:
            async for message in channel.history():
                key = str(message.author)
                if not key in d:
                    value = 1
                    d[key] = value
                else:
                    value = d[key]
                    d[key] = value + 1
        file = open('textfile.txt', 'w')
        for k, v in d.items():
            file.write(k + ': ' + str(v) + '\n')
            print(k + ': ' + str(v))
        file.close()




def setup(bot):
    bot.add_cog(Admin(bot))
