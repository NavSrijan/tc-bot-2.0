from discord.ext import commands
import discord
from database import DB_messages, DATABASE_URL
from PIL import Image, ImageFont, ImageDraw
import os
import requests
from io import BytesIO


def icon(image_object, image_size):
    
    #for i in ["assets/pfp1.png","assets/pfp2.png","assets/pfp3.png"]:
    #im = Image.open(image_path).convert('RGBA')
    im = image_object

    # start to make the photo square
    width,height = im.size
    crop_size = min(width,height)
    
    #length to crop from each side
    left = (width - crop_size)/2
    right = (width + crop_size)/2
    top = (height - crop_size)/2
    bottom = (height + crop_size)/2
    
    im = im.crop((left,top,right,bottom))
    
    # resize icon depending on image_size
    im = im.resize((image_size,image_size), Image.ANTIALIAS)
    #im = im.rotate(0)
    
    #create a round border
    bigsize = (image_size*3,image_size*3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    
    return im



class ImageFun(commands.Cog):
    """Basic hello commands"""
    def __init__(self, bot: commands.Bot):
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
        ImageDraw.Draw(base).text((0, 550), text, 'rgb(255,69,0)', font=title_text, spacing=10)
        
        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(file=discord.File(fp=image_binary, filename='modiji.png'))


    
    @commands.has_permissions(kick_members=True)
    @commands.command(name="lb_image")
    async def lb_image(self, ctx):
        db = DB_messages(DATABASE_URL, "message_bank")
        lb = db.get_week_data(to_send=False)

        j = 0
        for i in lb:
            if i[0] in [908309845634089001, 674289303374790666, 302253506947973130, 775964252783640586, 681918482681823255]:
                lb.pop(j)
            j+=1

        top_2 = lb[0:2]
        top_10 = lb[0:10]

        im_radius = 200

        background_image = Image.open('assets/bg.png')
        background_image = background_image.resize((720, 1080) ,Image.ANTIALIAS)
        base = Image.new('RGB', background_image.size)
        base.paste(background_image)

        title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', 70)
        ImageDraw.Draw(base).text((280, 20), ' TEENAGE\nCOMMUNITY', 'rgb(255,255,255)', font=title_text, spacing=10)

        tc = Image.open("assets/tc_f.png").convert('RGBA')
        tc = tc.resize((im_radius-40, im_radius-40), Image.ANTIALIAS)
        base.paste(tc, (80, 20), tc)

        ### Get icons
        iconsd = []
        for i in top_2:
            url = ctx.message.guild.get_member(int(i[0])).avatar.url
            im = Image.open(requests.get(url, stream=True).raw)
            dw = icon(im, im_radius)
            iconsd.append(dw)

        decorator_icon = Image.open("assets/f1.png").convert('RGBA')
        decorator_icon = decorator_icon.resize((im_radius-40, im_radius-40), Image.ANTIALIAS)

        s1_y = 65
        s1_x = int(s1_y*2.7)
        s1 = Image.open("assets/s1.png").convert('RGBA')
        s1 = s1.resize((s1_x, s1_y), Image.ANTIALIAS)



        x=120
        y=240

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
            #runner_up_list[i[0]] = i[1]
            try:
                runner_up_list[ctx.message.guild.get_member(int(i[0])).name] = i[1]
            except:
                runner_up_list[f"User not found_{temp}"] = i[1]
                temp+=1
        for i in iconsd:
            if kk!=0:
                x+=diff+im_radius

            base.paste(i, (x, y), i)
            base.paste(decorator_icon, (x-15, y-55), decorator_icon)
            s1_xx = x+20
            s1_yy = y+160
            base.paste(s1, (s1_xx, s1_yy), s1)
            
            font_size = 100
            title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', font_size)
            # Processing long names
            if len(names[kk])>12:
                nm = names[kk].split(" ")
                if len(nm)>1:
                    nm = nm[0] + "\n" + " ".join(nm[1:])
                else:
                    nm = nm[0]
                    nm1 = nm[0:int(len(nm)/2)]
                    nm2 = nm[int(len(nm)/2):]
                    nm = nm1+"-\n"+nm2
                names[kk] = nm

            while True:
                a,b,c,d = title_text.getbbox(names[kk])
                font_size-=1
                title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', font_size)
                if c<s1_x and d<s1_y:
                    break
            if len(names[kk])<=5:
                font_size-=10
            title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', font_size-5)
            a,b,c,d = title_text.getbbox(names[kk])
            tx = s1_xx + ((s1_x-c)/2)
            ty = s1_yy + ((s1_y-d)/2)
            if len(names[kk])>=12:
                font_size+=15
                title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', font_size-5)
                a,b,c,d = title_text.getbbox(names[kk])
                tx = s1_xx + ((s1_x-c)/2)+70
                ty = s1_yy + ((s1_y-d)/2)-17
            ImageDraw.Draw(base).text((tx, ty), names[kk], 'rgb(0,0,0)', font=title_text, spacing=10)
            kk+=1
        
        # Runners_up
        rx = 120
        ry = 550

        k = 0
        font_size = 35
        title_text = ImageFont.truetype('assets/B612Mono-Bold.ttf', font_size-5)
        #Finding largest entry
        largest = ""
        for i in runner_up_list:
            if len(largest)<len(i):
                largest = i
        for i in runner_up_list:
            num_of_spaces = len(largest)-len(i)
            k_s = 1
            if k==9:
                k_s = 0
            text = f"{k+1}.{' '*k_s}{i}:{' '*num_of_spaces} {runner_up_list[i]}"
            if k:
                ry += 40
            #elif k==6:
            #    rx += 100
            #    ry = 500
            #else:
            #    ry += 20
            k+=1

            ImageDraw.Draw(base).text((rx, ry), text, 'rgb(255,255,255)', font=title_text, spacing=10)

        with BytesIO() as image_binary:
            base.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(file=discord.File(fp=image_binary, filename='lb_image.png'))

        #base.show()


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

async def setup(bot):
    await bot.add_cog(ImageFun(bot))
