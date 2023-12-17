import discord
import pickle as pkl
#from database import Database_suggestions, DATABASE_URL
from PIL import Image, ImageFont, ImageDraw
import requests
from functions import download_and_return_image
from io import BytesIO
import textwrap


class PersistentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Green',
                       style=discord.ButtonStyle.green,
                       custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        await interaction.response.send_message('This is green.',
                                                ephemeral=True)

    @discord.ui.button(label='Red',
                       style=discord.ButtonStyle.red,
                       custom_id='persistent_view:red')
    async def red(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
        await interaction.response.send_message('This is red.', ephemeral=True)

    @discord.ui.button(label='Grey',
                       style=discord.ButtonStyle.grey,
                       custom_id='persistent_view:grey')
    async def grey(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        await interaction.response.send_message('This is grey.',
                                                ephemeral=True)


class VoteView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Upvote',
                       style=discord.ButtonStyle.green,
                       custom_id="VoteGreen")
    async def green(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id,
                                     interaction.user.id,
                                     resp=1)
            except:
                await interaction.response.send_message(
                    'Haven\'t you already responded?', ephemeral=True)
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))
            emb.description = suggs + "\n\n" + lines.format(
                up, down)  #"\n\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

    @discord.ui.button(label='Downvote',
                       style=discord.ButtonStyle.red,
                       custom_id='VoteRed')
    async def red(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id,
                                     interaction.user.id,
                                     resp=0)
            except:
                await interaction.response.send_message(
                    'Haven\'t you already responded?', ephemeral=True)
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))
            emb.description = suggs + "\n\n" + lines.format(up, down)

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)


class VoteViewForEmoji(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.voteLimit = 4

    async def set_emoji(self, interaction, url):
        img = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
        img = img.resize((32, 32))
        img.save("assets/images/em1.png")
        with open("assets/images/em1.png", "rb") as f:
            image = f.read()
        await interaction.guild.create_custom_emoji(name="em1", image=image)
        await interaction.message.delete()

    @discord.ui.button(label='Upvote',
                       style=discord.ButtonStyle.green,
                       custom_id="VoteGreenForEmoji")
    async def green(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id,
                                     interaction.user.id,
                                     resp=1)
            except:
                await interaction.response.send_message(
                    'Haven\'t you already responded?', ephemeral=True)
                emb = interaction.message.embeds[0]
                up = len(db.fetch_interactions_id(interaction.message.id, 1))
                if up >= self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))

            try:
                if up >= self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            except:
                pass

            emb.description = "\n\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

    @discord.ui.button(label='Downvote',
                       style=discord.ButtonStyle.red,
                       custom_id='VoteRedForEmoji')
    async def red(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id,
                                     interaction.user.id,
                                     resp=0)
            except:
                await interaction.response.send_message(
                    'Haven\'t you already responded?', ephemeral=True)
                try:
                    emb = interaction.message.embeds[0]
                    up = len(
                        db.fetch_interactions_id(interaction.message.id, 1))
                    if up >= self.voteLimit:
                        await self.set_emoji(interaction, emb.image.url)
                        return
                except:
                    pass

            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))

            try:
                if up >= self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            except:
                pass

            emb.description = "\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)


def basic_embed(title="",
                desc="",
                color=discord.Color.green(),
                fields=[],
                footer=None,
                author=None,
                image_url=None,
                thumbnail_url=None,
                icon_url=None):
    emb = discord.Embed(title=title, description=desc, color=color)

    if footer:
        emb.set_footer(footer)
    if author:
        if author_icon_url != None:
            emb.set_author(author, icon_url=author_icon_url)
        else:
            emb.set_author(author)
    if image_url:
        emb.set_image(url=image_url)
    if thumbnail_url:
        emb.set_thumbnail(url=thumbnail_url)

    if len(fields) > 0:
        for i in fields:
            emb.add_field(i[0], i[1])

    return emb


def center_text(base,
                text,
                font_to_use,
                shadowcolor="black",
                fillcolor="white",
                textwrap_=False,
                name="",
                font_diff=0):
    title_text = ImageFont.truetype(font_to_use, 80)
    xc, yc = base.size
    a, b, c, d = title_text.getbbox(text)

    font_size = 100
    tx, ty = 0, yc - 500
    while c - a > xc:
        font_size -= 1
        title_text = ImageFont.truetype(font_to_use, font_size)
        a, b, c, d = title_text.getbbox(text)
        tx = int((xc - (c - a)) / 2)

    if len(text) >= 4:
        to_subtract_y = 300
    else:
        to_subtract_y = 200

    if textwrap_ is True:
        text = textwrap.wrap(text, width=25)
        text = " \n".join(text)
    else:
        name = "\n" + name.center(len(text), " ")
        text += name

    ty = yc - to_subtract_y
    x, y = tx, ty
    shadowcolor = "black"
    fillcolor = "white"
    font = ImageFont.truetype(font_to_use, font_size + font_diff)
    draw = ImageDraw.Draw(base)
    draw.text((x - 2, y - 2), text, font=font, fill=shadowcolor)
    draw.text((x + 2, y - 2), text, font=font, fill=shadowcolor)
    draw.text((x - 2, y + 2), text, font=font, fill=shadowcolor)
    draw.text((x + 2, y + 2), text, font=font, fill=shadowcolor)

    draw.text((x, y), text, font=font, fill=fillcolor)
    return base


def send_image(base, name="modiji.png"):
    with BytesIO() as image_binary:
        base.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename=name)
        return file


def get_percentage_image(per):
    base = Image.open(f'assets/images/Synergy/percentage_bg.png')

    font_to_use = "assets/fonts/B612Mono-Bold.ttf"
    font_to_use = ImageFont.truetype(font_to_use, 80)

    ImageDraw.Draw(base).text((145, 100),
                              str(per),
                              'rgb(0,0,0)',
                              font=font_to_use,
                              spacing=10)
    with BytesIO() as image_binary:
        base.save(image_binary, 'PNG')
        image_binary.seek(0)
        filename="image_percentage_synergy.png"
        file = discord.File(fp=image_binary, filename=filename)
        return file, filename
    return file
