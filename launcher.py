from lib.bot import bot

VERSION = '0.0.1'


# @bot.command(name='start')
# async def start(ctx):
#     guild = ctx.guild
#     author = ctx.message.author
#     await ctx.send(f'Hello {author.mention}!')
#     if not ctx.message.author.voice:
#         await ctx.send('You have to be in a voice channel to start a game!')
#         return
#     game_channel = ctx.message.author.voice.channel
#     await game_channel.connect()


bot.run(version=VERSION)
