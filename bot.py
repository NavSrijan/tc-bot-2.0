import discord
import asyncio
from discord.ext import commands
from functions import updateMessagesCount
import os
import time
import pdb


##########
# Variables
##
numberOfMessages = 0
people_dict = {}
##
##########
# Cogs to load
cogs = ['revive_chat',
'welcome'
]

async def load_cogs(bot, cogs):
    for extension in cogs:
        await bot.load_extension('cogs.' + extension)
        print(f"Loaded {extension}")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message: discord.Message):
    global numberOfMessages, people_dict
    
    if message.author == bot.user:
        return
    
    print(message.content)

    def process_messages(message):
        to_not_count = ["owo", "pls"]
        for i in to_not_count:
            if message.content.startswith(i):
                return False
        return True
    if process_messages(message) == True:
        numberOfMessages+=1
        try:
            kk = people_dict[message.author.id]
            people_dict[message.author.id] = kk+1
        except:
            people_dict[message.author.id] = 1
    if numberOfMessages > 3:
        print("updating messages")
        updateMessagesCount(people_dict)
        people_dict = {}
        numberOfMessages = 0

    try:
        await bot.process_commands(message)
    except Exception as e:
        print(e)


async def main():
    async with bot:
        await load_cogs(bot, cogs)
        await bot.start(os.environ["token"])

asyncio.run(main())