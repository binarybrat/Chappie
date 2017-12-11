from discord.ext import commands
from cogs.helpers import config
from cogs.helpers import utils
import discord
import asyncio
import sqlite3
import random
import sys
import os
script_dir = sys.path[0]
img_path = os.path.join(script_dir, 'cogs/helpers/media/')


class Members:
    def __init__(self, bot):
        self.bot = bot

    def check_approved_server(ctx):
        return ctx.guild.name == "Health Anxiety Community"

    @commands.command()
    @commands.guild_only()
    @commands.check(check_approved_server)
    async def meme(self, ctx):
        """Sends a meme to the channel"""
        media_to_use = random.choice(config.memlist)
        await ctx.channel.send(file=discord.File(fp=img_path + media_to_use))

    @commands.command()
    @commands.guild_only()
    async def hug(self, ctx):
        """Sends a hug to the channel"""
        media_to_use = random.choice(config.huglist)
        await ctx.channel.send(file=discord.File(fp=img_path + media_to_use))

    @commands.command()
    @commands.guild_only()
    @commands.check(check_approved_server)
    async def breathe(self, ctx):
        """Sends a breathing gif to the channel"""
        media_to_use = random.choice(config.breathelist)
        await ctx.channel.send(file=discord.File(fp=img_path + media_to_use))

    @commands.command()
    @commands.guild_only()
    async def happybday(self, ctx):
        """Sends a happy birthday message to the channel"""
        media_to_use = random.choice(config.bdaylist)
        await ctx.channel.send(file=discord.File(fp=img_path + media_to_use))

    @commands.command()
    @commands.guild_only()
    async def congrats(self, ctx):
        """Sends a congrats message to the channel"""
        media_to_use = random.choice(config.congratslist)
        await ctx.channel.send(file=discord.File(fp=img_path + media_to_use))

    @commands.command()
    @commands.guild_only()
    @commands.check(check_approved_server)
    async def panic(self, ctx):
        """Panic attack command to alert others."""
        guild = ctx.guild
        channel = await utils.findChannelObject(guild, 'support-panic-attacks')
        role = await utils.findRoleObject(guild, '@everyone')

        await ctx.guild.get_channel(channel.id).set_permissions(role, send_messages=True)

        msg1 = 'Hello ' + ctx.author.mention + ', I see you\'re having a panic attack. Please move to our ' + \
            channel.mention + ' where we can better assist you.'
        msg2 = 'Is anyone @here available to assist {0.author.mention}.'.format(
            ctx)

        await ctx.channel.send(msg1)
        await ctx.guild.get_channel(channel.id).send(msg2)


def setup(bot):
    bot.add_cog(Members(bot))
