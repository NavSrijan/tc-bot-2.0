from discord.ext import commands
import discord
from functions import utc_to_ist
import datetime
import os
import pdb

class Embedder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command(name="embed")
    async def create_embed(self, ctx):
        await ctx.reply("Starting embed creation.")

        member = ctx.message.author
        channel = ctx.message.channel

        def check(message):
            return message.author == member and message.channel == channel

        a = "🇦"
        b = "🇧"

        msg = await ctx.message.channel.send("A. Movie announcement or B. General announcement?")
        await msg.add_reaction(a)
        await msg.add_reaction(b)
        def check_reaction(reaction, user):
            return user == member and reaction.emoji in [a, b] and user.bot == False
        reaction = await self.bot.wait_for("reaction_add", check = check_reaction, timeout=60)
        emoji = reaction[0].emoji

        if emoji == a:
            await ctx.message.channel.send("Movie name?")
            msg = await self.bot.wait_for('message', check = check, timeout=180)
            movieName = msg.content

            await ctx.message.channel.send("Movie duration?")
            msg = await self.bot.wait_for('message', check = check, timeout=180)
            movieDuration = msg.content

            await ctx.message.channel.send("Time?")
            msg = await self.bot.wait_for('message', check = check, timeout=180)
            ttime = msg.content

            desc = f"""
Hey guys, we are planning to host a movie night today at {ttime} !!
**•Movie name ->**
{movieName}
**•Duration ->**
{movieDuration}
"""
            image_url = "https://media.discordapp.net/attachments/894495731451297852/992826041422848060/images_13.jpeg?width=475&height=475"
            thumbnail_url = "https://cdn.discordapp.com/attachments/992882759330701323/995960581892870245/standard_1.gif"

            emb = discord.Embed(title="Movie Alert!", description=desc)
            emb.set_image(url=image_url)
            emb.set_thumbnail(url=thumbnail_url)
            emb.set_footer(text=utc_to_ist(datetime.datetime.utcnow()).date())

            await ctx.message.channel.send("Which channel to send to?")
            msg = await self.bot.wait_for('message', check = check, timeout=180)
            channel_to_send_to = int(msg.content[2:-1])

            await msg.reply(embed=emb)
            msg = await ctx.message.channel.send("Is this correct?")
            await msg.add_reaction(a)
            await msg.add_reaction(b)
            def check_reaction(reaction, user):
                return user == member and reaction.emoji in [a, b] and user.bot == False
            reaction = await self.bot.wait_for("reaction_add", check = check_reaction, timeout=60)
            emoji = reaction[0].emoji
            if emoji == a:
                try:
                    chnl = self.bot.get_channel(channel_to_send_to)
                    await chnl.send(embed=emb)
                except:
                    await msg.reply("Channel wrong")
            else:
                await msg.reply("Aborted!")

        elif emoji == b:
            await ctx.message.channel.send("Still developing this....")
        else:
            await ctx.message.channel.send(":hehe:")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

async def setup(bot):
    await bot.add_cog(Embedder(bot))