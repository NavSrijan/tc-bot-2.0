import discord
import asyncio
from discord.ext import commands, tasks
import datetime
from database import Database_message_bank, DATABASE_URL, Database_suggestions, Database_afk
from helpers import VoteView, VoteViewForEmoji, basic_embed
from functions import download_and_return_image
import os
import time

##########
# Variables
##
db_2 = Database_message_bank(DATABASE_URL, "message_bank")
db_afk = Database_afk(DATABASE_URL, "afk")


def get_afk_people_dict():
    global db_afk
    afk_people = {}
    all_users = db_afk.get_all_afk()
    for i in all_users:
        afk_people[i[0]] = [i[1], i[2], i[3]]
    return afk_people


afk_people = get_afk_people_dict()

##
##########
# Cogs to load
cogs = [
    'chat_cmd', 'welcome', 'counting', 'news', 'mod', 'games', 'help',
    'image_fun', 'suggestions', 'boosters', 'freedom'
]


async def load_cogs(bot, cogs):
    for extension in cogs:
        try:
            await bot.load_extension('cogs.' + extension)
            print(f"Loaded {extension}")
        except:
            print(f"Error loading {extension}")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
prefix = "$"
activity = discord.Activity(type=discord.ActivityType.listening, name="$help")
bot = commands.Bot(command_prefix=prefix,
                   case_insensitive=True,
                   intents=intents,
                   status=discord.Status.do_not_disturb,
                   activity=activity)
bot.highlights = {}


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot, cogs)


@bot.command(name="afk")
async def afk(ctx, *args):
    message = ctx.message
    role_required = [
        977217186928160828, 1005791066257096705, 1005791107713601576,
        1005791150629720155, 1005791187652841512, 1005791239490261092,
        1005791278199488564, 1005791286571315240, 1005791355357904946,
        998303854925975734, 960932026549174272, 988445679426867200,
        970902786638250034, 893950378431877131, 839010251868078101
    ]
    for i in role_required:
        if ctx.guild.get_role(i) in ctx.author.roles:
            db_afk.make_afk(message)
            afk_people[message.author.id] = [
                True, datetime.datetime.utcnow(), message.content[5:]
            ]
            name = message.author.display_name
            new_name = f"[AFK] {name}"
            try:
                await message.author.edit(nick=new_name)
            except Exception as e:
                print(e)
            await message.channel.send(f"{message.author.display_name} is AFK."
                                       )
            return
    await ctx.reply("You can't use this. Level up first!")


@commands.has_permissions(kick_members=True)
@bot.command(name="remove_afk")
async def remove_afk(ctx, *args):
    message = ctx.message
    try:
        mention = message.mentions[0]
        db_afk.remove_afk(mention.id)
        name = mention.display_name
        if name[0:6] == "[AFK] ":
            name = name[6:]
            try:
                await mention.edit(nick=name)
            except Exception as e:
                print(e)
        del afk_people[mention.id]
        to_delete = await message.reply(f"Removed {mention.mention}'s AFK.")
        await asyncio.sleep(2)
        await to_delete.delete()
    except:
        await ctx.reply("Mention someone.")


@bot.event
async def on_message(message: discord.Message):
    global afk_people, db_afk

    if message.author == bot.user or message.author.bot == True:
        return

    r_words = message.content.lower().split(" ")
    for i in r_words:
        if i in ["tc", "teenage", "community", "teenage", "teenagecommunity"]:
            tc_emoji = "<a:tc_excited:995961225525608500>"
            #unk = "<a:tc_excited:995961992173072445>"
            await message.add_reaction(tc_emoji)
            break
        if i in [
                "independence", "independent", "india", "bharat",
                "swatantrata", "diwas", "hindustan", "aazadi", "azadi", "azad",
                "bhagat", "sukhdev"
        ]:
            emoji_to_react = "<:pepeindia:1005858993492729998>"
            await message.add_reaction(emoji_to_react)
            break

        val_list = list(bot.highlights.values())
        if i in val_list:
            key_list = list(bot.highlights.keys())
            pos = val_list.index(i)
            p1 = key_list[pos]
            emb = discord.Embed(
                description=message.content +
                f"\n\n[Jump to the message]({message.jump_url})")
            emb.set_author(name=message.author.display_name,
                           icon_url=message.author.avatar.url)
            emb.color = discord.Color.blurple()
            await p1.send(embed=emb)

    channels_with_image_access = [
        895221352267677697, 983791675874877500, 895221241412198410,
        983787831476490291, 895014066853117983
    ]
    roles_allowed_to_send_images = [
        960932026549174272, 998303854925975734, 893950378431877131,
        970902786638250034, 839010251868078101, 975456077623746590,
        977217186928160828
    ]
    if message.channel.id not in channels_with_image_access:
        to_pass = True
        for k in message.author.roles:
            if k.id in roles_allowed_to_send_images:
                to_pass = False
                break
        if to_pass == True:
            for i in [
                    "https://media.discordapp.net/attachments",
                    "https://cdn.discordapp.com/attachments",
                    "https://imgur.com", "https://i.imgur.com",
                    "https://images-ext-1.discordapp.net/external",
                    "https://www.reddit.com/", "https://www.youtube.com/",
                    "https://youtu.be/", "https://bit.ly/"
            ]:
                if i in message.content.lower():
                    #await message.author.send(f"You aren't allowed to send link in <#{os.environ['revive_channel']}>.")
                    await message.author.send(
                        f"You aren't allowed to send link in <#{957263189320540170}>."
                    )
                    await message.delete()

    # Changing suggestions to polls
    if message.channel.id == 894495753655943210:
        # Converts suggestion to a vote
        emb = discord.Embed(
            title=f"{message.author.display_name}'s suggestion",
            description=f"`{message.content}`\n\n✅ ---> 0\n\n❌ ---> 0",
            color=discord.Color.dark_gold())

        view = VoteView()
        db = Database_suggestions(DATABASE_URL, "suggestions")

        await message.channel.send(embed=emb, view=view)
        await message.delete()
        return

    # Changing emojis to polls
    if message.channel.id == 998123210493132875:
        # Converts emoji suggestions to a vote
        if message.attachments:
            atm = message.attachments[0]
        else:
            a = await message.reply("Send only an image.")
            await asyncio.sleep(2)
            await message.delete()
            await a.delete()
            return

        emb = discord.Embed(
            title=f"{message.author.display_name}'s emoji suggestion",
            description=f"`Is this emoji good?`\n\n✅ ---> 0\n\n❌ ---> 0",
            color=discord.Color.random())
        img = download_and_return_image(atm.url)
        emb.set_image(url="attachment://emojiSuggestion.png")

        view = VoteViewForEmoji()
        db = Database_suggestions(DATABASE_URL, "suggestions")

        await message.channel.send(file=img, embed=emb, view=view)
        await message.delete()
        return

    # Managing AFK
    ## Removing AFK
    if message.author.id in afk_people:
        db_afk.remove_afk(message.author.id)
        name = message.author.display_name
        if name[0:6] == "[AFK] ":
            name = name[6:]
            try:
                await message.author.edit(nick=name)
            except Exception as e:
                print(e)
        del afk_people[message.author.id]
        to_delete = await message.reply("Removed your AFK.")
        await asyncio.sleep(2)
        await to_delete.delete()
    ## Check if anyone mentions AFK user
    def return_time_string(td: datetime.timedelta):
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        if h == 0:
            return f"{m} mins {s} secs"
        else:
            return f"{h} hours {m} mins {s} secs"

    for i in message.mentions:
        if i.id in afk_people and not message.content.startswith(
                "$remove_afk"):
            last_online = afk_people[i.id][1]
            diff = (datetime.datetime.utcnow() - last_online)
            await message.reply(
                f"{i.display_name} went AFK {return_time_string(diff)} ago:\n{afk_people[i.id][-1]}"
            )

    def process_messages(message):
        to_not_count = ["owo", "pls"]
        for i in to_not_count:
            if message.content.lower().startswith(i):
                return False
        return True

    if process_messages(message):
        try:
            number_of_words = len(message.content.split(" "))
            db_2.update_message(message.author.id, number_of_words)
        except:
            pass

    try:
        await bot.process_commands(message)
    except Exception as e:
        print(e)


bot.remove_command('help')


async def main():
    async with bot:
        await bot.start(os.environ["token"])


asyncio.run(main())
