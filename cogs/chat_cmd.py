from discord.ext import commands
from discord import AllowedMentions
import discord
from database import Database_members, DATABASE_URL
from functions import utc_to_ist, load, save
import datetime
import random
from helpers import basic_embed
import os


class Person():

    def __init__(self, author, idd=0):
        if idd == 0:
            self.id = author.id
        else:
            self.id = idd
        self.revives_available = int(os.environ["revives_available"])
        self.last_used = datetime.datetime.now()
        self.revives_used = 0


class Chat_commands(commands.Cog):
    """Contains chat commands"""

    def __init__(self, bot):
        self.bot = bot
        self.last_used = None
        self.revive_delay = int(os.environ['revive_delay'])
        self.revives_available = int(os.environ['revives_available'])
        self.revive_role = int(os.environ['revive_role'])
        self.topics = load("assets/random_data/topics.pkl")
        self.alreadyDone = []

    #@commands.command(name="highlight")
    #async def highlight(self, ctx, word):
    #    """Get a DM if someone mentions any word
    #    Syntax: $highlight <word>
    #    """
    #    await ctx.reply(
    #        "You won't be getting highligts for long.\nUse $highlight_stop to stop getting highlights"
    #    )
    #    self.bot.highlights[ctx.author] = word

    @commands.command(name="suggest")
    async def suggest(self, ctx, *args):
        """Suggest something reagarding the bot"""
        sugg = " ".join(args)
        thewhistler = self.bot.get_user(302253506947973130)
        emb = discord.Embed(description=sugg)
        emb.set_author(name=ctx.message.author.display_name + " suggested.",
                       icon_url=ctx.message.author.avatar.url)
        emb.color = discord.Color.blurple()
        await thewhistler.send(embed=emb)
        await ctx.reply("Your suggestion has been noted.")
        await ctx.message.delete()

    #@commands.command(name="highlight_stop")
    #async def highlight_stop(self, ctx):
    #    """Stop getting highlights"""
    #    self.bot.highlights.pop(ctx.author)
    #    await ctx.reply("You won't get highlights now.")

    @commands.group(aliases=['r', 'rev'])
    async def revive(self, ctx):
        """Commands regarding revive chat"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @revive.command(name="chat", aliases=['c', 'ch'])
    async def chat(self, ctx):
        """Revive the chat!"""
        if ctx.channel.id == int(os.environ["revive_channel"]):
            db = Database_members(DATABASE_URL, "members")
            p1 = Person(ctx.message.author)
            msg_time = utc_to_ist(ctx.message.created_at)
            if len(self.topics) != 0:
                topic = random.choice(self.topics)
                self.alreadyDone.append(
                    self.topics.pop(self.topics.index(topic)))
            else:
                self.topics = self.alreadyDone
                self.alreadyDone = []
                topic = random.choice(self.topics)
                self.alreadyDone.append(
                    self.topics.pop(self.topics.index(topic)))

            try:
                dateLast = load("variables/date_last.pkl")
            except:
                dateLast = datetime.datetime.today().date()
                db.resetRevives()
                save(dateLast, "variables/date_last.pkl")
            if dateLast < datetime.datetime.today().date():
                dateLast = datetime.datetime.today().date()
                db.resetRevives()
                save(dateLast, "variables/date_last.pkl")

            # Loading or saving the user
            try:
                p1 = (db.fetchUser(p1))
            except:
                db.addMember(p1)

            try:
                self.last_used = load("variables/last_revive_time.pkl")
                p1.last_used = self.last_used
            except:
                self.last_used = utc_to_ist(datetime.datetime.utcnow())

            if (msg_time - self.last_used
                ).seconds > self.revive_delay or self.last_used is None:
                if p1.revives_available != 0:
                    await ctx.channel.send(
                        f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||\n`{topic}`"
                    )
                    save(msg_time, "variables/last_revive_time.pkl")
                    p1.revives_available -= 1
                    db.updateMember(p1)
                else:
                    await ctx.reply("You have used all your revives today.")
            else:
                last = (msg_time - self.last_used).seconds
                timeLeft = self.revive_delay - last
                m, s = divmod(timeLeft, 60)
                await ctx.reply(f"The chat can be revived again in {m}m, {s}s."
                                )

    @commands.command(name="rc",
                      aliases=["revivechat", "revive_chat", "rev_chat"],
                      hidden=True)
    async def rc(self, ctx):
        chat_command = self.bot.get_command('revive').all_commands['chat']
        await ctx.invoke(chat_command)

    @commands.has_permissions(kick_members=True)
    @revive.command(name="reset_time", aliases=["rt"])
    async def reset_revive_time(self, ctx):
        """Resets the revive cooldown, so It can be used again."""
        self.last_used = None
        await ctx.reply("The revive time has been reset")

    @commands.has_permissions(kick_members=True)
    @revive.command(name="reset")
    async def reset_revives(self, ctx):
        """Reset the revives for a user"""
        if len(ctx.message.mentions) > 1:
            ll = ctx.message.mentions
        else:
            ll = [ctx.author]
        db = Database_members(DATABASE_URL, "members")
        for member in ll:
            db.resetRevivesUser(member.id)
        await ctx.reply("Done.")

    @commands.has_permissions(kick_members=True)
    @revive.command(name="count")
    async def count_revives(self, ctx):
        """Shows the revives left for a user"""
        if len(ctx.message.mentions) > 1:
            ll = ctx.message.mentions
        else:
            ll = [ctx.author]
        db = Database_members(DATABASE_URL, "members")
        toSend = ""
        for member in ll:
            p1 = Person(member)
            p1 = db.fetchUser(p1)
            toSend += f"{member.mention}: {p1.revives_available}" + "\n"
        await ctx.reply(toSend)

    @commands.command(name="topic", aliases=["t"])
    async def topic(self, ctx):
        """Sends a random topic to discuss upon."""
        if len(self.topics) != 0:
            topic = random.choice(self.topics)
            self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))
        else:
            self.topics = self.alreadyDone
            self.alreadyDone = []
            topic = random.choice(self.topics)
            self.alreadyDone.append(self.topics.pop(self.topics.index(topic)))
        await ctx.message.channel.send(f"`{topic}`")

    @revive.command(name="fake")
    async def fake_revive(self, ctx):
        """Revive the chat but it's fake!"""
        allowed_mentions = AllowedMentions(
            users=False,  # Whether to ping individual user @mentions
            everyone=False,  # Whether to ping @everyone or @here mentions
            roles=False,  # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
        )
        await ctx.message.channel.send(
            f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||",
            allowed_mentions=allowed_mentions)

    @commands.has_permissions(kick_members=True)
    @commands.command(name="show_revives")
    async def show_revives(self, ctx):
        """Shows the number of revives each person has left."""
        db = Database_members(DATABASE_URL, "members")

        allowed_mentions = AllowedMentions(
            users=False,  # Whether to ping individual user @mentions
            everyone=False,  # Whether to ping @everyone or @here mentions
            roles=False,  # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
        )

        finalMsg = """"""
        chunk = "<@{}>: {}, {}"
        all = db.viewAllUsers()

        for i in all:
            finalMsg += chunk.format(i[0], i[1], i[3]) + "\n"
        await ctx.message.reply(finalMsg, allowed_mentions=allowed_mentions)

    @commands.command(name="state")
    async def state(self, ctx, *args):
        try:
            state = args[0]
        except:
            await ctx.reply("No state found.")
            return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(embed=basic_embed(
                title="Permission Error",
                desc="You don't have the permission to use this.\nIf you feel you should be using this, contact staff."
            ))
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(Chat_commands(bot))
