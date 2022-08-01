from discord.ext import commands
import discord
import os
from helpers import PersistentView, VoteView
from database import Database_suggestions, DATABASE_URL
import ipdb

class Suggestion(commands.Cog):
    """Suggestions"""
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(VoteView())

    @commands.command(name="tt")
    async def tt(self, ctx):
        await ctx.send("This message has buttons!", view=PersistentView())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)



async def setup(bot):
    await bot.add_cog(Suggestion(bot))