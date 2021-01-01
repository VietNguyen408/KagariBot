import os
import asyncio
from datetime import datetime
from random import choice, shuffle

from dotenv import load_dotenv
from discord import Embed
from discord.ext import tasks
from discord.abc import PrivateChannel
from discord.ext.commands import Cog, command
from discord import Embed, ClientException
from discord.utils import get

from ..db.db import question_db

DEFAULT_TIMER = 60
BETWEEN_STAGES_TIME = 15
IMPOSTOR_IMG_URL = 'https://staticg.sportskeeda.com/editor/2020/09/340fd-16010530499727-800.jpg'
VOTING_EMOJI = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣')


class KurryGame:
    def __init__(self, ctx, bot, voice, timer):
        self.ctx = ctx
        self.bot = bot
        self.voice = voice
        self.timer = timer
        self.guild_id = ctx.guild.id
        self.channel = ctx.channel
        self.topic_pool = [topic for topic in question_db.find()]

    async def change_timer(self, new_timer):
        self.timer = new_timer

    async def send_topic_to_players(self, member_list, topic1, topic2):
        for index, member in enumerate(member_list):
            if not member.bot:
                if index == 0:
                    await member.send(topic1)
                else:
                    await member.send(topic2)
        await self.channel.send(('\n**The round has begin!**\n'
                                f'You have {self.timer} seconds '
                                'to discuss and find out who has the unique topic.'))

    async def send_voting_board(self, member_list, topic1, topic2):
        shuffle(member_list)
        voting_board = Embed(title='Voting time!', color=0xE8290B,
                            timestamp=datetime.utcnow())
        voting_board.set_author(
            name=f'{self.bot.user.name}-chan', icon_url=self.bot.user.avatar_url)
        voting_board.description = 'Who will you vote against?\n'
        for i, member in enumerate(member_list):
            voting_board.description += f'{VOTING_EMOJI[i]} {member.display_name}\n'
        msg = await self.channel.send(embed=voting_board)
        for i in range(len(member_list)):
            await msg.add_reaction(VOTING_EMOJI[i])

    async def send_round_result(self, member_list, topic1, topic2):
        round_result = Embed(title='Round result!', color=0xE8290B,
                            timestamp=datetime.utcnow())
        round_result.set_author(
            name=f'{self.bot.user.name}-chan', icon_url=self.bot.user.avatar_url)
        round_result.set_image(url=IMPOSTOR_IMG_URL)
        round_result.description = f'Everyone got \'{topic2}\'!'
        round_result.description += f'\nBut {member_list[0].display_name} got \'{topic1}\'!'
        await self.channel.send(embed=round_result)

    async def game_round(self):
        while True:
            member_list = self.voice.members
            member_list = list(
                filter(lambda member: not member.bot, member_list))
            shuffle(member_list)
            topic = choice(self.topic_pool)
            topic1 = topic['topic1']
            topic2 = topic['topic2']
            self.topic_pool.remove(topic)
            print((topic1, topic2))

            # Wait for the round to finish...
            await self.send_topic_to_players(member_list, topic1, topic2)
            await asyncio.sleep(self.timer)

            # Print the voting board
            await self.send_voting_board(member_list, topic1, topic2)
            await asyncio.sleep(BETWEEN_STAGES_TIME)

            # Print the result board
            await self.send_round_result(member_list, topic1, topic2)
            await asyncio.sleep(BETWEEN_STAGES_TIME)


class Game(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_voice_client = None
        self.leave_vc_if_alone.start()
        self.game = None

    def cog_unload(self):
        self.leave_vc_if_alone.cancel()

    async def start_new_game(self, ctx, timer):
        author = ctx.message.author
        await ctx.send(f'Hello {author.mention}!')
        if not ctx.message.author.voice:
            await ctx.send('You have to be in a public voice channel to start a game!')
            return
        game_channel = ctx.message.author.voice.channel
        if self.current_voice_client:
            await self.leave_voice_channel()
        self.current_voice_client = await game_channel.connect()

        kurry_game = KurryGame(
            ctx=ctx, bot=self.bot, voice=game_channel, timer=timer)
        self.game = asyncio.ensure_future(kurry_game.game_round())

    @command(name='rule', help='Display the rules for the game.')
    async def tutorial(self, ctx):
        await ctx.send(('**This is the rule of Kurry game:**\n'
                        '> - I will give each one of you guys a card that has a word on it.\n'
                        '> - Everyone has the the card with the same word except the impostor.\n'
                        '> - You have a set amount of time to discussion with your friends to find the impostor.\n'
                        '> - After that seconds, you will have to vote for the suspect.\n'
                        '> - If the one who get the most vote is the impostor you guy win, otherwise the impostor win.'))

    @command(name='kurry', aliases=['start', 'yasuo', 'play'], help='Start a new game.')
    async def kurry(self, ctx):
        timer = DEFAULT_TIMER
        mode_message = await ctx.send('Need at least 3 players\n\n'
                                    ':gear: Pick a mode:\n'
                                    '1️⃣ 40 seconds\n'
                                    '2️⃣ 60 seconds\n'
                                    '3️⃣ 90 seconds')
        await mode_message.add_reaction("1️⃣")
        await mode_message.add_reaction("2️⃣")
        await mode_message.add_reaction("3️⃣")

        def check_one(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"]
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check_one)
        except asyncio.TimeoutError:
            print("Timeout.")
            return
        else:
            if(reaction.emoji == "1️⃣"):
                timer = 40
            elif(reaction.emoji == "2️⃣"):
                timer = 60
            elif(reaction.emoji == "3️⃣"):
                timer = 90
            print("The length of timer is:", timer)

        bot_join_message = await ctx.send("💩 Start game")
        await bot_join_message.add_reaction("💩")

        def check_start(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["💩"]
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check_start)
        except asyncio.TimeoutError:
            print("Timeout.")
            return
        else:
            if str(reaction.emoji) == "💩":
                await self.start_new_game(ctx=ctx, timer=timer)

    @command(name='stop', aliases=['dc', 'disconnect', 'quit'], help='Stop the current game.')
    async def stop(self, ctx):
        self.game.cancel()
        await ctx.send('Game cancelled.')
        await self.current_voice_client.disconnect()

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
