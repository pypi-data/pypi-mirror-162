import disnake
from rbxexecutions import api
from disnake.ext import commands, tasks
from functools import wraps
from rbxexecutions.discordbot import admins

class commands_a(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def admins(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if ctx.author.id in admins:
                return await func(self, ctx, *args, **kwargs)
            
            await ctx.send('You no have permission')

        return wrapper

    @commands.command()
    @admins
    async def set_custom_name(self, ctx, name):
        result = await api.set_custom_name(name)
        await ctx.send(f"Successfully set custom name %s " % result.get('public_key'))

    @commands.command(pass_context=True)
    async def get_execution(self, ctx):
        result = await api.get_execution()
        await ctx.send(f"Executions: %s " % result.get('counter'))


    @commands.command()
    @admins
    async def set_execution(self, ctx, value):
        result = await api.set_execution(value)
        await ctx.send(f"Successfully set execution %s " % result.get('counter'))

    @commands.command()
    @admins
    async def get_name(self, ctx):
        result = (await api.get_execution()).get('public_key')
        await ctx.send(result)

def setup(bot):
    bot.add_cog(commands_a(bot))