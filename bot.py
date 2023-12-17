import asyncio
import datetime
import logging
import os
import time
import json
import re

import discord
from discord.ext import commands
import emoji

from config import Config
from database_2 import Message_Logs, Afk, Database_suggestions, Command_Logs, Voice_Logs
from functions import download_and_return_image, load, save, utc_to_ist
from helpers import VoteView, VoteViewForEmoji, basic_embed

##########
# Variables
##
db_message_logs = Message_Logs()
db_command_logs = Command_Logs()
db_voice_logs = Voice_Logs()
db_afk = Afk()
tc_id = 838857215305187328 # SH
#tc_id = 864085584691593216 # TW
MY_GUILD = discord.Object(id=tc_id)

##
##########
# Cogs to load
cogs = [
    'chat_cmd', 'welcome', 'counting', 'news', 'mod', 'games', 'help',
    'image_fun', 'suggestions', 'boosters'
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Loading the config
config_obj = Config("variables/config.toml")
config = config_obj.get_config()
prefix = config['bot']['prefix']
activity = discord.Activity(type=discord.ActivityType.listening,
                            name=f"{config['bot']['prefix']}help")
bot = commands.Bot(command_prefix=prefix,
                   case_insensitive=True,
                   intents=intents,
                   status=discord.Status.do_not_disturb,
                   activity=activity)
bot.highlights = load("variables/highlights.pkl")
bot.to_torture = []
bot.config_obj = config_obj
bot.message_logs = Message_Logs()
bot.config = config
bot.prefix = prefix
bot.tc_id = tc_id

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8',
                              mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def load_cogs(bot, cogs):
    for extension in cogs:
        try:
            await bot.load_extension('cogs.' + extension)
            print(f"Loaded {extension}")
        except Exception as e:
            print(f"Error loading {extension}")
            print(e)


def get_afk_people_dict():
    global db_afk
    afk_people = {}
    all_users = db_afk.get_all_afk()
    for i in all_users:
        afk_people[i[0]] = [i[1], i[2], i[3]]
    return afk_people


afk_people = get_afk_people_dict()


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def setup_hook():
    await load_cogs(bot, cogs)
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)


@bot.command(name="afk")
@commands.cooldown(1, 32, commands.BucketType.user)
async def afk(ctx, *args):
    message = ctx.message
    role_required = role_required = bot.config['roles_list']['roles_for_afk']
    for i in role_required:
        if ctx.guild.get_role(i) in ctx.author.roles:
            name = message.author.display_name
            new_name = f"[AFK] {name}"
            try:
                await message.author.edit(nick=new_name)
            except Exception as e:
                print(e)
            await message.channel.send(f"{message.author.display_name} is AFK."
                                       )
            await asyncio.sleep(30)
            db_afk.make_afk(message)
            afk_people[message.author.id] = [
                True, datetime.datetime.utcnow(), message.content[5:]
            ]
            return
    await ctx.reply("You can't use this. Level up first!")


@afk.error
async def afk_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = basic_embed(title="Tham ja bhai!",
                         desc=f"Try again in {error.retry_after:.2f}s.",
                         color=discord.Color.fuchsia())
        await ctx.send(embed=em)


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

    if len(bot.to_torture) > 0:
        if message.author in bot.to_torture:
            await message.delete()
            return

    r_words = message.content.lower().split(" ")
    for i in r_words:
        if i in ["tc", "teenage", "community", "teenage", "teenagecommunity", "social", "hideout", "sh", "island"]:
            tc_emoji = "<a:tc_excited:995961225525608500>"
            await message.add_reaction(tc_emoji)
            break

        val_list = list(bot.highlights.values())
        if i in val_list:
            if message.channel.id in [
                    957263189320540170, 894987356678000670, 895229974909444096,
                    895025182207524925, 984196485518340136, 895017321037455372,
                    895221478411350026, 983824068497264670,
                    1006956616354107472, 973577832116674650, 972708478978261023
            ]:
                key_list = list(bot.highlights.keys())
                pos = val_list.index(i)
                p1 = key_list[pos]
                emb = discord.Embed(
                    description=message.content +
                    f"\n\n[Jump to the message]({message.jump_url})")
                emb.set_author(name=message.author.display_name,
                               icon_url=message.author.avatar.url)
                emb.color = discord.Color.blurple()
                await message.guild.get_member(p1).send(embed=emb)

    channels_with_image_access = [
        895221352267677697, 983791675874877500, 895221241412198410,
        983787831476490291, 895014066853117983
    ]
    roles_allowed_to_send_images = bot.config['roles_list'][
        'roles_allowed_to_send_images']
    if message.channel.id not in channels_with_image_access:
        to_pass = True
        for k in message.author.roles:
            if k.id in roles_allowed_to_send_images:
                to_pass = False
                break
        if to_pass == True:
            for i in config['blocked_urls']['urls']:
                if i in message.content.lower():
                    await message.author.send(
                        f"You aren't allowed to send link in <#{957263189320540170}>."
                    )
                    await message.delete()

    # Changing suggestions to polls
    if message.channel.id == config['commands']['misc']['suggestions_channel']:
        # Converts suggestion to a vote
        emb = discord.Embed(
            title=f"{message.author.display_name}'s suggestion",
            description=f"`{message.content}`\n\n✅ ---> 0\n\n❌ ---> 0",
            color=discord.Color.dark_gold())

        view = VoteView()
        db = Database_suggestions

        await message.channel.send(embed=emb, view=view)
        await message.delete()
        return

    # Changing emojis to polls
    if message.channel.id == config['commands']['misc'][
            'emoji_suggestions_channel']:
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
        db = Database_suggestions

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

    # Check if anyone mentions AFK user
    for i in message.mentions:
        if i.id in afk_people and not message.content.startswith(
                "$remove_afk"):
            last_online = utc_to_ist(afk_people[i.id][1])
            if i.display_name.startswith("[AFK] "):
                name_to_display = i.display_name[6:]
            else:
                name_to_display = i.display_name
            allowed_mentions = discord.AllowedMentions(
                users=False,  # Whether to ping individual user @mentions
                everyone=False,  # Whether to ping @everyone or @here mentions
                roles=False,  # Whether to ping role @mentions
                replied_user=True,  # Whether to ping on replies to messages
            )
            await message.reply(
                f"{name_to_display} went AFK {discord.utils.format_dt(last_online, style='R')} ago:\n{afk_people[i.id][-1]}",
                allowed_mentions=allowed_mentions)

    def process_messages(message):
        to_not_count = ["owo", "pls"]
        for i in to_not_count:
            if message.content.lower().startswith(i):
                return False
        return True

    if process_messages(message):
        try:
            number_of_words = len(message.content.split(" "))
            if number_of_words > 50:
                number_of_words = 50
            emojis = re.findall(r"\<:\w*:\d*>|:\w*:",
                                emoji.demojize(message.content))
            db_message_logs.insert_message(message, number_of_words, emojis)
        except:
            pass

    try:
        ctx = await bot.get_context(message)
        if ctx.invoked_with:
            ments = ctx.message.content[len(ctx.prefix) +
                                        len(ctx.invoked_with):].lstrip().split(
                                            " ")
            arguments = {}
            for i, j in enumerate(ments):
                arguments[i] = j
            arguments = json.dumps(arguments)
            db_command_logs.insert_command(message, message.id,
                                           ctx.command.name, arguments,
                                           message.author)

        await bot.process_commands(message)
    except Exception as e:
        print(e)


@bot.event
async def on_interaction(interaction):
    try:
        arguments = json.dumps(interaction.data['options'][0])
    except:
        arguments = json.dumps({})
    if interaction.data['name'] in ['']:
        return
    db_command_logs.insert_command(interaction, interaction.id,
                                   interaction.data['name'], arguments,
                                   interaction.user)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    if after.channel is None and before.channel:
        state = 0
        channel_id = before.channel.id
        data = db_voice_logs.fetch_last_state(member.id)
        time_of_join = data[11]
        time_spent = (datetime.datetime.now() - time_of_join).seconds
    elif before.channel is None and after.channel:
        state = 1
        channel_id = after.channel.id
        time_spent = 0
    db_voice_logs.insert_command(member.id, channel_id, after, state,
                                 time_spent)


@bot.event
async def on_member_update(before, after):
    if "whistler" in after.nick.lower() and after.id != 302253506947973130:
        await after.edit(nick="gay")


bot.remove_command('help')


async def main():
    async with bot:
        await bot.start(os.environ["tc_token"])


asyncio.run(main())
