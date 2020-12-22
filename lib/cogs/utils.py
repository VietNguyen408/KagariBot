from discord.ext.commands import Cog
from discord.ext.commands import command

from lib.db.db import prefix_db


class Utils(Cog):
    def __init__(self, bot):
        self.bot = bot

    # !prefix [new-prefix] to change prefix for the server
    @command(name='prefix', help='Change command prefix')
    async def set_prefix(self, ctx, *prefix: str):
        guild = ctx.guild
        if not guild:
            return
        if not prefix:
            await ctx.send("""
Please add an additional argument. For example: 
> !prefix ?   
to change the prefix to ?
		""")
        else:
            current_prefix = prefix_db.find_one({'guild_id': guild.id})
            if current_prefix:
                prefix_db.update_one(
                    {'guild_id': guild.id},
                    {'$set': {
                        'prefix': prefix[0]
                    }}
                )
            else:
                new_entry = {
                    'guild_id': guild.id,
                    'prefix': prefix[0]
                }
                prefix_db.insert_one(new_entry)
            await ctx.send(f'Prefix changed to {prefix[0]}')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("utils")

    # @Cog.listener()
    # async def on_message(self):
    #     pass


def setup(bot):
    bot.add_cog(Utils(bot))
