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
    @commands.command(name="test", hidden=True)
    async def test(self, ctx):
        emb = basic_embed(
            desc="hi",
            color=discord.Color.red(),
            image_url=
            "https://tenor.com/view/wow-very-dangerous-wow-berry-dangerous-very-dangerous-ayub-kha98-tiktoker-gif-23393447"
        )
        await ctx.reply(embed=emb)

    @commands.has_permissions(kick_members=True)
    @commands.command(name="torture")
    async def torture(self, ctx):
        """Keep deleting a users message for 60s."""
        if len(ctx.message.mentions) >= 1:
            user = ctx.message.mentions[0]
        else:
            await ctx.reply("Mention someone.")
            return

        def check(message):
            return message.author == user

        total_timeout = 60
        old_time = time.time()
        while total_timeout > 0:
            try:
                msg = await self.bot.wait_for('message',
                                              check=check,
                                              timeout=total_timeout)
                await msg.delete()
                total_timeout -= +time.time() - old_time
                old_time = time.time()
            except:
                await ctx.reply("Done.")
        await ctx.reply("Done.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="lock")
    async def lock_channel(self, ctx):
        """
        Locks the channel
        """
        await ctx.channel.set_permissions(ctx.message.guild.default_role,
                                          read_messages=True,
                                          send_messages=False)
        await ctx.channel.send("The channel has been locked.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="unlock")
    async def unlock_channel(self, ctx):
        """
        Unlocks the channel
        """
        await ctx.channel.set_permissions(ctx.message.guild.default_role,
                                          read_messages=True,
                                          send_messages=True)
        await ctx.channel.send("The channel has been unlocked.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick")
    async def kick(self, ctx):
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
        if ctx.message.mentions:
            member = ctx.message.mentions[0]
        else:
            await ctx.reply("Mention someone.")
            return
        name = member.name
        try:
            await member.kick()
            await ctx.channel.send(random.choice(gifs))
            await ctx.channel.send(f"`{name} has been kicked.`")
        except:
            await ctx.reply("Sorry but, I don't have the permissions.")

    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban")
    async def ban(self, ctx):
        """Ban a member"""
        if ctx.message.mentions:
            member = ctx.message.mentions[0]
        else:
            await ctx.reply("Mention someone.")
            return
        name = member.name
        try:
            await member.ban()
            await ctx.channel.send(
                "https://tenor.com/view/bad-mom-grandma-baby-kicking-i-love-children-gif-23173847"
            )
            await ctx.channel.send(f"{name} has been banned.")
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
    @commands.group(name="config")
    async def config(self, ctx):
        """Change the config"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid command")

    @commands.has_permissions(kick_members=True)
    @config.command(name="add_url")
    async def add_blocked_url(self, ctx, *args):
        for i in args:
            urls = self.bot.config_obj.add_blocked_url(i)

        text = "These urls are blocked."
        for i in urls:
            text += f"`{i}` \n"
        await ctx.reply(text)

    @commands.has_permissions(kick_members=True)
    @config.command(name="remove_url")
    async def remove_blocked_url(self, ctx, *args):
        for i in args:
            urls = self.bot.config_obj.remove_blocked_url(i)

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

    @commands.has_permissions(kick_members=True)
    @config.command(name="revive_channel")
    async def revive_channel(self, ctx, revive_channel):
        try:
            chnl = self.bot.get_channel(revive_channel)
            self.bot.config['commands']['revive']['revive_channel'] = revive_channel
            await ctx.reply("The revive channel has been successfully changed.")
            self.bot.config_obj.dump_config()
        except:
            await ctx.reply(f"Provide the id of the channel you with to switch the revive_channel to.\nCurrent channel is <#{self.bot.config['commands']['revive']['revive_channel']}>")

    @commands.has_permissions(kick_members=True)
    @config.command(name="revive_available")
    async def revive_available(self, ctx, revive_available):
        try:
            chnl = int(revive_available)
            self.bot.config['commands']['revive']['revive_available'] = revive_available
            await ctx.reply("The revive count has been successfully changed.")
            self.bot.config_obj.dump_config()
        except:
            await ctx.reply(f"Provide the number to set the revives to.\nCurrent available revives is {self.bot.config['commands']['revive']['revive_available']}")

    @commands.has_permissions(kick_members=True)
    @config.command(name="revive_delay")
    async def revive_delay(self, ctx, revive_delay):
        try:
            chnl = int(revive_delay)
            self.bot.config['commands']['revive']['revive_delay'] = revive_delay
            await ctx.reply("The revive delay has been successfully changed.")
            self.bot.config_obj.dump_config()
        except:
            await ctx.reply(f"Provide the number of seconds to set the revive delay to.\nCurrent delay is {self.bot.config['commands']['revive']['revive_delay']}")

    @commands.has_permissions(kick_members=True)
    @config.command(name="revive_role")
    async def revive_delay(self, ctx, revive_role):
        try:
            chnl = int(revive_role)
            self.bot.config['commands']['revive']['revive_delay'] = revive_role
            await ctx.reply("The revive role has been successfully changed.")
            self.bot.config_obj.dump_config()
        except:
            await ctx.reply(f"Provide the revive role to set the revive role to.\nCurrent role is {self.bot.config['commands']['revive']['revive_role']}")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            #ctx.message.reply(error)
            print(error)


async def setup(bot):
    await bot.add_cog(Mod(bot))
