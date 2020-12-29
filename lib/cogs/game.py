import os
import asyncio
from random import choice, shuffle

from dotenv import load_dotenv
from discord.ext import tasks
from discord.abc import PrivateChannel
from discord.ext.commands import Cog, command
from discord import Embed, ClientException
from discord.utils import get

from ..db.db import question_db, setting_db

load_dotenv()
PREFIX = os.getenv('DEFAULT_PREFIX')
DEFAULT_TIMER = os.getenv('GAME_DEFAULT_TIMER')

class KurryGame:
    def __init__(self, ctx, voice):
        self.ctx = ctx
        self.voice = voice
        self.guild_id = ctx.guild.id
        self.channel = ctx.channel
        self.is_paused = False
        custom_setting = setting_db.find_one({'guild_id': self.guild_id})
        self.topic_pool = [topic for topic in question_db.find()]
        self.timer = custom_setting['timer'] if custom_setting else DEFAULT_TIMER
        if not custom_setting:
            new_entry = {
                    'guild_id': self.guild_id,
                    'prefix': PREFIX,
                    'timer' : DEFAULT_TIMER
                }
            setting_db.insert_one(new_entry)

    async def send_voting_board(self):
        pass

    async def a_single_round(self, member_list, topic1, topic2):
        shuffle(member_list)
        for index, member in enumerate(member_list):
            if not member.bot:
                if index == 0:
                    await member.send(topic1)
                else:
                    await member.send(topic2)
        await self.channel.send(('The round has begin!\n'
            f'You have {self.timer} seconds ' 
            'to discuss and find out who has the unique topic.'))

    async def game_loop(self):
        while True:
            member_list = self.voice.members
            topic = choice(self.topic_pool)
            topic1 = topic['topic1']
            topic2 = topic['topic2']
            self.a_single_round(member_list, topic1, topic2)

            # Wait for the round to finish...
            await asyncio.sleep(self.timer)

            # Print the voting board

            # Print the result board
        

class Game(Cog):
    def __init__(self,bot):
        self.bot = bot
        self.current_voice_client = None
        self.leave_vc_if_alone.start()
        self.game = None

    def cog_unload(self):
        self.leave_vc_if_alone.cancel()

    @command(name='rule', help='Display the rules for the game.')
    async def tutorial(self,ctx):
        await ctx.send("""This is the rule of Quiz game:\n- I will give each one of you guys a card that has a word on it.
- Everyone has the the card with the same word except the impostor.\n- You have 90 seconds to discussion with your friends to find the impostor.\n- After 90 seconds, you will have to vote for the suspect.
- If the one who get the most vote is the impostor you guy win, otherwise the impostor win.""")

    @command(name='start', help='Start a new game.')
    async def start(self, ctx):
        author = ctx.message.author
        await ctx.send(f'Hello {author.mention}!')
        if not ctx.message.author.voice:
            await ctx.send('You have to be in a public voice channel to start a game!')
            return
        game_channel = ctx.message.author.voice.channel
        if self.current_voice_client:
            await self.leave_voice_channel()
        self.current_voice_client = await game_channel.connect()

        self.game = KurryGame(ctx=ctx, voice=game_channel)
        await self.game.a_single_round()

    @command(name='stop', alias=['dc', 'disconnect', 'quit'], help='Stop the game.')
    async def stop(self, ctx):
        pass

    @command(name='skip', help='Skip this round, get a new topic.')
    async def skip(self, ctx):
        pass

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("game")
    
    @tasks.loop(seconds=3.0)
    async def leave_vc_if_alone(self):
        if self.current_voice_client:
            # If alone in voice channel
            if len(self.current_voice_client.channel.members) == 1:
                await self.leave_voice_channel()

    @leave_vc_if_alone.before_loop
    async def before_checking(self):
        print('Kagari is gearing up... (leave_vc_if_alone)')
        await self.bot.wait_until_ready()

    async def leave_voice_channel(self):
        try:
            await self.current_voice_client.disconnect()
        finally:
            self.current_voice_client = None


def setup(bot):
    bot.add_cog(Game(bot))
