from bot import bot
import keep_alive as alive

VERSION = '0.0.4'

# Keep the server alive 24/7
alive.keep_alive()
bot.run(version=VERSION)
