from discord.ext import commands, tasks
from discord import AllowedMentions
from database import Database_members, DATABASE_URL
from functions import utc_to_ist, load, save
import datetime
import random
import pdb

import os

class Person():
    def __init__(self, author, idd=0):
        if idd==0:
            self.id = author.id
        else:
            self.id = idd
        self.revives_available = int(os.environ["revives_available"])
        self.last_used = datetime.datetime.now()
        self.revives_used = 0

class Revive(commands.Cog):
    """Contains chat revive commands"""
    def __init__(self, bot):
        self.bot = bot
        self.last_used = None
        self.revive_delay = int(os.environ['revive_delay'])
        self.revives_available = int(os.environ['revives_available'])
        self.revive_role = int(os.environ['revive_role'])
        self.topics = load("assets/random_data/topics.pkl")
        self.alreadyDone = []

    @commands.command(name="revive")
    async def revive(self, ctx, *args):
        """Revive the chat!"""
        if args[0]=="chat" and ctx.channel.id == int(os.environ["revive_channel"]):
            db = Database_members(DATABASE_URL, "members")
            p1 = Person(ctx.message.author)
            msg_time = utc_to_ist(ctx.message.created_at)
            
            if len(self.topics)!=0:
                topic = random.choice(self.topics)
                self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))
            else:
                self.topics = self.alreadyDone
                self.alreadyDone = []
                topic = random.choice(self.topics)
                self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))

            try:
                dateLast = load("variables/date_last.pkl")
            except:
                dateLast = datetime.datetime.today().date()
                db.resetRevives()
                save(dateLast, "variables/date_last.pkl")
            if dateLast<datetime.datetime.today().date():
                dateLast=datetime.datetime.today().date()
                db.resetRevives()
                save(dateLast, "variables/date_last.pkl")

            #Loading or saving the user
            try:
                p1 = (db.fetchUser(p1))
            except:
                db.addMember(p1)

            try:
                self.last_used = load("variables/last_revive_time.pkl")
                p1.last_used = self.last_used
            except:
                self.last_used = utc_to_ist(datetime.datetime.utcnow())

            if (msg_time - self.last_used).seconds > self.revive_delay or self.last_used == None:
                if p1.revives_available!=0:
                    await ctx.channel.send(f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||\n`{topic}`")
                    save(msg_time, "variables/last_revive_time.pkl")
                    p1.revives_available-=1
                    db.updateMember(p1)
                else:
                    await ctx.reply("You have used all your revives today.")
            else:
                last = (msg_time - self.last_used).seconds
                timeLeft = self.revive_delay-last
                m, s = divmod(timeLeft, 60)
                await ctx.reply(f"The chat can be revived again in {m}m, {s}s.")
        
    @commands.command(name="topic")
    async def topic(self, ctx):
        """Sends a random topic to discuss upon."""
        if len(self.topics)!=0:
            topic = random.choice(self.topics)
            self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))
        else:
            self.topics = self.alreadyDone
            self.alreadyDone = []
            topic = random.choice(self.topics)
            self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))
        await ctx.message.channel.send(f"`{topic}`")

    @commands.command(name="fake")
    async def fake_revive(self, ctx):
        """Revive the chat but it's fake!"""
        if ctx.message.content == "fake revive":
            allowed_mentions=AllowedMentions(
            users=False,         # Whether to ping individual user @mentions
            everyone=False,      # Whether to ping @everyone or @here mentions
            roles=False,         # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
            )
            await ctx.message.channel.send(f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||", allowed_mentions=allowed_mentions)

    @commands.has_permissions(kick_members=True)
    @commands.command(name="show_revives")
    async def show_revives(self, ctx):
        """Shows the number of revives each person has left."""
        db = Database_members(DATABASE_URL, "members")
        p1 = Person(ctx.message.author)

        allowed_mentions=AllowedMentions(
        users=False,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
        replied_user=False,  # Whether to ping on replies to messages
        )

        finalMsg = """"""
        chunk = "<@{}>: {}, {}"
        all = db.viewAllUsers()

        for i in all:
            finalMsg+=chunk.format(i[0], i[1], i[3])+"\n"
        await ctx.message.reply(finalMsg, allowed_mentions=allowed_mentions)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #await ctx.message.reply(error)
            print(error)

async def setup(bot):
    await bot.add_cog(Revive(bot))
