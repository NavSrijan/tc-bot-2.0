from discord.ext import commands
import discord
from database_2 import Message_Logs, Voice_Logs
from helpers import *
from PIL import Image, ImageFont, ImageDraw
import os
import random
import requests
from io import BytesIO
import textwrap


def icon(image_object, image_size):

    im = image_object

    # start to make the photo square
    width, height = im.size
    crop_size = min(width, height)

    #length to crop from each side
    left = (width - crop_size) / 2
    right = (width + crop_size) / 2
    top = (height - crop_size) / 2
    bottom = (height + crop_size) / 2

    im = im.crop((left, top, right, bottom))

    # resize icon depending on image_size
    im = im.resize((image_size, image_size), Image.ANTIALIAS)
    #im = im.rotate(0)

    #create a round border
    bigsize = (image_size * 3, image_size * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    return im


class ImageFun(commands.Cog):
    """Image manipulation commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="iloveyou")
    async def ily_real(self, ctx):
        """Just puts your pfp on Dr. Strange for some reason ||I was bored.||
        Syntax: $iloveyou
        """
        x, y = 300, 100
        base = Image.open(f'assets/images/iloveyou/1.jpg')
        url = ctx.author.avatar.url
        im = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
        dw = icon(im, 350)
        base.paste(dw, (x, y), dw)
        file = send_image(base)
        await ctx.send(file=file)

    @commands.hybrid_command(name="spinner")
    async def spinner(self, ctx):
        """Spinner!"""
        path = "assets/images/spinner"
        files = os.listdir(path)

        with open(path + "/" + random.choice(files), "rb") as f:
            await ctx.reply(file=discord.File(f))

    @commands.hybrid_command(name="binod")
    async def binod(self, ctx, text=""):
        """Dekh raha hai na Binod?
        Syntax: $binod kaise help dekha ja raha hai
        """
        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        base = Image.open(f'assets/images/binod/binod.png')

        base = center_text(base,
                           text,
                           font_to_use,
                           textwrap_=True,
                           font_diff=-5)
        file = send_image(base)
        await ctx.reply(file=file)

    @commands.hybrid_command(name="jal")
    async def jal(self, ctx, text=" "):
        """Jal lijiye
        Syntax: $jal thak gaye honge dc chalate chalate"""
        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        base = Image.open(f'assets/images/jal/jal.jpg')

        name = text

        text = f"Jal lijiye, thak gaye honge"
        base = center_text(base, text, font_to_use, name=name, font_diff=0)
        file = send_image(base)
        await ctx.reply(file=file)

    @commands.hybrid_command(name="compress")
    async def compress(self, ctx, user: discord.Member):
        """Don't like someone? Just compress them!
        Syntax: $compress @user"""
        images = []
        discord_bg = "#36393F"

        if user:
            name = user
        else:
            await ctx.reply("Mention someone.")
            return
        await ctx.reply("Generating.", ephemeral=True)

        url = name.avatar.url
        ima = Image.open(requests.get(url, stream=True).raw).convert('RGBA')

        width, height = ima.size
        w, h = ima.size

        while height > 0:
            im = Image.new('RGBA', (w, h), color=discord_bg)
            imz = ima.resize((width, height)).convert('RGBA')
            x, y = w - width, h - height
            im.paste(imz, (x, y), imz)
            images.append(im)
            height -= 10

        images[0].save('assets/images/compress/1.gif',
                       save_all=True,
                       append_images=images[1:],
                       optimize=False,
                       duration=1,
                       loop=0)
        await ctx.channel.send(
            file=discord.File("assets/images/compress/1.gif"))

    @commands.hybrid_command(name="ily")
    async def ily(self, ctx, user: discord.Member):
        """Lonely?
        Syantx: $ily @user"""
        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        choices = ['emma.jpeg', 'olsen.jpg', "scarjo.jpg"]
        choice = random.choice(choices)
        base_image = Image.open(f'assets/images/ily/{choice}')
        base = Image.new('RGB', base_image.size)
        base.paste(base_image)
        text = 'I love you'
        if user:
            name = user.name
        else:
            await ctx.reply("Mention someone.")
            return
        await ctx.reply("Generating", ephemeral=True)
        name = "\n" + name.center(len(text), " ")
        text += name

        title_text = ImageFont.truetype(font_to_use, 50)
        xc, yc = base.size
        a, b, c, d = title_text.getbbox(text)

        font_size = 50
        while xc < c or yc < d:
            font_size -= 5
            title_text = ImageFont.truetype(font_to_use, font_size)
            a, b, c, d = title_text.getbbox(text)

        a, b, c, d = title_text.getbbox(text)
        b_x = int(xc / 2) - int(c / 2) - (0 * xc / 100)
        b_y = int(yc) - ((20 * yc) / 100) - d

        ImageDraw.Draw(base).text((b_x, b_y),
                                  text,
                                  'rgb(255,0,0)',
                                  font=title_text,
                                  spacing=10)

        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='modiji.png')
            await ctx.reply(file=file)

    @commands.hybrid_command(name="travel")
    async def travel_ticket(self, ctx, passenger, from_place, destination):
        """Generate a airline ticket for your next travel destination.
        syntax example: $travel "Nick Jonas" Delhi Karachi
        """
        name = passenger
        to_place = from_place
        from_place = destination

        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        base_image = Image.open(
            f'assets/images/travel_ticket/base.png').convert('RGBA')
        base = Image.new('RGBA', base_image.size)
        base.paste(base_image)
        if len(name) > 20:
            font_size = 15
        else:
            font_size = 20
        title_text = ImageFont.truetype(font_to_use, font_size)

        ImageDraw.Draw(base).text((120, 240),
                                  to_place,
                                  'rgb(0,0,0)',
                                  font=title_text,
                                  spacing=10)
        ImageDraw.Draw(base).text((390, 240),
                                  from_place,
                                  'rgb(0,0,0)',
                                  font=title_text,
                                  spacing=10)
        ImageDraw.Draw(base).text((120, 305),
                                  name,
                                  'rgb(0,0,0)',
                                  font=title_text,
                                  spacing=10)

        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='modiji.png')
            await ctx.send(file=file)

    @commands.hybrid_command(name="wish")
    async def modiji(self, ctx, user: discord.Member):
        """
        Wish someone a best of luck!
        syntax: $wish {mention}
        """
        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        choices = [
            "modi1.jpg", "elon1.jpg", "mike1.jpg", "bean1.jpg", "vin1.jpeg"
        ]
        choice = random.choice(choices)
        base_image = Image.open(f'assets/images/wish/{choice}')
        base_image = base_image.resize((1080, 720), Image.ANTIALIAS)
        base = Image.new('RGB', base_image.size)
        base.paste(base_image)
        text = '      Best of Luck      '
        name = user.name
        name = "\n" + name.center(len(text), " ")
        text += name
        title_text = ImageFont.truetype(font_to_use, 70)
        ImageDraw.Draw(base).text((0, 550),
                                  text,
                                  'rgb(255,255,255)',
                                  font=title_text,
                                  spacing=10)

        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='modiji.png')

        emb = basic_embed(color=discord.Color.orange(),
                          title=f"{ctx.author.name} wishes {name}",
                          image_url="attachment://modiji.png")
        await ctx.reply(file=file, embed=emb)

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="lb_image")
    async def lb_image(self, ctx, offset_by_days: int = 0):
        """
        Generates weekly lb image
        syntax: $lb_image <days_to_subtract>
        """
        font_to_use = "assets/fonts/B612Mono-Bold.ttf"
        db = Message_Logs()
        await ctx.reply("Starting the process.", ephemeral=True)

        try:
            date_to_subtract = int(offset_by_days)
            lb = db.lb_week_combined(date_to_subtract=date_to_subtract)
        except:
            lb = db.lb_week_combined()

        def check_role(user, roles_to_check: list):
            """Returns True if any user has any roles mentioned in roles_to_check."""
            for i in user.roles:
                if i.id in roles_to_check:
                    return True
            return False
        items_to_pop = []
        for i in lb:
            try:
                user = ctx.guild.get_member(i[0])
                if check_role(user, self.bot.config['roles_list']['roles_not_in_lb']):
                    items_to_pop.append(i)
            except:
                items_to_pop.append(i)
                continue
        for i in items_to_pop:
            lb.remove(i)

        top_2 = lb[0:2]
        top_10 = lb[0:10]

        im_radius = 200

        background_image = Image.open('assets/images/lb_image/bg.png')
        background_image = background_image.resize((720, 1080),
                                                   Image.ANTIALIAS)
        base = Image.new('RGB', background_image.size)
        base.paste(background_image)

        title_text = ImageFont.truetype(font_to_use, 70)
        ImageDraw.Draw(base).text((280, 20),
                                  ' TEENAGE\nCOMMUNITY',
                                  'rgb(255,255,255)',
                                  font=title_text,
                                  spacing=10)

        tc = Image.open("assets/images/lb_image/tc_f.png").convert('RGBA')
        tc = tc.resize((im_radius - 40, im_radius - 40), Image.ANTIALIAS)
        base.paste(tc, (80, 20), tc)

        ### Get icons
        iconsd = []
        for i in top_2:
            try:
                url = ctx.message.guild.get_member(int(i[0])).avatar.url
            except:
                url = ctx.message.guild.get_member(int(
                    i[0])).default_avatar.url
            im = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
            dw = icon(im, im_radius)
            iconsd.append(dw)

        decorator_icon = Image.open("assets/images/lb_image/f1.png").convert(
            'RGBA')
        decorator_icon = decorator_icon.resize(
            (im_radius - 40, im_radius - 40), Image.ANTIALIAS)

        s1_y = 65
        s1_x = int(s1_y * 2.7)
        s1 = Image.open("assets/images/lb_image/s1.png").convert('RGBA')
        s1 = s1.resize((s1_x, s1_y), Image.ANTIALIAS)

        x = 120
        y = 240

        diff = 100
        diff2 = 30

        kk = 0
        names = []
        for i in top_2:
            try:
                hoho = ctx.message.guild.get_member(int(i[0])).name
            except:
                hoho = "User not found"
            names.append(hoho)
        runner_up_list = {}
        temp = 0
        for i in top_10:
            try:
                runner_up_list[ctx.message.guild.get_member(int(
                    i[0])).name] = i[1]
            except:
                runner_up_list[f"User not found_{temp}"] = i[1]
                temp += 1
        for i in iconsd:
            if kk != 0:
                x += diff + im_radius

            base.paste(i, (x, y), i)
            base.paste(decorator_icon, (x - 15, y - 55), decorator_icon)
            s1_xx = x + 20
            s1_yy = y + 160
            base.paste(s1, (s1_xx, s1_yy), s1)

            font_size = 100
            title_text = ImageFont.truetype(font_to_use, font_size)
            # Processing long names
            if len(names[kk]) > 12:
                nm = names[kk].split(" ")
                if len(nm) > 1:
                    nm = nm[0] + "\n" + " ".join(nm[1:])
                else:
                    nm = nm[0]
                    nm1 = nm[0:int(len(nm) / 2)]
                    nm2 = nm[int(len(nm) / 2):]
                    nm = nm1 + "-\n" + nm2
                names[kk] = nm

            while True:
                a, b, c, d = title_text.getbbox(names[kk])
                font_size -= 1
                title_text = ImageFont.truetype(font_to_use, font_size)
                if c < s1_x and d < s1_y:
                    break
            if len(names[kk]) <= 5:
                font_size -= 10
            title_text = ImageFont.truetype(font_to_use, font_size - 5)
            a, b, c, d = title_text.getbbox(names[kk])
            tx = s1_xx + ((s1_x - c) / 2)
            ty = s1_yy + ((s1_y - d) / 2)
            if len(names[kk]) >= 12:
                font_size += 15
                title_text = ImageFont.truetype(font_to_use, font_size - 5)
                a, b, c, d = title_text.getbbox(names[kk])
                tx = s1_xx + ((s1_x - c) / 2) + 70
                ty = s1_yy + ((s1_y - d) / 2) - 17
            ImageDraw.Draw(base).text((tx, ty),
                                      names[kk],
                                      'rgb(0,0,0)',
                                      font=title_text,
                                      spacing=10)
            kk += 1

        # Runners_up
        rx = 120
        ry = 550

        k = 0
        font_size = 35
        title_text = ImageFont.truetype(font_to_use, font_size - 5)
        #Finding largest entry
        largest = ""
        for i in runner_up_list:
            if len(largest) < len(i):
                largest = i
        for i in runner_up_list:
            num_of_spaces = len(largest) - len(i)
            k_s = 1
            if k == 9:
                k_s = 0
            text = f"{k+1}.{' '*k_s}{i}:{' '*num_of_spaces} {runner_up_list[i]}"
            if k:
                ry += 40
            k += 1

            ImageDraw.Draw(base).text((rx, ry),
                                      text,
                                      'rgb(255,255,255)',
                                      font=title_text,
                                      spacing=10)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        await ctx.channel.send("Send the channel id to send the image to.")
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        try:
            chnl = int(msg.content)
            chnl = self.bot.get_channel(chnl)
        except:
            await msg.reply("Not a valid channel id")
            return
        await ctx.channel.send("Any additional text?\nSend `no` for none.")
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        try:
            if msg.content.lower() == "no":
                addText = ""
            else:
                addText = (msg.content)
        except:
            await msg.reply("Kuch to gadbad hui")
            return

        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            await chnl.send(
                f"{addText}",
                file=discord.File(fp=image_binary, filename='lb_image.png'))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(ImageFun(bot))
