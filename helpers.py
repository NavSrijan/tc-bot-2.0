import discord

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
