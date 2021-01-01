import os
import asyncio
from random import choice, shuffle

from dotenv import load_dotenv
from discord.ext import tasks
from discord.abc import PrivateChannel
from discord.ext.commands import Cog, command
from discord import Embed, ClientException
from discord.utils import get

from ..db.db import question_db

DEFAULT_TIMER = 60

class KurryGame:
    def __init__(self, ctx, voice, timer):
        self.ctx = ctx
        self.voice = voice
        self.timer = timer
        self.guild_id = ctx.guild.id
        self.channel = ctx.channel
        self.topic_pool = [topic for topic in question_db.find()]

    async def change_timer(self, new_timer):
        pass

    # async def change_mode(self, option):
    #     pass

    async def send_voting_board(self, member_list, topic1, topic2):
        await self.channel.send('Hell yeah.')

    async def send_round_result(self, member_list, topic1, topic2):
        await self.channel.send('Hell no.')

    async def send_topic_to_players(self, member_list, topic1, topic2):
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
            member_list = list(filter(lambda member: not member.bot, member_list))
            shuffle(member_list)
            topic = choice(self.topic_pool)
            topic1 = topic['topic1']
            topic2 = topic['topic2']
            self.topic_pool.remove(topic)
            print((topic1, topic2))

            # Wait for the round to finish...
            await asyncio.sleep(self.timer-50)
            await self.send_topic_to_players(member_list, topic1, topic2)

            # Print the voting board
            await self.send_voting_board(member_list, topic1, topic2)
            await asyncio.sleep(10)

            # Print the result board
            await self.send_round_result(member_list, topic1, topic2)
        

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

        kurry_game = KurryGame(ctx=ctx, voice=game_channel, timer = DEFAULT_TIMER)
        self.game = asyncio.ensure_future(kurry_game.game_loop())
    
    @command(name='kurry', help = 'Start the game immediately')
    async def kurry(self,ctx):
        timer = DEFAULT_TIMER
        bot_start_message = await ctx.send("Need at least 3 players\n💩Join | :gear:Setting")
        await bot_start_message.add_reaction("💩")
        await bot_start_message.add_reaction("⚙️")
        bot_start_message_id = bot_start_message.id
        channel_id = ctx.channel.id
        print("Message id of bot start message is",bot_start_message_id)
        print("Channel ID is",channel_id)

        def check_setting(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⚙️"]
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout = 30.0, check = check_setting)
        except asyncio.TimeoutError:
            print("Timeout")
        else:
            if str(reaction.emoji) == "⚙️":
                mode_message = await ctx.send("⚙️ Pick a mode:\n:one: 40 seconds\n:two: 60 seconds\n:three: 90 seconds")
                await mode_message.add_reaction("1️⃣")
                await mode_message.add_reaction("2️⃣")
                await mode_message.add_reaction("3️⃣")
                mode_message_id = mode_message.id
                print("Mode message id is: ",mode_message_id)
                def check_one(reaction,user):
                    return user == ctx.author and str(reaction.emoji) in ["1️⃣","2️⃣","3️⃣"]
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout = 30.0, check = check_one)
                except asyncio.TimeoutError:
                    print("Timeout")
                else:
                    if(reaction.emoji == "1️⃣"):
                        timer = 40
                    elif(reaction.emoji == "2️⃣"):
                        timer = 60
                    elif(reaction.emoji == "3️⃣"):
                        timer = 90
                    print("The length of timer is:",timer)
                

        def check_start(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["💩"] 
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout = 30.0, check = check_start)
            print("User that reacts to poop icon:",user)
        except asyncio.TimeoutError:
            print("Timeout")
        else:
            if str(reaction.emoji) == "💩":
                print("Successfully poop")
                #start send dm to user

    @command(name='stop', alias=['dc', 'disconnect', 'quit'], help='Stop the game.')
    async def stop(self, ctx):
        # try:
        self.game.cancel()
        print('Game cancelled')

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
