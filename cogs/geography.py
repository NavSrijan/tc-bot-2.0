from discord.ext import commands
import random
import asyncio
import os

class Geography(commands.Cog):
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
        
            

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)
    

async def setup(bot):
    await bot.add_cog(Geography(bot))