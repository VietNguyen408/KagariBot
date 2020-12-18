from typing import Optional

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import command


class Test(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='ping', aliases=['p'])
    async def hello_world(self, ctx):
        await ctx.send("pong!")

    @command(name='start')
    async def start(self, ctx):
        guild = ctx.guild
        author = ctx.message.author
        await ctx.send(f'Hello {author.mention}!')
        if not ctx.message.author.voice:
            await ctx.send('You have to be in a voice channel to start a game!')
            return
        game_channel = ctx.message.author.voice.channel
        await game_channel.connect()

    @command(name='slap', aliases=['hit'])
    async def bitch_slap(self, ctx, member: Member, *, reason: Optional[str] = 'no reason'):
        await ctx.send(f'{ctx.author.display_name} slapped {member.display_name} for {reason}!')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("test")

    # @Cog.listener()
    # async def on_message(self):
    #     pass


def setup(bot):
    bot.add_cog(Test(bot))
