from discord.ext import commands, tasks
from discord import AllowedMentions
from database import Database, DATABASE_URL
from functions import utc_to_ist, load, save
from datetime import datetime

import os

class Person():
    def __init__(self, author, revives_available,  idd=0):
        if idd==0:
            self.id = author.id
        else:
            self.id = idd
        self.revives_available = revives_available
        self.last_used = None
        self.revives_used = 0

class Revive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_used = None
        self.revive_delay = int(os.environ['revive_delay'])
        self.revives_available = int(os.environ['revives_available'])
        self.revive_role = int(os.environ['revive_role'])

    @commands.command(name="revive")
    async def revive(self, ctx):
        if ctx.message.content == "revive chat" and ctx.channel.id == int(os.environ["revive_channel"]):
            db = Database(DATABASE_URL, "members")
            p1 = Person(ctx.message.author, self.revives_available)
            msg_time = utc_to_ist(ctx.message.created_at)
            
            try:
                dateLast = load("date_last.pkl")
            except:
                dateLast = datetime.today().date()
                db.resetRevives()
                save(dateLast, "date_last.pkl")
            if dateLast<datetime.today().date():
                dateLast=datetime.today().date()
                db.resetRevives()
                save(dateLast, "date_last.pkl")

            #Loading or saving the user
            try:
                p1 = (db.fetchUser(p1))
            except:
                db.addMember(p1)

            try:
                self.last_used = load("last_revive_time.pkl")
                p1.last_used = self.last_used
            except:
                self.last_used = utc_to_ist(datetime.utcnow())

            if (msg_time - self.last_used).seconds > self.revive_delay or self.last_used == None:
                if p1.revives!=0:
                    await ctx.channel.send(f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||")
                    save(msg_time, "last_revive_time.pkl")
                    p1.revives-=1
                    db.updateMember(p1)
                else:
                    await ctx.reply("You have used all your revives today.")
            else:
                last = (msg_time - self.last_used).seconds
                timeLeft = self.revive_delay-last
                m, s = divmod(timeLeft, 60)
                await ctx.reply(f"The chat can be revived again in {m}m, {s}s.")
        
        
    @commands.command(name="yo")
    async def yoyo(self, ctx):
        await ctx.reply("yoyo")

    @commands.command(name="yo")
    async def yoyo(self, ctx):
        allowed_mentions=AllowedMentions(
        users=False,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
        replied_user=False,  # Whether to ping on replies to messages
        )
        await message.channel.send(f"<@&{reviveRole}> Trying to revive the chat. ||By <@{message.author.id}>||", allowed_mentions=allowed_mentions)

    @commands.has_permissions(kick_members=True)
    @commands.command(name="lb")
    async def yoyo(self, ctx):
        db = Database(DATABASE_URL, "members")
        await ctx.channel.send(db.get_messages_lb())

    @tasks.loop(time=datetime.strptime("00:00:00", "%H:%M:%S").time())
    async def dumpMessagesFromDatabaseToPKL(self, ctx):
        db = Database(DATABASE_URL, "members")
        db.resetMessagesCount()

        channel = self.bot.get_channel(int(os.environ['logs_channel']))
        channel.send("Resetting the messages count for the day.")

        channel = self.bot.get_channel(int(os.environ['mods_channel']))
        msg_to_send = db.get_messages_lb()
        channel.send(msg_to_send)

async def setup(bot):
    await bot.add_cog(Revive(bot))