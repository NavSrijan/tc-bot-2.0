from discord.ext import commands
import random
import csv
import os


class Welcome(commands.Cog):
    """Basic hello commands"""

    def __init__(self, bot):
        self.bot = bot
        with open("assets/random_data/welcome_messages.csv", "r") as f:
            self.welcomeMessages = list(csv.reader(f))


    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Welcomes the new user who joins.
        """
        channel = self.bot.get_channel(int(self.bot.config['commands']['welcome']['welcome_channel']))
        self_roles_channel = int(self.bot.config['commands']['welcome']['self_roles_channel'])

        arrow1 = "<a:animatearrow:976181084578517032>"
        arrow2 = "<a:arrowrigh23t:976181875083198464>"

        welcomeMessage = f"""
╭━─━─━─━─  ≪✠≫  ─━─━─━─━╮
{arrow2} HEY <@{member.id}>
{arrow2} WELCOME TO SOCIAL HIDEOUT
{arrow2} PLEASE GRAB YOUR <#{self_roles_channel}>
╰━─━─━─━─  ≪✠≫  ─━─━─━─━╯

**{random.choice(self.welcomeMessages)[0]}**
"""
        await channel.send(welcomeMessage)

        def check(message):
            return message.author == member

        tc_emoji = "<a:tc_excited:995961225525608500>"

        message = await self.bot.wait_for('message', check=check, timeout=300)
        await message.add_reaction(tc_emoji)

    #@commands.command(name="hello", aliases=["hi", "greetings", "namaste"])
    @commands.hybrid_command(name="hello")
    async def hello(self, ctx):
        """Say hello to the bot!"""
        await ctx.send(f"Hello! {ctx.message.content[5:]}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)

    @commands.hybrid_command(name="yo")
    async def yo(self, ctx):
        """What help do you need for this?"""
        await ctx.reply("yoyo")


async def setup(bot):
    await bot.add_cog(Welcome(bot))
