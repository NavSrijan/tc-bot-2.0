from discord.ext import commands
from database import DB_messages, DATABASE_URL
import os
import pdb

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)


    @commands.has_permissions(kick_members=True)
    @commands.command(name="lb")
    async def yoyo(self, ctx):
        db = DB_messages(DATABASE_URL, "message_bank")
        await ctx.channel.send(db.get_data(num=10))

async def setup(bot):
    await bot.add_cog(Counting(bot))