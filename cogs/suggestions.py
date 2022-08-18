from discord.ext import commands
import discord
import os
from helpers import PersistentView, VoteView, VoteViewForEmoji
from database import Database_suggestions, DATABASE_URL


class Suggestion(commands.Cog):
    """Suggestions"""

    def __init__(self, bot):
        self.bot = bot
        bot.add_view(VoteView())
        bot.add_view(VoteViewForEmoji())

    @commands.command(name="tt", hidden=True)
    async def tt(self, ctx):
        await ctx.send("This message has buttons!", view=PersistentView())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(Suggestion(bot))
