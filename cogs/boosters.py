from discord.ext import commands
import discord
from functions import load, save
from helpers import basic_embed
import os

class Boosters(commands.Cog):
    """Commands for boosters"""
    def __init__(self, bot):
        self.bot = bot

    def load_nitro_roles(self):
        return load("variables/nitro_roles.pkl")
    def save_nitro_roles(self, roles):
        return save(roles,"variables/nitro_roles.pkl")

    @commands.command(name="c")
    async def c(self, ctx):
        """Useless"""
        await ctx.reply("Send the six digit color you wish to have.")
        def check(message):
            return message.author == ctx.message.author and message.channel == ctx.message.channel
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        color = msg.content
        emb = discord.Embed(title="Hi!", color=discord.Color.from_str(color))
        await ctx.channel.send(embed=emb)

    @commands.command(name="custom_role")
    async def custom_role(self, ctx):
        """Custom role for the user"""
        try:
            nitro_roles = self.load_nitro_roles()
        except:
            await ctx.reply(embed=basic_embed(desc="There is some error on my end. Contact staff."))
        roles = []
        for i in ctx.message.author.roles:
            roles.append(i.id)
        if 988445679426867200 in roles:
            def check(message):
                return message.author == ctx.message.author and message.channel == ctx.message.channel

            await ctx.reply(embed=basic_embed(desc="What should be the roles name?"))
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            name = msg.content

            await ctx.reply(embed=basic_embed(desc="Send the HEX of the color you wish to have.\nEx: #cf691b"))
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            color = msg.content
            try:
                color = discord.Color.from_str(color)
            except:
                await msg.reply(embed=basic_embed(desc="Not in the correct format."))
                return

            ### Deleting old role
            intersection = list(set(roles) & set(nitro_roles))
            if len(intersection)>0:
                for i in ctx.message.author.roles:
                    if i.id == intersection[0]:
                         await i.delete()
                         nitro_roles.remove(i.id)

            ### Role Creation
            guild = ctx.guild
            new_role = await guild.create_role(name=name, color=color, hoist=True)
            await ctx.message.author.add_roles(new_role)

            nitro_roles.append(new_role.id)
            self.save_nitro_roles(nitro_roles)

        else:
            await ctx.message.reply(embed=basic_embed(desc="Shouldn't you be boosting first?"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)

    
async def setup(bot):
    await bot.add_cog(Boosters(bot))