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
people_dict = {}
##
##########
# Cogs to load
cogs = ['revive_chat',
'welcome',
'counting',
'news',

]

async def load_cogs(bot, cogs):
    for extension in cogs:
        await bot.load_extension('cogs.' + extension)
        print(f"Loaded {extension}")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)
db_2 = DB_messages(DATABASE_URL, "message_bank")

#@tasks.loop(minutes=5)
#async def push_to_db():
#    global people_dict
#    if len(people_dict)>1:
#        print("updating messages")
#        updateMessagesCount(people_dict)
#        people_dict = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot, cogs)
    await push_to_db.start()

@bot.event
async def on_message(message: discord.Message):
    global numberOfMessages, people_dict

    if message.author == bot.user or message.author.bot == True:
        return
    
    #print(message.content)
    message.content = message.content.lower()

    ## Reacting to user's first message.
    r_words =  message.content.lower().split(" ")
    for i in r_words:
        if i in ["tc", "teenage", "community", "teenage", "teenagecommunity"]:
            tc_emoji = "<a:tc_excited:995961225525608500>"
            #unk = "<a:tc_excited:995961992173072445>"
            await message.add_reaction(tc_emoji)
            break
        if i in ["bkl", "bsdk", "chutiya", "chutiye", "❤️ de", "❤️de", "❤️ day", "❤️day", "bhadwe", "bhadwa", "bhadwi", "lodu", "gandu", "gaandu", "lawde", "lavde", "laude"]:
            await message.reply("Gaali na de!")
            break

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


async def main():
    async with bot:
        await bot.start(os.environ["token"])

asyncio.run(main())