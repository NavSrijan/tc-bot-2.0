from discord.ext import commands, tasks
from database import Database, DATABASE_URL
import datetime
import os
import pdb

class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dumpMessagesFromDatabaseToPKL.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
    
    @tasks.loop(time=datetime.time(9, 18)) 
    async def dumpMessagesFromDatabaseToPKL(self):
        #db = Database(DATABASE_URL, "members")
        #db.resetMessagesCount()
#
        #channel = self.bot.get_channel(int(os.environ['logs_channel']))
        #channel.send("Resetting the messages count for the day.")
#
        print("ENTERED")
        channel = self.bot.get_channel(int(os.environ['mods_channel']))
        msg_to_send = db.get_messages_lb()
        await channel.send(msg_to_send)

async def setup(bot):
    await bot.add_cog(Loops(bot))