from discord.ext import commands
import random
import asyncio
import os
import pdb

class Geography(commands.Cog):
    """Games"""
    
    def __init__(self, bot):
        self.bot = bot
        self.countries = self.load_countries()
        self.lives = 3
        self.points = 0
    def load_countries(self, file="country_data.csv"):
        with open(file, "r") as f:
            data = f.readlines()
        countries = {}
        for i in data:
            j = i.split(",")
            countries[j[0][1:-1].lower()] = j[1][1:-1].lower()
        return countries

    @commands.command(name="geo")
    async def country_capital(self, ctx):
        await ctx.reply("Starting the game!\nYou'll have ```60 secs``` for each question.")
        channel = ctx.channel

        points_and_lives = "```Points: {}\nLives: {}```"

        while self.lives!=0:
            capital = random.choice(list(self.countries.values()))
            country = [k for k, v in self.countries.items() if v == capital][0]
            print(country, capital)
            
            await channel.send(f"What is the capital of `{country}`?")
            try:
                def check(message):
                    if message.content.lower() in ["$skip"]:
                        return True
                    return message.channel == channel and message.content.lower() == capital
                msg = await self.bot.wait_for('message', check = check, timeout=60)
                if msg.content.lower() == "$skip":
                    self.lives-=1
                    await channel.send(f"Skipping this question.")
                    await channel.send(points_and_lives.format(self.points, self.lives))
                    continue
                self.points += 1
                await msg.reply(f"Yes! You got that right!")
                await channel.send(points_and_lives.format(self.points, self.lives))
                continue
            except asyncio.TimeoutError:
                await channel.send(f"TIMEOUT!!!")
                await channel.send(f"The answer was `{capital}`")
                self.lives -=1
                await channel.send(points_and_lives.format(self.points, self.lives))
                continue
        pons = self.points
        self.points = 0
        self.lives = 3
        await channel.send(f"You lost! Total Points: {pons}")
        
    @commands.command(name='pi')
    async def pi(self, ctx):
        x = 0
        exp = "3."
        score = 0

        channel = ctx.channel
        author = ctx.author

        def matchDigits(dig):
            dig = list(dig)
            score = 0
            h = 0
            for i in digits[0:len(dig)]: 
                if dig[h]!=i:
                    return score
                score+=1
                h+=1
            return score
        def check(message):
            return message.channel == channel and message.author == author
        def check_int(x):
            try:
                x = int(x)
                return True
            except:
                return False

        file = open("/home/thewhistler/thewhistlerScripts/pi.pi", "r")
        digits = file.readline()
        digits.strip(" ")
        
        await channel.send("START!")
        await channel.send("3.....")

        diff = 2

        while True:
            try:
                x= await self.bot.wait_for('message', check = check, timeout=10)
                if check_int(x.content):
                    exp+=x.content
                    if matchDigits(exp)==len(x.content)+diff:
                        diff = len(exp)
                        await x.add_reaction("🙂")
                        score=matchDigits(exp)
                    else:
                        score=matchDigits(exp)
                        await channel.send("SCORE: {}".format(score-2))
                        await channel.send("The next four digits are: {}".format(digits[len(exp)-1:len(exp)+3]))
                        break
            except:
                await channel.send("Timeout! Try again!")
                await channel.send("SCORE: {}".format(score-2))
                break



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)
    

async def setup(bot):
    await bot.add_cog(Geography(bot))