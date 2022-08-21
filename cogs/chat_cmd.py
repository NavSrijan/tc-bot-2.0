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

    @commands.command(name="highlight", aliases=["hl"])
    async def highlight(self, ctx, word):
        """Get a DM if someone mentions any word
        Syntax: $highlight <word>
        """
        await ctx.reply(
            "You won't be getting highligts for long.\nUse $highlight_stop to stop getting highlights"
        )
        self.bot.highlights[ctx.author] = word

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

    @commands.command(name="joke", hidden=True)
    async def joke(self, ctx, *args):
        categories = ["Dark", "Programming", "Misc", "Pun", "Spooky", "Christmas"]
        url = "https://v2.jokeapi.dev/joke/Dark?blacklistFlags=nsfw,explicit"

        
    @commands.command(name="highlight_stop")
    async def highlight_stop(self, ctx):
        """Stop getting highlights"""
        self.bot.highlights.pop(ctx.author)
        await ctx.reply("You won't get highlights now.")

    @commands.group(aliases=['r', 'rev'])
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
                await ctx.reply(f"The chat can be revived again in {m}m, {s}s.")
        else:
            await ctx.reply(f"Head over to <#{self.vars['revive_channel']}> to revive the chat.")

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

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, *args):
        def display_av(user):
            try:
                av = user.avatar.url
            except:
                av = user.default_avatar.url
            emb = basic_embed(title=user.name, image_url=av)
            return emb
        if len(ctx.message.mentions) > 0:
            user_o = ctx.message.mentions[0]
            a = "✅"
            b = "❌"
            msg = await ctx.reply(f"{user_o.mention} Do you wish for your pfp to be enlarged?")
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
                await msg.edit(content="The user does not want their pfp to be displayed.")

        else:
            await ctx.reply(embed=display_av(ctx.message.author))

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

    @commands.command(name="state", hidden=True)
    async def state(self, ctx, *args):
        """Stereotypes, TBD"""
        try:
            state = args[0]
        except:
            await ctx.reply("No state found.")
            return

    @commands.command(name="how", aliases=["how's", "hows", "htj"])
    async def josh(self, ctx, *args):
        """JOSH!"""
        alia = [
            "how's the josh", "hows the josh?", "hows the josh",
            "how's the josh?", "htj?", "htj"
        ]
        for i in alia:
            if ctx.message.content[1:].lower().startswith(i):
                await ctx.send(
                    "https://tenor.com/view/high-sir-salute-respect-yessir-yeah-gif-15588688"
                )
                return

    @commands.command(name="slogan", aliases=["india"])
    async def slogan(self, ctx, *args):
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
        await ctx.channel.send(embed=basic_embed(title=slogan[0], desc=f"{slogan[1]}"))

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
