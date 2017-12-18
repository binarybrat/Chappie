import sqlite3
import random
from . import point_system

thingsToSay = ['What?', 'That\'s me', 'Hello!',
               'That\'s my name, don\'t wear it out']

rank = ['Level 1: Server Newbie', 'Level 2: Server Apprentice', 'Level 3: Server Helper', 'Level 4: Server Contributor', 'Level 5: Server Legend']


async def findChannelObject(guild, channel_name):
    for channel in guild.channels:
        if channel.name == channel_name:
            return channel


async def findRoleObject(guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return role


async def point_system_check(message):
    guild = message.guild
    if not message.author.bot:
        pt = point_system
        if not pt.check_if_user_in_table(message):
            pt.insert_user_in_table(message)
        que = pt.query_points(message)
        points = que[0].num_points
        points += 1
        pt.update_table(message, points)

        if 100 < points <= 249:

            role1 = await findRoleObject(guild, rank[0])
            if not role1 in message.author.roles:
                msg = 'Congrats {1.author.mention}, you have achieved {0.name}! The more you contribute to any server chat the more XP you get :). You will have to gain 150 more XP to gain another level! :robot:'
                await message.author.add_roles(role1)
                await message.channel.send(msg.format(role1, message))

        elif 250 <= points <= 499:

            role1 = await findRoleObject(guild, rank[1])
            role2 = await findRoleObject(guild, rank[1 - 1])
            if not role1 in message.author.roles:
                msg = 'Congrats {1.author.mention}, you have achieved {0.name}! The more you contribute to any server chat the more XP you get :). You will have to gain 250 more XP to gain another level! :robot:'
                await message.author.remove_roles(role2)
                await message.author.add_roles(role1)
                await message.channel.send(msg.format(role1, message))

        elif 500 <= points <= 999:

            role1 = await findRoleObject(guild, rank[2])
            role2 = await findRoleObject(guild, rank[2 - 1])
            if not role1 in message.author.roles:
                msg = 'Congrats {1.author.mention}, you have achieved {0.name}! The more you contribute to any server chat the more XP you get :). You will have to gain 750 more XP to gain another level! :robot:'
                await message.author.remove_roles(role2)
                await message.author.add_roles(role1)
                await message.channel.send(msg.format(role1, message))

        elif 1000 <= points <= 2499:

            role1 = await findRoleObject(guild, rank[3])
            role2 = await findRoleObject(guild, rank[3 - 1])
            if not role1 in message.author.roles:
                msg = 'Congrats {1.author.mention}, you have achieved {0.name}! The more you contribute to any server chat the more XP you get :). You will have to gain 1500 more XP to gain another level! :robot:'
                await message.author.remove_roles(role2)
                await message.author.add_roles(role1)
                await message.channel.send(msg.format(role1, message))

        elif 2500 <= points:

            role1 = await findRoleObject(guild, rank[4])
            role2 = await findRoleObject(guild, rank[4 - 1])
            if not role1 in message.author.roles:
                msg = 'Congrats {1.author.mention}, you have achieved {0.name}! The more you contribute to any server chat the more XP you get :). You have reached maximum level! :robot:'
                await message.author.remove_roles(role2)
                await message.author.add_roles(role1)
                await message.channel.send(msg.format(role1, message))