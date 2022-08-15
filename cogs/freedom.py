from discord.ext import commands
import os


class Freedom(commands.Cog):
    """Basic hello commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="how", aliases=["how's", "hows", "htj"])
    async def Josh(self, ctx, *args):
        """JOSH!"""
        alia=["how's the josh", "hows the josh?", "how's the josh?", "htj?", "htj"]
        for i in alia:
            if ctx.message.content[1:].lower().startswith(i):
                await ctx.send("**HIGH SIR!!!**")
                return


async def setup(bot):
    await bot.add_cog(Freedom(bot))
