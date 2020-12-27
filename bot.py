import os
import sys
import platform
import traceback

from asyncio import sleep
from datetime import datetime
from glob import glob

import discord
from discord import Intents
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from dotenv import load_dotenv

from lib.db.db import prefix_db

load_dotenv()

OWNER_IDS = [596641174236692491, 619607278382874675]
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_TOKEN')
PREFIX = os.getenv('DEFAULT_PREFIX')
PLATFORM = platform.system()

COGS = [path.split('\\')[-1][:-3] for path in glob('./lib/cogs/*.py')] if PLATFORM == 'Windows' \
    else [path.split('/')[-1][:-3] for path in glob('./lib/cogs/*.py')]
if '__init__' in COGS:
    COGS.remove('__init__')


async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        custom_prefix = prefix_db.find_one({'guild_id': guild.id})
        return custom_prefix['prefix'] if custom_prefix else PREFIX
    else:
        return PREFIX


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} is ready.')

    def all_ready(self):
        return all(getattr(self, cog) for cog in COGS)


class KagariBot(Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True)
        self.platform = PLATFORM
        self.guild = None
        self.ready = False
        self.cogs_ready = Ready()
        self.version = '0.0.0'
        self.default_channel = None
        self.welcome_message = None
        super().__init__(
            command_prefix=determine_prefix,
            owner_ids=OWNER_IDS,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=Intents.all(),
        )

    def run(self, version):
        self.version = version
        print('Gearing up Kagari...  (run - b4 setup)')
        self.setup()
        print('Deploying Kagari...  (run - after setup')
        super().run(TOKEN)

    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f'{cog} cog loaded.')

        print('Gear up completed.')

    async def on_connect(self):
        print(f'{self.user.name}-chan has connected to Discord!')

    async def on_disconnect(self):
        print(f'{self.user.name}-chan has disconnected from Discord :(')

    async def on_ready(self):
        if not self.ready:
            self.default_channel = self.get_channel(785613761967816774)
            self.guild = self.get_guild(int(GUILD))

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.welcome_message = Embed(title='Sky Striker Mobilize - Engage!',
                                         description='Kagari-chan has been deployed.',
                                         color=0xE8290B,
                                         timestamp=datetime.utcnow())
            self.welcome_message.set_author(
                name=f'{self.user.name}-chan', icon_url=self.user.avatar_url)
            self.welcome_message.set_image(url=self.user.avatar_url)

            self.ready = True
            print(f'{self.user.name}-chan is ready UwU  (on_ready)')

            await self.default_channel.send(embed=self.welcome_message)
        else:
            print(f'{self.user.name}-chan is reconnected OwO  (on_ready)')

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}',
                      file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        if ctx.command is None or ctx.guild is None:
            return

        if self.ready:
            await self.invoke(ctx)
        else:
            await ctx.send('I am not ready yet.')


bot = KagariBot()
