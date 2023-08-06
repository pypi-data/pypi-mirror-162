import disnake
import os

from disnake.ext import commands

token = ''
prefix = ''

def start():
    bot = commands.Bot(command_prefix=prefix or '!', intents=disnake.Intents.all())

    @bot.event
    async def on_ready():
        print(bot.user, 'Ready')
        for filename in ['status.py', 'commands.py']:
            if filename.endswith('.py') and filename != '__init__.py':
                print(filename)
                bot.load_extension(f'rbxexecutions.discordbot.cogs.{filename[:-3]}')

    bot.run(token)