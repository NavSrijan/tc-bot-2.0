import asyncio
import datetime
import random
from typing import Literal
import ipdb

import discord
from discord import AllowedMentions, app_commands
from discord.ext import commands
from jokeapi import Jokes
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from database import DATABASE_URL, Database_members
from database_2 import Message_Logs, Synergy, Birthday
from functions import load, save, utc_to_ist, MorseCode
from helpers import basic_embed, get_percentage_image
import aiohttp


class Chat_commands(commands.Cog):
    """Contains chat commands"""

    def __init__(self, bot):
        self.bot = bot
        self.last_used = None
        self.topics = load("assets/random_data/topics.pkl")
        self.last_revive_used = None
        self.alreadyDone = []

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.hybrid_command(name="synergy", aliases=['syn'])
    async def synergy(self,
                      ctx,
                      user1: discord.Member = None,
                      user2: discord.Member = None):

        ml = Message_Logs()
        if user1 is None:
            user1 = ctx.author
            random_user_id = random.choice(ml.random_active_user())[0]
            user2 = ctx.bot.get_user(random_user_id)
        elif user1 is not None and user2 is None:
            user2, user1 = user1, ctx.author
        tries = 0
        while True:
            try:
                if tries > 5:
                    return
                tries += 1
                syn = Synergy(user1.id, user2.id)
                break
            except:
                random_user_id = random.choice(ml.random_active_user())[0]
                user2 = ctx.bot.get_user(random_user_id)
        emb = discord.Embed(
            color=discord.Color.from_str("#e81538"),
            title=user1.name[:3] + user2.name[-3:],
            description=
            f"Wanna see how {user1.mention}'s 'synergy with {user2.mention} is?\nHere we go!"
        )

        try:
            av_1 = user1.avatar.url
        except:
            av_1 = user1.default_avatar.url
        try:
            av_2 = user2.avatar.url
        except:
            av_2 = user2.default_avatar.url

        emb.set_thumbnail(url=av_1)

        file, filename = get_percentage_image(round(syn.final_score))
        msg = await ctx.message.reply(embed=emb)

        common_words = ", ".join(syn.step_1_data['words'])

        common_emojis_final = []
        for i in syn.step_4_data['common_emojis']:
            common_emojis_final.append(i[0])

        desc_1 = f"""

        >>> Your use of words are `{round(syn.step_1_data['score'], 2)}%` similar.
        Most common words used by both are: `{common_words}`


        """
        desc_2 = f"""
        You are active together `{round(syn.step_2_data['score'], 2)}%` of the times.
        Common Hours: `{" ,".join(str(x) for x in syn.step_2_data['common_hours'])}`
        Common Days : `{" ,".join(str(x) for x in syn.step_2_data['common_days'])}`. 


        """
        desc_3 = f"""
        Your mention score is `{round(syn.step_3_data['score'], 2)}%`.
        This shows how much you guys mention each other.


        """
        desc_4 = f"""
        You use `{round(syn.step_4_data['score'], 2)}%` of the emojis which are same.
        Common emojis: {" ".join(common_emojis_final[:6])}


        """
        desc_5 = f"""
        Your `{round(syn.step_5_data['score'], 2)}%` of the messages are of similar length.


        """
        desc_6 = f"""
        YOUR FINAL SCORE IS
        """

        descs = [desc_1, desc_2, desc_3, desc_4, desc_5]

        for i in descs:
            await asyncio.sleep(1)

            emb.description += i
            await msg.edit(embed=emb)

        if syn.final_score < 30:
            emb.color = discord.Color.from_str("#3da813")
            await msg.edit(embed=emb)

        await ctx.send(file=file)

        del ml

    @commands.hybrid_command(name="wordcloud", aliases=["wc"])
    async def word_cloud(self, ctx, user: discord.Member = None):
        """Generates a word cloud"""
        # select unnest(string_to_array(content, ' ')) AS parts, COUNT(*) AS cnt from message_logs WHERE user_id= GROUP BY parts ORDER BY cnt DESC;
        if user is None:
            user = ctx.author
        messages = self.bot.message_logs.fetch_messages(user.id)
        ll = []
        for i in messages:
            k = i[0]
            if k.startswith("http"):
                continue
            ll.append(k.lower())
        text = " ".join(ll)
        wordcloud = WordCloud(
            width=1080,
            height=1080,
            background_color='white',
        ).generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("wc.png", dpi=300)
        # plt.show()
        file = discord.File(fp='wc.png', filename='wc.png')
        await ctx.reply(file=file)
        
    @commands.hybrid_command(name="line_equation")
    async def line_equation(self, ctx, x1:int, y1:int, x2:int, y2:int):
        slope = (y2-y1)/(x2-x1)
        eq = f"**(y-{y1})={slope}*(x-{x1})**"
        await ctx.reply(f"The equation of the line is {eq}")

    @commands.hybrid_command(name="highlight", aliases=["hl"], enabled=False)
    async def highlight(self, ctx, word):
        """Get a DM if someone mentions any word"""
        await ctx.reply("Use $highlight_stop to stop getting highlights",
                        ephemeral=True)
        self.bot.highlights[ctx.author.id] = word
        save(self.bot.highlights, "variables/highlights.pkl")

    @commands.hybrid_command(name="laser")
    async def laser(self, ctx, user: discord.Member = None):
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
            text = f"{user.mention}" + ' ' * ((6 - i - 1) * 6) + las * i + mol
            await msg.edit(content=text)
        text = f"{explode}" + ' ' * ((6 - i - 1) * 6) + las * i + mol
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

    @commands.hybrid_group(name="morse")
    async def morse(self, ctx):
        """Commands regarding Morse code"""
        if ctx.invoked_subcommand is None:
            await ctx.reply("Not a valid command", delete_after=5)

    @morse.command(name="encrypt")
    async def encrypt_morse(self, ctx, text):
        mor = MorseCode()
        await ctx.reply(mor.encrypt(text))

    @morse.command(name="decrypt")
    async def decrypt_morse(self, ctx, text):
        mor = MorseCode()
        await ctx.reply(mor.decrypt(text))

    @commands.hybrid_group(name="revive", enabled=False)
    async def revive(self, ctx):
        """Commands regarding revive chat"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @revive.command(name="chat", aliases=['c', 'ch'], enabled=False)
    async def chat(self, ctx):
        """Revive the chat!"""
        if ctx.channel.id == self.bot.config['commands']['revive'][
                'revive_channel']:
            msg_time = ctx.message.created_at
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

            if self.last_used is None or (
                    msg_time - self.last_used).seconds > self.revive_delay:
                await ctx.reply(
                    f"<@&{self.bot.config['commands']['revive']['revive_role']}> Trying to revive the chat. ||By <@{ctx.author.id}>||\n`{topic}`"
                )
            else:
                last = (msg_time - self.last_used).seconds
                timeLeft = self.revive_delay - last
                m, s = divmod(timeLeft, 60)
                await ctx.reply(f"The chat can be revived again in {m}m, {s}s."
                                )
        else:
            await ctx.reply(
                f"Head over to <#{self.bot.config['commands']['revive']['revive_channel']}> to revive the chat."
            )

    @commands.hybrid_command(name="rc",
                             aliases=["revivechat", "revive_chat", "rev_chat"],
                             hidden=True,
                             enabled=False)
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
    async def avatar(self, ctx, user_av: discord.Member = None, pfp: Literal["server", "default"]="server"):
        """View the avatar of a person. $avatar [user] {server/default}"""

        def display_av(user):
            try:
                if pfp=="server":
                    av = user.display_avatar.url
                else:
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
                    f"{user_o.mention} Do you wish for your avatar to be enlarged?"
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
                        "The user does not want their avatar to be displayed.")

            else:
                await ctx.reply(embed=display_av(ctx.message.author))

        else:
            if user_av:
                user_o = user_av
                a = "✅"
                b = "❌"
                msg = await ctx.reply(
                    f"{user_o.mention} Do you wish for your avatar to be enlarged?"
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
                        "The user does not want their avatar to be displayed.")

            else:
                await ctx.reply(embed=display_av(ctx.message.author))

    @commands.hybrid_command(name="state", hidden=True)
    async def state(self, ctx, state):
        """Stereotypes, TBD"""
        pass

    @commands.hybrid_command(name="most_used_emojis")
    async def most_used_emojis(self, ctx, user: discord.Member = None):
        """Which emojis do you use the most?"""
        if user is None:
            user = ctx.author
        emojis = self.bot.message_logs.most_used_emojis_user(user.id)
        ll = ""
        for i in emojis[0:10]:
            ll += f"{i[0]} : {i[1]}\n"
        emb = basic_embed(title=user.display_name,
                          desc=f"Your most used emojis are:\n{ll}")
        await ctx.reply(embed=emb)
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

    @commands.hybrid_command(name="emojify")
    async def emojify(self, ctx, text):
        """Emojify your text"""
        emojis = {
            'a': ':a:',
            'b': ':b:',
            'c': ':regional_indicator_c:',
            'd': ':regional_indicator_d:',
            'e': ':regional_indicator_e:',
            'f': ':regional_indicator_f:',
            'g': ':regional_indicator_g:',
            'h': ':regional_indicator_h:',
            'i': ':regional_indicator_i:',
            'j': ':regional_indicator_j:',
            'k': ':regional_indicator_k:',
            'l': ':regional_indicator_l:',
            'm': ':m:',
            'n': ':regional_indicator_n:',
            'o': ":o:",
            'p': ':regional_indicator_p:',
            'q': ':regional_indicator_q:',
            'r': ':regional_indicator_r:',
            's': ':regional_indicator_s:',
            't': ':regional_indicator_t:',
            'u': ':regional_indicator_u:',
            'v': ':regional_indicator_v:',
            'w': ':regional_indicator_w:',
            'x': ':x:',
            'y': ':regional_indicator_y:',
            'z': ':regional_indicator_z:',
            '?': ':question:',
        }
        words = text.lower().split(" ")
        final = ""
        for i in words:
            word = ""
            for j in i:
                try:
                    word += emojis[j]
                except:
                    pass
            final += word + "     "
        await ctx.reply(final)

    @commands.hybrid_group(name="birthday")
    async def birthday(self, ctx):
        """Commands regarding Birthdays"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @birthday.command(name="add")
    async def add_birthday(self, ctx, date):
        """Stores bday in the db."""
        # DD-MM-YYYY
        date_format = "%d/%m/%Y"
        try:
            date_final = datetime.datetime.strptime(date, date_format)
        except:
            await ctx.reply("Enter date in the format: DD/MM/YYYY", ephemeral=True)
            return
        bday = Birthday()
        bday.insert_command(ctx.message.author.id, date_final)
        bday.closeConnection()
        del bday
        await ctx.reply(f"Your birthdate has been set as: ||{date_final.strftime('%d/%m/%Y')}||.")



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
