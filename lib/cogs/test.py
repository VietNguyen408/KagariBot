from discord.ext.commands import Cog
from discord.ext.commands import command


class Test(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='ping', aliases=['p'])
    async def hello_world(self, ctx):
        await ctx.send("pong!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("test")

    # @Cog.listener()
    # async def on_message(self):
    #     pass


def setup(bot):
    bot.add_cog(Test(bot))
