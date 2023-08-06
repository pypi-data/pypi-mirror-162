import disnake
from rbxexecutions import api
from disnake.ext import commands, tasks

class commands_d(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.printer.start()
    
    @tasks.loop(seconds=1)
    async def printer(self):
        activity = disnake.Game(name=f"{(await api.get_execution()).get('counter')} | Execution", type=3)
        await self.bot.change_presence(activity=activity)

    

def setup(bot):
    bot.add_cog(commands_d(bot))