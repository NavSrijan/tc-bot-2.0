from discord.ext import commands
import discord
from PIL import Image, ImageFont, ImageDraw
import os
from io import BytesIO

class ImageFun(commands.Cog):
    """Basic hello commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wish")
    async def modiji(self, ctx):
        base_image = Image.open('assets/modi1.jpg')
        base_image = base_image.resize((1080, 720) ,Image.ANTIALIAS)
        base = Image.new('RGB', base_image.size)
        base.paste(base_image)
        text = '      Best of Luck      '
        if ctx.message.mentions:
            name = ctx.message.mentions[0].name
        else:
            await ctx.reply("Mention someone.")
            return
        name = "\n"+name.center(len(text), " ")
        text+=name
        title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', 70)
        ImageDraw.Draw(base).text((250, 550), text, 'rgb(255,69,0)', font=title_text, spacing=10)
        
        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(file=discord.File(fp=image_binary, filename='modiji.png'))


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

async def setup(bot):
    await bot.add_cog(ImageFun(bot))
