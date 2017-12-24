from discord.ext import commands
from .helpers.checks import find_channel, find_role, embed_perms, get_user
from .helpers import point_system
import discord
from random import *


class Members:
    def __init__(self, bot):
        self.bot = bot

    def check_approved_server(ctx):
        return ctx.guild.name == "Testing Server"

    @commands.command()
    @commands.check(check_approved_server)
    async def panic(self, ctx):
        """Panic attack command to alert others."""

        channel = find_channel(ctx.guild.text_channels, 'support-panic-attacks')
        role = find_role(ctx.guild.roles, '@everyone')

        await ctx.guild.get_channel(channel.id).set_permissions(role, send_messages=True)

        msg1 = 'Hello {0.author.mention}, I see you\'re having a panic attack. ' \
               'Please move to our {1.mention} where we can better assist you.'.format(ctx, channel)
        msg2 = 'Is anyone @here available to assist {0.author.mention}.'.format(ctx)

        await ctx.channel.send(msg1)
        await ctx.guild.get_channel(channel.id).send(msg2)

    @commands.command()
    async def top5(self, ctx):
        """Gets the top 5 ranked people in the server."""

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


def setup(bot):
    bot.add_cog(Members(bot))
