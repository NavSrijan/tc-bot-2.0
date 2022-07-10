from discord.ext import commands
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(int(os.environ['welcome_channel']))
        self_roles_channel = int(os.environ['self_roles_channel'])

        welcomeMessage = f"""
╭━─━─━─━─  ≪✠≫  ─━─━─━─━╮
{arrow2} 𝙷𝙴𝚈 <@{member.id}>
{arrow2} 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝚃𝙾 𝚃𝙴𝙴𝙽𝙰𝙶𝙴 𝙲𝙾𝙼𝙼𝚄𝙽𝙸𝚃𝚈
{arrow2} 𝙿𝙻𝙴𝙰𝚂𝙴 𝙶𝚁𝙰𝙱 𝚈𝙾𝚄𝚁 <#{self_roles_channel}>
╰━─━─━─━─  ≪✠≫  ─━─━─━─━╯
"""
        await channel.send(welcomeMessage)



        def check(message):
            return message.author == member
        
        message = await self.bot.wait_for(event = 'message', check = check, timeout = 60.0)
        await message.reply(message.content)
    
    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send(f"Hello! {ctx.message.content[5:]}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))