import platform
from lib.bot import bot

VERSION = '0.0.1'
PLATFORM = platform.system()

bot.run(version=VERSION, platform=PLATFORM)
