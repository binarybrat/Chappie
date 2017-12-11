import sqlite3
import random

thingsToSay = ['What?', 'That\'s me', 'Hello!',
               'That\'s my name, don\'t wear it out']


async def findChannelObject(guild, channel_name):
    for channel in guild.channels:
        if channel.name == channel_name:
            return channel


async def findRoleObject(guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return role