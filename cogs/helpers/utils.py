import sqlite3
import random
from . import point_system

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


async def point_system_check(message):
    if not message.author.bot:
        pt = point_system
        if not pt.check_if_user_in_table(message):
            pt.insert_user_in_table(message)
        que = pt.query_points(message)
        points = que[0].num_points
        points += 1
        print(points)
        pt.update_table(message, points)