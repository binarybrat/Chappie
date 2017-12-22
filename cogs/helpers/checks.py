import json
import time
import git
import discord
import os
import aiohttp
from urllib.parse import quote as uriquote


def embed_perms(message):
    try:
        check = message.author.permissions_in(message.channel).embed_links
    except:
        check = True

    return check


def get_user(message, user):
    try:
        member = message.mentions[0]
    except:
        member = message.guild.get_member_named(user)
    if not member:
        try:
            member = message.guild.get_member(int(user))
        except ValueError:
            pass
    if not member:
        return None
    return member


def find_channel(channel_list, text):
    if text.isdigit():
        found_channel = discord.utils.get(channel_list, id=int(text))
    elif text.startswith("<#") and text.endswith(">"):
        found_channel = discord.utils.get(channel_list,
                                          id=text.replace("<", "").replace(">", "").replace("#", ""))
    else:
        found_channel = discord.utils.get(channel_list, name=text)
    return found_channel

def attach_perms(message):
    return message.author.permissions_in(message.channel).attach_files
