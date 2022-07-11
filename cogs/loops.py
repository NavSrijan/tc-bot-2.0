from discord.ext import commands, tasks
from database import Database, DATABASE_URL
from functions import load, save, utc_to_ist
import datetime
import os

class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dumpMessagesFromDatabaseToPKL.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

    @commands.has_permissions(kick_members=True)
    @commands.command(name="reset")
    async def reset(self, ctx):
        if ctx.message.content == "reset word_count":
            db = Database(DATABASE_URL, "members")
            db.resetMessagesCount()
            await ctx.reply("DONE!")

    @tasks.loop(time=datetime.time(18, 25))
    async def dumpMessagesFromDatabaseToPKL(self):
        print("Dumping messages from database")
        db = Database(DATABASE_URL, "members")
        # Storing
        all_users = db.get_messages_lb(to_send=False)
        date = utc_to_ist(datetime.datetime.utcnow()).date()

            ## Trying to retrieve previously stored data.
        try:
            p_data = load("word_count.pkl")
            try:
                todays_data = p_data[date]
            except:
                p_data[date] = {}
                todays_data = p_data[date]
            for i in all_users:
                try:
                    todays_data[int(i[0])]+=int(i[1])
                except:
                    todays_data[int(i[0])] = int(i[1])
            p_data[date] == todays_data
        except:
            p_data = {}
            try:
                todays_data = p_data[date]
            except:
                p_data[date] = {}
                todays_data = p_data[date]
            for i in all_users:
                try:
                    todays_data[int(i[0])]+=int(i[1])
                except:
                    todays_data[int(i[0])] = int(i[1])
            p_data[date] == todays_data
        save(p_data, "word_count.pkl")


        # Resetting
        db.resetMessagesCount()

        channel = self.bot.get_channel(int(os.environ['logs_channel']))
        await channel.send("Resetting the messages count for the day.")

        channel = self.bot.get_channel(int(os.environ['mods_channel']))
        msg_to_send = db.get_messages_lb()
        await channel.send(msg_to_send)


async def setup(bot):
    await bot.add_cog(Loops(bot))