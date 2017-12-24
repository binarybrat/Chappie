import asyncio
import os
import sys
sys.path.insert(0, "lib")
import logging
import logging.handlers
import traceback
import datetime
import subprocess
from discord.ext import commands
import discord

#from cogs.utils.settings import Settings
#from cogs.utils.dataIO import dataIO
#from cogs.utils.chat_formatting import inline
from collections import Counter
from io import TextIOWrapper

description = "Chappie - A bot made  by Philzeey"

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):

        def prefix_manager(bot, message):
            """
            Returns prefixes of the message's server if set.
            If none are set or if the message's server is None
            it will return the global prefixes instead.

            Requires a Bot instance and a Message object to be
            passed as arguments.
            """
            return bot.settings.get_prefixes(message.server)

        self.counter = Counter()
        self.uptime = datetime.datetime.utcnow()  # Refreshed before login
        self._message_modifiers = []
        self.settings = Settings()
        self._intro_displayed = False
        self._shutdown_mode = None
        self.logger = set_logger(self)
        self._last_exception = None
        self.oauth_url = ""
        if 'self_bot' in kwargs:
            self.settings.self_bot = kwargs['self_bot']
        else:
            kwargs['self_bot'] = self.settings.self_bot
            if self.settings.self_bot:
                kwargs['pm_help'] = False
        super().__init__(*args, command_prefix=prefix_manager, **kwargs)

    async def send_message(self, *args, **kwargs):
        if self._message_modifiers:
            if "content" in kwargs:
                pass
            elif len(args) == 2:
                args = list(args)
                kwargs["content"] = args.pop()
            else:
                return await super().send_message(*args, **kwargs)

            content = kwargs['content']
            for m in self._message_modifiers:
                try:
                    content = str(m(content))
                except:   # Faulty modifiers should not
                    pass  # break send_message
            kwargs['content'] = content

        return await super().send_message(*args, **kwargs)

    async def shutdown(self, *, restart=False):
        """Gracefully quits Red with exit code 0

        If restart is True, the exit code will be 26 instead
        The launcher automatically restarts Red when that happens"""
        self._shutdown_mode = not restart
        await self.logout()

    def add_message_modifier(self, func):
        """
        Adds a message modifier to the bot

        A message modifier is a callable that accepts a message's
        content as the first positional argument.
        Before a message gets sent, func will get called with
        the message's content as the only argument. The message's
        content will then be modified to be the func's return
        value.
        Exceptions thrown by the callable will be catched and
        silenced.
        """
        if not callable(func):
            raise TypeError("The message modifier function "
                            "must be a callable.")

        self._message_modifiers.append(func)

    def remove_message_modifier(self, func):
        """Removes a message modifier from the bot"""
        if func not in self._message_modifiers:
            raise RuntimeError("Function not present in the message "
                               "modifiers.")

        self._message_modifiers.remove(func)

    def clear_message_modifiers(self):
        """Removes all message modifiers from the bot"""
        self._message_modifiers.clear()

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await self.send_message(ctx.message.channel, page)
        else:
            pages = self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.send_message(ctx.message.channel, page)

    def user_allowed(self, message):
        author = message.author

        if author.bot:
            return False

        if author == self.user:
            return self.settings.self_bot

        mod_cog = self.get_cog('Mod')
        global_ignores = self.get_cog('Owner').global_ignores

        if self.settings.owner == author.id:
            return True

        if author.id in global_ignores["blacklist"]:
            return False

        if global_ignores["whitelist"]:
            if author.id not in global_ignores["whitelist"]:
                return False

        if not message.channel.is_private:
            server = message.server
            names = (self.settings.get_server_admin(
                server), self.settings.get_server_mod(server))
            results = map(
                lambda name: discord.utils.get(author.roles, name=name),
                names)
            for r in results:
                if r is not None:
                    return True

        if mod_cog is not None:
            if not message.channel.is_private:
                if message.server.id in mod_cog.ignore_list["SERVERS"]:
                    return False

                if message.channel.id in mod_cog.ignore_list["CHANNELS"]:
                    return False

        return True

    async def pip_install(self, name, *, timeout=None):
        """
        Installs a pip package in the local 'lib' folder in a thread safe
        way. On Mac systems the 'lib' folder is not used.
        Can specify the max seconds to wait for the task to complete

        Returns a bool indicating if the installation was successful
        """

        IS_MAC = sys.platform == "darwin"
        interpreter = sys.executable

        if interpreter is None:
            raise RuntimeError("Couldn't find Python's interpreter")

        args = [
            interpreter, "-m",
            "pip", "install",
            "--upgrade",
            "--target", "lib",
            name
        ]

        if IS_MAC: # --target is a problem on Homebrew. See PR #552
            args.remove("--target")
            args.remove("lib")

        def install():
            code = subprocess.call(args)
            sys.path_importer_cache = {}
            return not bool(code)

        response = self.loop.run_in_executor(None, install)
        return await asyncio.wait_for(response, timeout=timeout)


class Formatter(commands.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _add_subcommands_to_page(self, max_width, commands):
        for name, command in sorted(commands, key=lambda t: t[0]):
            if name in command.aliases:
                # skip aliases
                continue

            entry = '  {0:<{width}} {1}'.format(name, command.short_doc,
                                                width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)


def initialize(bot_class=Bot, formatter_class=Formatter):
    formatter = formatter_class(show_check_failure=False)

    bot = bot_class(formatter=formatter, description=description, pm_help=None)

    async def get_oauth_url():
        try:
            data = await bot.application_info()
        except Exception as e:
            return "Couldn't retrieve invite link.Error: {}".format(e)
        return discord.utils.oauth_url(data.id)

    async def set_bot_owner():
        if bot.settings.self_bot:
            bot.settings.owner = bot.user.id
            return "[Selfbot mode]"

        if bot.settings.owner:
            owner = discord.utils.get(bot.get_all_members(),
                                      id=bot.settings.owner)
            if not owner:
                try:
                    owner = await bot.get_user_info(bot.settings.owner)
                except:
                    owner = None
                if not owner:
                    owner = bot.settings.owner  # Just the ID then
            return owner

        how_to = "Do `[p]set owner` in chat to set it"

        if bot.user.bot:  # Can fetch owner
            try:
                data = await bot.application_info()
                bot.settings.owner = data.owner.id
                bot.settings.save_settings()
                return data.owner
            except:
                return "Failed to fetch owner. " + how_to
        else:
            return "Yet to be set. " + how_to

    @bot.event
    async def on_ready():
        if bot._intro_displayed:
            return
        bot._intro_displayed = True

        owner_cog = bot.get_cog('Owner')
        total_cogs = len(owner_cog._list_cogs())
        users = len(set(bot.get_all_members()))
        servers = len(bot.servers)
        channels = len([c for c in bot.get_all_channels()])

        login_time = datetime.datetime.utcnow() - bot.uptime
        login_time = login_time.seconds + login_time.microseconds/1E6

        print("Login successful. ({}ms)\n".format(login_time))

        owner = await set_bot_owner()

        print("-----------------")
        print("Red - Discord Bot")
        print("-----------------")
        print(str(bot.user))
        print("\nConnected to:")
        print("{} servers".format(servers))
        print("{} channels".format(channels))
        print("{} users\n".format(users))
        prefix_label = 'Prefix'
        if len(bot.settings.prefixes) > 1:
            prefix_label += 'es'
        print("{}: {}".format(prefix_label, " ".join(bot.settings.prefixes)))
        print("Owner: " + str(owner))
        print("{}/{} active cogs with {} commands".format(
            len(bot.cogs), total_cogs, len(bot.commands)))
        print("-----------------")

        if bot.settings.token and not bot.settings.self_bot:
            print("\nUse this url to bring your bot to a server:")
            url = await get_oauth_url()
            bot.oauth_url = url
            print(url)

        print("\nOfficial server: https://discord.gg/red")

        print("Make sure to keep your bot updated. Select the 'Update' "
              "option from the launcher.")

        await bot.get_cog('Owner').disable_commands()

    @bot.event
    async def on_resumed():
        bot.counter["session_resumed"] += 1

    @bot.event
    async def on_command(command, ctx):
        bot.counter["processed_commands"] += 1

    @bot.event
    async def on_message(message):
        bot.counter["messages_read"] += 1
        if bot.user_allowed(message):
            await bot.process_commands(message)

    @bot.event
    async def on_command_error(error, ctx):
        channel = ctx.message.channel
        if isinstance(error, commands.MissingRequiredArgument):
            await bot.send_cmd_help(ctx)
        elif isinstance(error, commands.BadArgument):
            await bot.send_cmd_help(ctx)
        elif isinstance(error, commands.DisabledCommand):
            await bot.send_message(channel, "That command is disabled.")
        elif isinstance(error, commands.CommandInvokeError):
            # A bit hacky, couldn't find a better way
            no_dms = "Cannot send messages to this user"
            is_help_cmd = ctx.command.qualified_name == "help"
            is_forbidden = isinstance(error.original, discord.Forbidden)
            if is_help_cmd and is_forbidden and error.original.text == no_dms:
                msg = ("I couldn't send the help message to you in DM. Either"
                       " you blocked me or you disabled DMs in this server.")
                await bot.send_message(channel, msg)
                return

            bot.logger.exception("Exception in command '{}'".format(
                ctx.command.qualified_name), exc_info=error.original)
            message = ("Error in command '{}'. Check your console or "
                       "logs for details."
                       "".format(ctx.command.qualified_name))
            log = ("Exception in command '{}'\n"
                   "".format(ctx.command.qualified_name))
            log += "".join(traceback.format_exception(type(error), error,
                                                      error.__traceback__))
            bot._last_exception = log
            await ctx.bot.send_message(channel, inline(message))
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await bot.send_message(channel, "That command is not "
                                            "available in DMs.")
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.send_message(channel, "This command is on cooldown. "
                                            "Try again in {:.2f}s"
                                            "".format(error.retry_after))
        else:
            bot.logger.exception(type(error).__name__, exc_info=error)

    return bot


def check_folders():
    folders = ("data", "data/red", "cogs", "cogs/utils")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)