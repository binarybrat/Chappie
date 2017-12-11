from discord.ext import commands
from bs4 import BeautifulSoup
import requests


class Scraping:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def urban(self, ctx, *, arg):
        """Finds the word, you typed, in urbandictionary.com"""
        r = requests.get(
            "http://www.urbandictionary.com/define.php?term={}".format(arg))
        soup = BeautifulSoup(r.content, "html.parser")
        definition = soup.find("div", attrs={"class": "meaning"}).text
        await ctx.channel.send("From Urban Dictionary, " + "**" + arg + "**" + " is defined as:"'\n''\n' + definition)

    @commands.command()
    @commands.guild_only()
    async def define(self, ctx, *, arg):
        """Finds the word, you typed, in dictionary.com"""
        r = requests.get(
            "http://www.dictionary.com/browse/{}?s=t".format(arg))
        soup = BeautifulSoup(r.content, "html.parser")
        definition = soup.find("div", attrs={"class": "def-content"}).text
        await ctx.channel.send("From Dictionary.com, " + "**" + arg + "**" + " is defined as:"'\n''\n' + definition)


def setup(bot):
    bot.add_cog(Scraping(bot))
