import discord
import asyncio
from discord.ext import commands, tasks
from functions import updateMessagesCount
import os
import time


##########
# Variables
##
people_dict = {}
##
##########
# Cogs to load
cogs = ['revive_chat',
'welcome',
'loops',
]

async def load_cogs(bot, cogs):
    for extension in cogs:
        await bot.load_extension('cogs.' + extension)
        print(f"Loaded {extension}")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)

@tasks.loop(minutes=5)
async def push_to_db():
    global people_dict
    if len(people_dict)>1:
        print("updating messages")
        updateMessagesCount(people_dict)
        people_dict = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot, cogs)
    await push_to_db.start()

@bot.event
async def on_message(message: discord.Message):
    global numberOfMessages, people_dict
    
    if message.author == bot.user:
        return
    
    #print(message.content)
    message.content = message.content.lower()

    def process_messages(message):
        to_not_count = ["owo", "pls"]
        for i in to_not_count:
            if message.content.lower().startswith(i):
                return False
        return True
    if process_messages(message) == True:
        try:
            number_of_words = len(message.content.split(" "))
            #print(number_of_words)
            kk = people_dict[message.author.id]
            people_dict[message.author.id] = kk+number_of_words
        except:
            people_dict[message.author.id] = 1

    try:
        await bot.process_commands(message)
    except Exception as e:
        print(e)


async def main():
    async with bot:
        await bot.start(os.environ["token"])

asyncio.run(main())