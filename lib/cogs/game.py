from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed

class Rule(Cog):
    def __init__(self,bot):
        self.bot = bot

    @command(name='rule')
    async def tutorial(self,ctx):
        await ctx.send("""This is the rule of Quiz game:\n- I will give each one of you guys a card that has a word on it.
- Everyone has the the card with the same word except the impostor.\n- You have 90 seconds to discussion with your friends to find the impostor.\n- After 90 seconds, you will have to vote for the suspect.
- If the one who get the most vote is the impostor you guy win, otherwise the impostor win.""")

    @command(name='start')
    async def start(self, ctx):
        # guild = ctx.guild
        author = ctx.message.author
        await ctx.send(f'Hello {author.mention}!')
        if not ctx.message.author.voice:
            await ctx.send('You have to be in a voice channel to start a game!')
            return
        game_channel = ctx.message.author.voice.channel
        await game_channel.connect()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("game")
    
    
def setup(bot):
    bot.add_cog(Rule(bot))