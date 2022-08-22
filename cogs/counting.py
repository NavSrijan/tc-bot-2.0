from discord.ext import commands
from discord import AllowedMentions, Embed
from database import Database_message_bank, DATABASE_URL
import os


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
    @commands.hybrid_command(name="lb_week", aliases=["leaderboard_week", "leaderboard_w", "lb_w"])
    async def lb_week(self, ctx, number_of_entries: int=10):
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
