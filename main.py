from discord.ext import commands
from cogs.helpers import point_system
import traceback
import discord
import sys
import json

initial_extensions = ('cogs.admin',
                      'cogs.scraping',
                      'cogs.music',
                      'cogs.members',
                      'cogs.poll',
                      'cogs.help',
                      'cogs.userinfo',
                      'cogs.serverinfo')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game
    # you could remove type and url.
    await bot.change_presence(game=discord.Game(name='with your dog'))

    # Here we load our extensions listed above in [initial_extensions].
    if __name__ == '__main__':
        for extension in initial_extensions:
            try:
                bot.load_extension(extension)
            except Exception as e:
                print(
                    f'Failed to load extension {extension}.',
                    file=sys.stderr)
                traceback.print_exc()
    print(f'Successfully logged in and booted...!')


@bot.listen()
async def on_message(message: discord.Message):
    if not message.author.bot:
        pt = point_system
        if not pt.check_if_user_in_table(message):
            pt.insert_user_in_table(message)
        que = pt.query_points(message)
        points = que[0].num_points
        points += 1
        print(points)
        pt.update_table(message, points)

with open("cogs/helpers/config.json", "r", encoding="utf8") as fp:
    config = json.load(fp)
    token = config["test_token"]

bot.run(token, bot=True, reconnect=True)