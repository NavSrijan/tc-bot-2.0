from discord.ext import commands
from discord import AllowedMentions, app_commands
import discord
from database import Database_members, DATABASE_URL
from functions import utc_to_ist, load, save
import datetime
import random
from helpers import basic_embed
import asyncio
from jokeapi import Jokes
from typing import Literal


class Person():

    def __init__(self, author, idd=0):
        if idd == 0:
            self.id = author.id
        else:
            self.id = idd
        self.revives_available = 3
        self.last_used = datetime.datetime.now()
        self.revives_used = 0


class Chat_commands(commands.Cog):
    """Contains chat commands"""

    def __init__(self, bot):
        self.bot = bot
        self.last_used = None
        self.vars = self.bot.config['commands']['revive']
        self.revive_delay = int(self.vars['revive_delay'])
        self.revives_available = int(self.vars['revives_available'])
        self.revive_role = int(self.vars['revive_role'])
        self.topics = load("assets/random_data/topics.pkl")
        self.alreadyDone = []
        self.one_time_revive_pass = False

    @commands.hybrid_command(name="highlight", aliases=["hl"])
    async def highlight(self, ctx, word):
        """Get a DM if someone mentions any word"""
        await ctx.reply(
            "Use $highlight_stop to stop getting highlights",
            ephemeral=True)
        self.bot.highlights[ctx.author.id] = word
        save(self.bot.highlights, "variables/highlights.pkl")

    @commands.hybrid_command(name="laser")
    async def laser(self, ctx, user: discord.Member=None):
        mo = "<:modiji:1011452564195246120>"
        las = "<:l1:1011452560147746939>"
        mol = "<:m1:1011452558444871731>"
        explode = "<a:explode:1011458958046793740>"

        if user is None:
            user = ctx.author

        text = f"{user.mention}" + ' ' * (30) + mo
        msg = await ctx.reply(text)

        for i in range(0, 6):
            await asyncio.sleep(1.5)
            text = f"{user.mention}" + ' ' * ((6 - i-1)*6) + las * i + mol
            await msg.edit(content=text)
        text = f"{explode}" + ' ' * ((6 - i-1)*6) + las * i + mol
        await msg.edit(content=text)
        await asyncio.sleep(1.5)
        text = f"{explode}" + ' ' * (30) + mo
        await msg.edit(content=text)

    @commands.hybrid_command(name="suggest")
    async def suggest(self, ctx, suggestion):
        """Suggest something reagarding the bot"""
        if ctx.interaction:
            sugg = suggestion
            thewhistler = self.bot.get_user(302253506947973130)
            emb = discord.Embed(description=sugg)
            emb.set_author(name=ctx.message.author.display_name +
                           " suggested.",
                           icon_url=ctx.message.author.avatar.url)
            emb.color = discord.Color.blurple()
            await thewhistler.send(embed=emb)
            await ctx.reply("Your suggestion has been noted.", ephemeral=True)
        else:
            sugg = ctx.message.content
            thewhistler = self.bot.get_user(302253506947973130)
            emb = discord.Embed(description=sugg)
            emb.set_author(name=ctx.message.author.display_name +
                           " suggested.",
                           icon_url=ctx.message.author.avatar.url)
            emb.color = discord.Color.blurple()
            await thewhistler.send(embed=emb)
            await ctx.reply("Your suggestion has been noted.", ephemeral=True)
            await ctx.message.delete()

    @commands.hybrid_command(name="joke")
    async def joke(self,
                   ctx,
                   category: Literal["dark", "programming", "misc", "pun",
                                     "spooky", "christmas"] = None):
        jokesapi = await Jokes()
        categories = [
            "dark", "programming", "misc", "pun", "spooky", "christmas"
        ]
        blacklist = ["nsfw", "explicit"]
        if category == None:
            joke = await jokesapi.get_joke(blacklist=blacklist)
        else:
            if category in categories:
                joke = await jokesapi.get_joke(blacklist=blacklist,
                                               category=[category])
            else:
                joke = await jokesapi.get_joke(blacklist=blacklist,
                                               search_string=category)

        if joke["type"] == "twopart":
            setup = joke["setup"]
            delivery = joke["delivery"]
            cont = f"{setup}\n||{delivery}||"
        else:
            cont = joke['joke']

        await ctx.reply(cont)

    @commands.hybrid_command(name="highlight_stop", aliases=["hl_s"])
    async def highlight_stop(self, ctx):
        """Stop getting highlights"""
        self.bot.highlights.pop(ctx.author.id)
        save(self.bot.highlights, "variables/highlights.pkl")
        await ctx.reply("You won't get highlights now.")

    @commands.hybrid_group(name="revive")
    async def revive(self, ctx):
        """Commands regarding revive chat"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @revive.command(name="chat", aliases=['c', 'ch'])
    async def chat(self, ctx):
        """Revive the chat!"""
        if ctx.channel.id == int(self.vars['revive_channel']):
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

            if (
                    msg_time - self.last_used
            ).seconds > self.revive_delay or self.last_used is None or self.one_time_revive_pass is True:
                self.one_time_revive_pass = False
                if p1.revives_available != 0:
                    await ctx.reply(
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
        else:
            await ctx.reply(
                f"Head over to <#{self.vars['revive_channel']}> to revive the chat."
            )

    @commands.hybrid_command(name="rc",
                             aliases=["revivechat", "revive_chat", "rev_chat"],
                             hidden=True)
    async def rc(self, ctx):
        """Alias for revive_chat"""
        chat_command = self.bot.get_command('revive').all_commands['chat']
        await ctx.invoke(chat_command)

    @commands.has_permissions(kick_members=True)
    @revive.command(name="reset_time", aliases=["rt"])
    async def reset_revive_time(self, ctx):
        """Resets the revive cooldown, so It can be used again."""
        self.one_time_revive_pass = True
        await ctx.reply("The revive time has been reset", ephemeral=True)

    @commands.has_permissions(kick_members=True)
    @revive.command(name="reset")
    async def reset_revives(self, ctx, user: discord.Member = None):
        """Reset the revives for a user"""
        if user != None:
            ll = [user]
        else:
            ll = [ctx.author]
        db = Database_members(DATABASE_URL, "members")
        for member in ll:
            db.resetRevivesUser(member.id)
        await ctx.reply("Done.")

    @commands.has_permissions(kick_members=True)
    @revive.command(name="count")
    async def count_revives(self, ctx, user: discord.Member = None):
        """Shows the revives left for a user"""
        if user != None:
            ll = user
        else:
            ll = [ctx.author]
        db = Database_members(DATABASE_URL, "members")
        toSend = ""
        for member in ll:
            p1 = Person(member)
            p1 = db.fetchUser(p1)
            toSend += f"{member.mention}: {p1.revives_available}" + "\n"
        await ctx.reply(toSend)

    @commands.hybrid_command(name="topic", aliases=["t"])
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
        await ctx.reply(f"`{topic}`")

    @revive.command(name="fake")
    async def fake_revive(self, ctx):
        """Revive the chat but it's fake!"""
        allowed_mentions = AllowedMentions(
            users=False,  # Whether to ping individual user @mentions
            everyone=False,  # Whether to ping @everyone or @here mentions
            roles=False,  # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
        )
        await ctx.reply(
            f"<@&{self.revive_role}> Trying to revive the chat. ||By <@{ctx.author.id}>||",
            allowed_mentions=allowed_mentions)

    @commands.hybrid_command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, user_av: discord.Member=None):

        def display_av(user):
            try:
                av = user.avatar.url
            except:
                av = user.default_avatar.url
            emb = basic_embed(title=user.name, image_url=av)
            return emb

        if ctx.interaction:
            if user_av:
                user_o = user_av
                a = "✅"
                b = "❌"
                msg = await ctx.reply(
                    f"{user_o.mention} Do you wish for your pfp to be enlarged?"
                )
                await msg.add_reaction(a)
                await msg.add_reaction(b)

                def check_reaction(reaction, user):
                    return user == user_o and reaction.emoji in [
                        a, b
                    ] and user_o.bot is False

                reaction = await self.bot.wait_for("reaction_add",
                                                   check=check_reaction,
                                                   timeout=60)
                emoji = reaction[0].emoji
                if emoji == a:
                    emb = display_av(user_o)
                    await msg.clear_reactions()
                    await msg.edit(content="", embed=emb)
                else:
                    await msg.clear_reactions()
                    await msg.edit(
                        content=
                        "The user does not want their pfp to be displayed.")

            else:
                await ctx.reply(embed=display_av(ctx.message.author))

        else:
            if user_av:
                user_o = user_av
                a = "✅"
                b = "❌"
                msg = await ctx.reply(
                    f"{user_o.mention} Do you wish for your pfp to be enlarged?"
                )
                await msg.add_reaction(a)
                await msg.add_reaction(b)

                def check_reaction(reaction, user):
                    return user == user_o and reaction.emoji in [
                        a, b
                    ] and user_o.bot is False

                reaction = await self.bot.wait_for("reaction_add",
                                                   check=check_reaction,
                                                   timeout=60)
                emoji = reaction[0].emoji
                if emoji == a:
                    emb = display_av(user_o)
                    await msg.clear_reactions()
                    await msg.edit(content="", embed=emb)
                else:
                    await msg.clear_reactions()
                    await msg.edit(
                        content=
                        "The user does not want their pfp to be displayed.")

            else:
                await ctx.reply(embed=display_av(ctx.message.author))

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="show_revives")
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
        await ctx.reply(finalMsg, allowed_mentions=allowed_mentions)

    @commands.hybrid_command(name="state", hidden=True)
    async def state(self, ctx, state):
        """Stereotypes, TBD"""
        pass

    @commands.hybrid_command(name="slogan", aliases=["india"])
    async def slogan(self, ctx):
        """SlOGAN!"""
        slogans = [
            [
                "Jai Hind",
                "The slogan “Jai Hind” was initially coined by Zain-ul Abideen Hasan, but it was adopted by Netaji Subhash Chandra Bose. It is now used as a way of salutation throughout India. It means “Victory to India” in English."
            ],
            [
                "Vande Mataram",
                "It was a poem mentioned in Bankim Chandra Chattopadhyay’s novel Anandmath. Also a journalist and activist, Chattopadhyay wrote the novel in Bengali and Sanskrit in 1882. “Vande Matram” means “I salute you, mother”."
            ],
            [
                "Swaraj Mera Janamsiddh adhikar hai, aur main ise lekar rahunga",
                "Coined by Kaka Baptista in India’s fight for independence, this slogan was adopted by Bal Gangadhar Tilak. This slogan motivated Indians to fight for independence and also invoked the feeling of love towards the nation in their hearts."
            ],
            [
                "Jai Jawaan, Jai Kisaan",
                "Given by Lal Bahadur Shastri, this slogan acknowledges and appreciates the efforts of soldiers and farmers of our country."
            ],
            [
                "Satyameva Jayate",
                "Pandit Madan Mohan Malaviya coined this slogan, and it means “truth alone triumphs”."
            ],
            [
                "Inquilab Zindabad",
                "This slogan was given by Muslim leader Hasrat Mohani. It means “Long live the revolution”. After bombing the Central Assembly in Delhi, Bhagat Singh also shouted this slogan. It turned into one of the rallying cries of Indian independence movement."
            ],
            [
                "Sarfaroshi Ki Tamanna, Ab hamare dil mein hai",
                "It’s a patriotic poem which was given by Bismil Azimabadi, and later, Ramprasad Bismil started to use it as a slogan. It urged people to fight for what’s right."
            ],
            [
                "Dushman ki goliyon ka hum samna karenge, Azad hee rahein hain, Azad hee rahenge",
                "Chandra Shekhar Azad gave this slogan after the Jallianwala Bagh Massacre happened, that led to the loss of hundreds of innocent lives."
            ],
            [
                "Araam Haraam hai",
                "This slogan was given by our former Prime Minister Jawaharlal Nehru. It reflects that our freedom fighters had no rest throughout the freedom struggle."
            ],
            [
                "Tum mujhe khoon do, mai tumhe azaadi doonga.",
                "Netaji Subhash Chandra Bose used this slogan to urge the youth to join Indian Army, and contribute to India’s fight for independence."
            ]
        ]
        slogan = random.choice(slogans)
        await ctx.channel.send(
            embed=basic_embed(title=slogan[0], desc=f"{slogan[1]}"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(embed=basic_embed(
                title="Permission Error",
                desc=
                "You don't have the permission to use this.\nIf you feel you should be using this, contact staff."
            ))
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(Chat_commands(bot))
