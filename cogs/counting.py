from discord.ext import commands
import discord
from discord import AllowedMentions, Embed
from database import Database_message_bank, DATABASE_URL
import os
from helpers import send_image
from PIL import ImageFont, ImageDraw, Image


class Counting(commands.Cog):
    """Hehe, you can't use these."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)

    @commands.hybrid_command(name="active")
    async def active(self, ctx, user: discord.Member = None):
        """Know which day of the week you're most active!"""
        if not user:
            user = ctx.author
        db = Database_message_bank(DATABASE_URL, "message_bank")
        data = db.get_week_activity(user.id)

        colors = [
            '#ffc599', '#ffb780', '#ffa966', '#ff9a4d', '#ff8c33', '#ff7d19',
            '#e66400', '#cc5900', '#b34e00', '#994300', '#803800', '#662c00'
        ]

        im_size = (640, 420)

        font = ImageFont.truetype("B612Mono-Bold", 12)
        im = Image.new('RGBA', (im_size[0], im_size[1]))
        draw = ImageDraw.Draw(im)

        rect_width = im_size[0] / 7
        days = [
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday"
        ]

        x, y = 0, 0
        j = 0
        for i in data:
            x = rect_width * int(i[0])
            draw.rectangle([(x, y), (x + rect_width, im_size[1])],
                           fill=colors[j])
            draw.text((x + 10, im_size[1] - 50),
                      days[int(i[0])],
                      fill="black",
                      font=font)
            j+=1

        await ctx.reply(file=send_image(im))

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="lb", aliases=["leaderboard"])
    async def lb(self, ctx):
        """Get the lb for the day"""
        db = Database_message_bank(DATABASE_URL, "message_bank")

        allowed_mentions = AllowedMentions(
            users=False,  # Whether to ping individual user @mentions
            everyone=False,  # Whether to ping @everyone or @here mentions
            roles=False,  # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
        )

        #await ctx.channel.send(db.get_data(num=10), allowed_mentions=allowed_mentions)
        await ctx.channel.send(db.get_data(num=10))

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(
        name="lb_week", aliases=["leaderboard_week", "leaderboard_w", "lb_w"])
    async def lb_week(self, ctx, number_of_entries: int = 10):
        """Get the lb for the week."""
        db = Database_message_bank(DATABASE_URL, "message_bank")

        allowed_mentions = AllowedMentions(
            users=False,  # Whether to ping individual user @mentions
            everyone=False,  # Whether to ping @everyone or @here mentions
            roles=False,  # Whether to ping role @mentions
            replied_user=False,  # Whether to ping on replies to messages
        )

        #await ctx.channel.send(db.get_week_data(), allowed_mentions=allowed_mentions)
        await ctx.reply(db.get_week_data(num=number_of_entries))

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="lb_week_embed")
    async def lb_week_embed(self, ctx):
        """Get an embed with the weekly lb"""
        db = Database_message_bank(DATABASE_URL, "message_bank")

        all_users = db.get_week_data(to_send=False)

        j = 1
        desc = ""
        chunk = "{}: <@{}>\nPoints: `{}`\n"
        for i in all_users[:10]:
            desc += chunk.format(j, i[0], i[1]) + "\n"
            j += 1

        emb = Embed(title="Leaderboard", description=desc)
        await ctx.channel.send(embed=emb)


async def setup(bot):
    await bot.add_cog(Counting(bot))
