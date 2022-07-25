from discord.ext import commands
import discord
import os
import requests
from newsapi import NewsApiClient
import requests
import ast
import time

import pdb

def getFact():
    limit = 1
    api_url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(limit)
    response = requests.get(api_url, headers={'X-Api-Key': os.environ['xapi']})
    if response.status_code == requests.codes.ok:
        final = ast.literal_eval(response.text)[0]['fact']
        return final
    else:
        print("Error:", response.status_code, response.text)
def getNews(query):
    # https://newsapi.org/
    key = str(os.environ["newsapi"])
    newsapi = NewsApiClient(api_key=key)
    #top = newsapi.get_top_headlines(q=query,
    #                                language='en',)
    top = newsapi.get_everything(q=query,
                                    language='en',)
    #nws = random.choice(top['articles'])
    nws = top['articles'][0]

    my = discord.Embed(
                   title = nws['title'],
                   description = nws['description'] + f"\n\n\n Read more at {nws['url']}",
                   color=0xc21d46 ) 
    my.set_image(url=nws['urlToImage'])
    my.set_author(name=nws['source']['name'])
    return my
def getMeaning(word):
    response = requests.get(f"http://api.urbandictionary.com/v0/define?term={word}")
    res = response.json()['list']
    return res

class News(commands.Cog):
    """Random Apis"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news")
    async def news(self, ctx, *args):
        try:
            query = " ".join(args)
        except:
            query = ""
        try:
            emb = getNews(query)
            await ctx.message.channel.send(embed=emb)
        except:
            z = await ctx.message.reply("This query fetched no articles.")
            time.sleep(2)
            await z.delete()

    @commands.command(name="fact")
    async def fact(self, ctx):
        fact = getFact()
        toSend = f"```{fact}```"
        await ctx.message.reply(toSend)

    @commands.command(name="what")
    async def meaning(self, ctx, *args):
        word = " ".join(args)
        res = getMeaning(word)
        toSend = "Data from Urban Dictionary"
        j = 1
        for i in res:
            defn = i['definition']
            if len(defn)<=600:
                toSend+=f"```{j}. {defn}```\n"
                j+=1
            if j==4:
                break
        await ctx.message.reply(toSend)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

async def setup(bot):
    await bot.add_cog(News(bot))