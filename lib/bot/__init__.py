import os
import platform

from asyncio import sleep
from datetime import datetime
from glob import glob

from discord import Intents
from discord import Embed
from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import CommandNotFound, Context
from dotenv import load_dotenv

# from ..db import db

load_dotenv()

DEFAULT_PREFIX = '!'
OWNER_IDS = [596641174236692491, 619607278382874675]
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_TOKEN')
PLATFORM = platform.system()

COGS = [path.split('\\')[-1][:-3] for path in glob('./lib/cogs/*.py')] if PLATFORM == 'Windows' \
    else [path.split('/')[-1][:-3] for path in glob('./lib/cogs/*.py')]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} is ready.')

    def all_ready(self):
        return all(getattr(self, cog) for cog in COGS)


class Bot(BaseBot):
    def __init__(self):
        self.platform = PLATFORM
        self.prefix = DEFAULT_PREFIX
        self.guild = None
        self.ready = False
        self.cogs_ready = Ready()
        self.version = '0.0.0'
        self.default_channel = None
        self.welcome_message = None
        super().__init__(
            command_prefix=DEFAULT_PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def run(self, version):
        self.version = version
        print('Gearing up Kagari...')
        self.setup()
        print('Deploying Kagari...')
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
            self.welcome_message.set_author(name=f'{self.user.name}-chan', icon_url=self.user.avatar_url)
            self.welcome_message.set_image(url=self.user.avatar_url)

            self.ready = True
            print(f'{self.user.name}-chan is ready UwU')

            await self.default_channel.send(embed=self.welcome_message)
        else:
            print(f'{self.user.name}-chan is reconnected OwO')

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
        # raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass
        elif hasattr(exc, 'original'):
            raise exc.original
        else:
            raise exc

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)
        else:
            await ctx.send('I am not ready yet')


bot = Bot()
