from discord.ext import commands
import discord
from functions import utc_to_ist
import datetime
import time
from helpers import basic_embed
import random
import asyncio


class Mod(commands.Cog):
    """Hehe, you can't use these."""

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="test", hidden=True)
    async def test(self, ctx):
        emb = basic_embed(
            desc="hi",
            color=discord.Color.red(),
            image_url=
            "https://tenor.com/view/wow-very-dangerous-wow-berry-dangerous-very-dangerous-ayub-kha98-tiktoker-gif-23393447"
        )
        await ctx.reply(embed=emb)

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="torture")
    async def torture(self, ctx, user: discord.Member, time_to_delete=60):
        """Keep deleting a users message for a certain amount of time."""
        if user:
            await ctx.reply("Okay.... :smirk:")
        else:
            await ctx.reply("Mention someone.", ephemeral=True)
            return

        self.bot.to_torture.append(user)
        total_timeout = time_to_delete
        await asyncio.sleep(total_timeout)
        try:
            self.bot.to_torture.remove(user)
        except:
            pass
        await ctx.reply("Done.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="remove_torture")
    async def remove_torture(self, ctx, user: discord.Member):
        """Remove a person from torture."""
        try:
            self.bot.to_torture.remove(user)
            await ctx.reply("Done.")
        except:
            await ctx.reply("User not found in the torture list.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="lock")
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Locks the channel
        """
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.message.guild.default_role,
                                      read_messages=True,
                                      send_messages=False)
        await channel.send("The channel has been locked.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="unlock")
    async def unlock_channel(self, ctx):
        """
        Unlocks the channel
        """
        await ctx.channel.set_permissions(ctx.message.guild.default_role,
                                          read_messages=True,
                                          send_messages=True)
        await ctx.channel.send("The channel has been unlocked.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="kick")
    async def kick(self, ctx, user: discord.Member):
        """Kick a member"""
        gifs = [
            "https://tenor.com/view/throw-him-out-gif-14876020",
            "https://tenor.com/view/berg-ankit-kick-out-throw-out-get-out-of-here-gif-20129402",
            "https://tenor.com/view/spongebob-squarepants-get-out-kick-out-booted-bye-felicia-gif-13565963",
            "https://tenor.com/view/anime-love-after-world-domination-kick-kicking-kick-out-gif-25869776",
            "https://tenor.com/view/dont-mess-with-the-zohan-you-no-te-metas-con-pissed-off-kick-chair-gif-15621872",
            "https://tenor.com/view/kirk-star-trek-kick-gif-26008018",
            "https://tenor.com/view/oh-yeah-high-kick-take-down-fight-gif-14272509",
            "https://tenor.com/view/bad-mom-grandma-baby-kicking-i-love-children-gif-23173847"
        ]
        if user:
            member = user
        else:
            await ctx.reply("Mention someone.")
            return
        name = member.name
        try:
            await member.kick()
            await ctx.channel.send(random.choice(gifs))
            await ctx.reply(f"`{name} has been kicked.`")
        except:
            await ctx.reply("Sorry but, I don't have the permissions.")

    @commands.has_permissions(ban_members=True)
    @commands.hybrid_command(name="ban")
    async def ban(self, ctx, user: discord.Member):
        """Ban a member"""
        gifs = [
            "https://tenor.com/view/among-us-ban-among-us-ban-imposter-ban-gif-18884723",
            "https://tenor.com/view/spongebob-ban-pubg-lite-banned-rainbow-gif-16212382",
            "https://tenor.com/view/ban-banned-sakura-anime-spray-gif-22585378",
            "https://tenor.com/view/elmo-fire-ban-syntheticllama-gif-21044291",
            "https://tenor.com/view/when-your-team-too-good-ban-salt-bae-gif-7580925",
            "https://tenor.com/view/bane-no-banned-and-you-are-explode-gif-16047504"
        ]
        if user:
            member = user
        else:
            await ctx.reply("Mention someone.")
            return
        name = member.name
        try:
            await member.ban()
            await ctx.channel.send(random.choice(gifs))
            await ctx.reply(f"{name} has been banned.")
        except:
            await ctx.reply("Sorry but, I don't have the permissions.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="embed")
    async def create_embed(self, ctx):
        """Generate an embed to send."""
        await ctx.reply("Starting embed creation.")

        member = ctx.message.author
        channel = ctx.message.channel

        def check(message):
            return message.author == member and message.channel == channel

        a = "🇦"
        b = "🇧"

        msg = await ctx.message.channel.send(
            "A. Movie announcement or B. General announcement?")
        await msg.add_reaction(a)
        await msg.add_reaction(b)

        def check_reaction(reaction, user):
            return user == member and reaction.emoji in [
                a, b
            ] and user.bot == False

        reaction = await self.bot.wait_for("reaction_add",
                                           check=check_reaction,
                                           timeout=60)
        emoji = reaction[0].emoji

        if emoji == a:
            await ctx.message.channel.send("Movie name?")
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            movieName = msg.content

            await ctx.message.channel.send("Movie duration?")
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            movieDuration = msg.content

            #await ctx.message.channel.send("Time?")
            #msg = await self.bot.wait_for('message', check = check, timeout=180)
            #ttime = msg.content

            await ctx.channel.send("Likhna kya hai?")
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            try:
                if msg.content.lower() == "no":
                    customText = ""
                else:
                    customText = (msg.content)
            except:
                await msg.reply("Kuch to gadbad hui")
                return

            desc = f"""
{customText}

**•Movie name ->**
`{movieName}`
**•Duration ->**
`{movieDuration}`
"""
            image_url = "https://media.discordapp.net/attachments/894495731451297852/992826041422848060/images_13.jpeg?width=475&height=475"
            #thumbnail_url = "https://cdn.discordapp.com/attachments/992882759330701323/995960581892870245/standard_1.gif"

            emb = discord.Embed(title="Movie Alert!", description=desc)
            emb.set_image(url=image_url)
            #emb.set_thumbnail(url=thumbnail_url)
            emb.set_footer(text=utc_to_ist(datetime.datetime.utcnow()).date())

            await ctx.message.channel.send("Which channel to send to?")
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            channel_to_send_to = int(msg.content[2:-1])

            await msg.reply(embed=emb)
            msg = await ctx.message.channel.send("Is this correct?")
            await msg.add_reaction(a)
            await msg.add_reaction(b)

            def check_reaction(reaction, user):
                return user == member and reaction.emoji in [
                    a, b
                ] and user.bot == False

            reaction = await self.bot.wait_for("reaction_add",
                                               check=check_reaction,
                                               timeout=60)
            emoji = reaction[0].emoji
            color = discord.Color.from_str("#4ce4e7")
            emb.color = color

            await ctx.channel.send("Any additional text?\nSend `no` for none.")
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            try:
                if msg.content.lower() == "no":
                    addText = ""
                else:
                    addText = (msg.content)
            except:
                await msg.reply("Kuch to gadbad hui")
                return
            if emoji == a:
                try:
                    chnl = self.bot.get_channel(channel_to_send_to)
                    await chnl.send(addText, embed=emb)
                except:
                    await msg.reply("Channel wrong")
            else:
                await msg.reply("Aborted!")

        elif emoji == b:
            await ctx.message.channel.send("Still developing this....")
        else:
            await ctx.message.channel.send(":hehe:")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="load")
    async def load_cog(self, ctx, *args):
        """Load cog"""
        extension = args[0]
        try:
            await self.bot.load_extension('cogs.' + extension)
            await ctx.reply(f"{extension} has been loaded.")
        except:
            await ctx.reply(f"{extension} is already loaded.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="mass_role")
    async def mass_role(self, ctx, *args):
        """Adds a role to every user in the server."""
        await ctx.reply("Send the role id to add to everyone.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check, timeout=60)
        try:
            role_id = int(msg.content)
            role = msg.guild.get_role(role_id)
        except:
            await ctx.channel.send("Not a valid role id.")
            return
        await msg.reply(
            "Are you sure? This will give everyone in this server this role. y/n"
        )
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        if msg.content.lower() != "y":
            await msg.reply("Okay! Aborting.")
            return

        members = ctx.guild.members
        try:
            for i in members:
                try:
                    await i.add_roles(role)
                    print(i.name)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(e)
        except:
            await ctx.channel.send("Permission missing.")
        await ctx.channel.send("Done!")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="mass_derole")
    async def mass_derole(self, ctx, *args):
        """Adds a role to every user in the server."""
        await ctx.reply("Send the role id to remove from everyone.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check, timeout=60)
        try:
            role_id = int(msg.content)
            role = msg.guild.get_role(role_id)
        except:
            await ctx.channel.send("Not a valid role id.")
            return
        await msg.reply(
            "Are you sure? This will remove this role from everyone in this server. y/n"
        )
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        if msg.content.lower() != "y":
            await msg.reply("Okay! Aborting.")
            return

        members = ctx.guild.members
        try:
            for i in members:
                await i.remove_roles(role)
                print(i.name)
                await asyncio.sleep(1)
        except:
            await ctx.channel.send("Permission missing.")
        await ctx.channel.send("Done!")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="unload")
    async def unload_cog(self, ctx, *args):
        """Unload cog"""
        extension = args[0]
        try:
            await self.bot.unload_extension('cogs.' + extension)
            await ctx.reply(f"{extension} has been unloaded.")
        except:
            await ctx.reply(f"{extension} is already unloaded.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_group(name="config")
    async def config(self, ctx):
        """Change the config"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @config.command(name="show")
    async def show_config(self, ctx):
        """Displays all the config variables"""
        config = self.bot.config
        desc = ""
        for section in config:
            if section == "name":
                name = config[section]
                desc += f"**{name}**\n\n"
            elif section == "bot":
                desc += f"`prefix`: {config[section]['prefix']}\n\n"
            elif section == "commands":
                desc += "\n**commands**\n"
                for con in config[section]:
                    desc += "\n"
                    for sec_2 in config[section][con]:
                        desc += f"`{sec_2}`: {config[section][con][sec_2]}\n"
            elif type(config[section]) is dict:
                desc += f"`{section}`\n"
                for sec_2 in config[section]:
                    if isinstance(config[section][sec_2], list):
                        desc += f"{sec_2}\n`"
                        for el in config[section][sec_2]:
                            desc += el + "\n"
                        desc += "`"
                    else:
                        desc += f"`{sec_2}`: {config[section][sec_2]}\n"
        emb = basic_embed(desc=desc)
        await ctx.reply(embed=emb)

    @commands.has_permissions(kick_members=True)
    @config.command(name="change")
    async def change_config(self, ctx, group_name, variable, value):
        """Change the commands section of the config.
        Syntax: $config change <name of group> <variable to change> <value>"""
        if group_name and variable and value:
            try:
                group = group_name
                var = variable
                value = value

                if isinstance(self.bot.config['commands'][group][var], int):
                    try:
                        value = int(value)
                        self.bot.config['commands'][group][var] = value
                        self.bot.config_obj.dump_config()
                        await ctx.reply(f"{var} has been changed to {value}.")
                    except:
                        await ctx.reply("Not a correct value it seems.")
                else:
                    self.bot.config['commands'][group][var] = value
                    self.bot.config_obj.dump_config()
                    await ctx.reply(f"{var} has been changed to {value}.")
            except:
                await ctx.reply("Syntax error.")

        else:
            await ctx.reply(
                "What to change?\nSyntax: $config change <name of group> <variable to change> <value>"
            )

    @commands.has_permissions(kick_members=True)
    @config.command(name="add_url")
    async def add_blocked_url(self, ctx, url):
        urls = self.bot.config_obj.add_blocked_url(url)

        text = "These urls are blocked.\n"
        for i in urls:
            text += f"`{i}` \n"
        await ctx.reply(text)

    @commands.has_permissions(kick_members=True)
    @config.command(name="remove_url")
    async def remove_blocked_url(self, ctx, url):
        urls = self.bot.config_obj.remove_blocked_url(url)

        text = "These urls are blocked.\n"
        for i in urls:
            text += f"`{i}` \n"
        await ctx.reply(text)

    @commands.has_permissions(kick_members=True)
    @config.command(name="show_urls")
    async def show_blocked_url(self, ctx):
        text = "These urls are blocked."
        urls = self.bot.config['blocked_urls']['urls']
        for i in urls:
            text += f"`{i}` \n"
        await ctx.reply(text)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(Mod(bot))
