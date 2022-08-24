import discord
from discord.ext import commands


class Help(commands.Cog):
    """Sends this help message"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", aliases=["h"])
    async def help(self, ctx, command=None):
        prefix = "$"
        # Show the main help message
        if command is None:
            # Preparing the description
            desc = ""
            emb = discord.Embed(title="Help",
                                description=desc,
                                color=discord.Color.gold())
            blocked_cogs = ["Suggestion"]
            for cog in self.bot.cogs:
                if cog not in blocked_cogs:
                    desc += cog + "\n"
                    for cmd in self.bot.get_cog(cog).get_commands():
                        if not cmd.hidden:
                            desc += "`" + cmd.name + "` "
                    desc = desc[0:-2]
                    desc += "`\n"

            desc += f"\n\n For more info about a command use {prefix}help <command>.\nAuthor: <@302253506947973130>"

            emb.description = desc
        elif command is not None:
            # Getting the help for a particular command or module
            done = False
            for cog in self.bot.cogs:
                if cog.lower() == command.lower():
                    emb = discord.Embed(title=cog,
                                        description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.gold())

                    for cmd in self.bot.get_cog(cog).get_commands():
                        if not cmd.hidden:
                            emb.add_field(name=f"{prefix}{cmd.name}",
                                          value=cmd.help,
                                          inline=False)
                    done = True
                    break
            if not done:
                for cog in self.bot.cogs:
                    for cmd in self.bot.get_cog(cog).get_commands():
                        if not cmd.hidden and cmd.name == command:
                            emb = discord.Embed(title=cmd.name,
                                                description=cmd.help,
                                                color=discord.Color.gold())
                            done = True
                            break
            if not done:
                emb = discord.Embed(description="Command not found.",
                                    color=discord.Color.red())

        else:
            emb = discord.Embed(description="Supply only one argument.",
                                color=discord.Color.red())

        await ctx.reply(embed=emb)


async def setup(bot):
    await bot.add_cog(Help(bot))
