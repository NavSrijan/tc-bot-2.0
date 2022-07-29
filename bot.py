import discord
import asyncio
from discord.ext import commands, tasks
from database import DB_messages, DATABASE_URL
import os
import time
import pdb


##########
# Variables
##

##
##########
# Cogs to load
cogs = ['revive_chat',
'welcome',
'counting',
'news',
'mod',
'games',
'help',
'image_fun'

]

async def load_cogs(bot, cogs):
    for extension in cogs:
        await bot.load_extension('cogs.' + extension)
        print(f"Loaded {extension}")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
prefix = "$"
activity = discord.Activity(type=discord.ActivityType.listening, name="$help")
bot = commands.Bot(command_prefix=prefix, intents=intents, status=discord.Status.do_not_disturb, activity=activity)
db_2 = DB_messages(DATABASE_URL, "message_bank")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot, cogs)

@bot.event
async def on_message(message: discord.Message):

    if message.author == bot.user or message.author.bot == True:
        return
    
    #print(message.content)
    message.content = message.content.lower()

    r_words =  message.content.lower().split(" ")
    for i in r_words:
        if i in ["tc", "teenage", "community", "teenage", "teenagecommunity"]:
            tc_emoji = "<a:tc_excited:995961225525608500>"
            #unk = "<a:tc_excited:995961992173072445>"
            await message.add_reaction(tc_emoji)
            break
        #if i in ["bkl", "bsdk", "chutiya", "chutiye", "❤️ de", "❤️de", "❤️ day", "❤️day", "bhadwe", "bhadwa", "bhadwi", "lodu", "gandu", "gaandu", "lawde", "lavde", "laude"]:
        #    await message.reply("Gaali na de!")
        #    break

    channels_with_image_access = [895221352267677697, 983791675874877500, 895221241412198410, 983787831476490291, 895014066853117983]
    roles_allowed_to_send_images = [960932026549174272, 998303854925975734, 893950378431877131, 970902786638250034, 839010251868078101, 975456077623746590, 977217186928160828]
    if message.channel.id not in channels_with_image_access:
        to_pass = True
        for k in message.author.roles:
            if k.id in roles_allowed_to_send_images:
                to_pass = False
                break
        if to_pass==True:
            for i in ["https://media.discordapp.net/attachments","https://cdn.discordapp.com/attachments", "https://imgur.com", "https://i.imgur.com", "https://images-ext-1.discordapp.net/external"]:
                if i in message.content:
                    #await message.author.send(f"You aren't allowed to send link in <#{os.environ['revive_channel']}>.")
                    await message.author.send(f"You aren't allowed to send link in <#{957263189320540170}>.")
                    await message.delete()
                


    def process_messages(message):
        to_not_count = ["owo", "pls"]
        for i in to_not_count:
            if message.content.lower().startswith(i):
                return False
        return True
    if process_messages(message) == True:
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