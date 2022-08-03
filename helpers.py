import discord
import pickle as pkl
from database import Database_suggestions, DATABASE_URL
from PIL import Image
import requests
from functions import download_and_return_image

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Green', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('This is green.', ephemeral=True)

    @discord.ui.button(label='Red', style=discord.ButtonStyle.red, custom_id='persistent_view:red')
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('This is red.', ephemeral=True)

    @discord.ui.button(label='Grey', style=discord.ButtonStyle.grey, custom_id='persistent_view:grey')
    async def grey(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('This is grey.', ephemeral=True)

class VoteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Upvote', style=discord.ButtonStyle.green, custom_id="VoteGreen")
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id, interaction.user.id, resp=1)
            except:
                await interaction.response.send_message('Haven\'t you already responded?', ephemeral=True)
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))
            emb.description = "\n\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

    @discord.ui.button(label='Downvote', style=discord.ButtonStyle.red, custom_id='VoteRed')
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id, interaction.user.id, resp=0)
            except:
                await interaction.response.send_message('Haven\'t you already responded?', ephemeral=True)
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))
            emb.description = "\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

class VoteViewForEmoji(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.voteLimit = 2
    async def set_emoji(self, interaction, url):
        img = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
        img = img.resize((32,32))
        img.save("assets/images/em1.png")
        with open("assets/images/em1.png","rb") as f:
            image = f.read()
        await interaction.guild.create_custom_emoji(name="em1", image=image)
        await interaction.message.delete()

    @discord.ui.button(label='Upvote', style=discord.ButtonStyle.green, custom_id="VoteGreenForEmoji")
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id, interaction.user.id, resp=1)
            except:
                await interaction.response.send_message('Haven\'t you already responded?', ephemeral=True)
                emb = interaction.message.embeds[0]
                up = len(db.fetch_interactions_id(interaction.message.id, 1))
                if up>=self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            emb = interaction.message.embeds[0]
            desc = emb.description
            lines = "✅ ---> {}\n\n❌ ---> {}"
            suggs = desc.split("\n")[0]
            up = len(db.fetch_interactions_id(interaction.message.id, 1))
            down = len(db.fetch_interactions_id(interaction.message.id, 0))

            try:
                if up>=self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            except:
                pass


            emb.description = "\n\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

    @discord.ui.button(label='Downvote', style=discord.ButtonStyle.red, custom_id='VoteRedForEmoji')
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            db = Database_suggestions(DATABASE_URL, "suggestions")
            try:
                db.insert_message_id(interaction.message.id, interaction.user.id, resp=0)
            except:
                await interaction.response.send_message('Haven\'t you already responded?', ephemeral=True)
                try:
                    emb = interaction.message.embeds[0]
                    up = len(db.fetch_interactions_id(interaction.message.id, 1))
                    if up>=self.voteLimit:
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
                if up>=self.voteLimit:
                    await self.set_emoji(interaction, emb.image.url)
                    return
            except:
                pass


            emb.description = "\n".join([suggs, lines.format(up, down)])

            await interaction.response.edit_message(embed=emb)
        except Exception as e:
            print(e)

def basic_embed(title="", desc="", color=discord.Color.green(), fields={}, footer=None, author=None, image_url=None, thumbnail_url=None):
    emb = discord.Embed(title=title, description=desc, color=color)

    if footer:
        emb.set_footer(footer)
    if author:
        emb.set_author(author)
    if image_url:
        emb.set_image(url=image_url)
    if thumbnail_url:
        emb.set_thumbnail(url=thumbnail_url)
    
    if len(fields)>0:
        for i in fields:
            emb.add_field(i, fields[i])

    return emb
