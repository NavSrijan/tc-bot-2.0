from discord.ext import commands
import os
import random
from helpers import basic_embed


class Freedom(commands.Cog):
    """Basic hello commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="how", aliases=["how's", "hows", "htj"])
    async def Josh(self, ctx, *args):
        """JOSH!"""
        alia = [
            "how's the josh", "hows the josh?", "hows the josh",
            "how's the josh?", "htj?", "htj"
        ]
        for i in alia:
            if ctx.message.content[1:].lower().startswith(i):
                await ctx.send(
                    "https://tenor.com/view/high-sir-salute-respect-yessir-yeah-gif-15588688"
                )
                return

    @commands.command(name="slogan", aliases=["india"])
    async def Josh(self, ctx, *args):
        """SlOGAN!"""
        slogans = [
            [
                "Jai Hind",
                "The slogan “Jai Hind” was initially coined by Zain-ul Abideen Hasan, but it was adopted by Netaji Subhash Chandra Bose. It is now used as a way of salutation throughout India. It means “Victory to India” in English."
            ],
            [
                "Vande Mataram",
                "It was a poem mentioned in Bankim Chandra Chattopadhyay’s novel Anandmath. Also a journalist and activist, Chattopadhyay wrote the novel in Bengali and Sanskrit in 1882. “Vande Matram” means “I salute you, mother”."
            ],
            [
                "Swaraj Mera Janamsiddh adhikar hai, aur main ise lekar rahunga",
                "Coined by Kaka Baptista in India’s fight for independence, this slogan was adopted by Bal Gangadhar Tilak. This slogan motivated Indians to fight for independence and also invoked the feeling of love towards the nation in their hearts."
            ],
            [
                "Jai Jawaan, Jai Kisaan",
                "Given by Lal Bahadur Shastri, this slogan acknowledges and appreciates the efforts of soldiers and farmers of our country."
            ],
            [
                "Satyameva Jayate",
                "Pandit Madan Mohan Malaviya coined this slogan, and it means “truth alone triumphs”."
            ],
            [
                "Inquilab Zindabad",
                "This slogan was given by Muslim leader Hasrat Mohani. It means “Long live the revolution”. After bombing the Central Assembly in Delhi, Bhagat Singh also shouted this slogan. It turned into one of the rallying cries of Indian independence movement."
            ],
            [
                "Sarfaroshi Ki Tamanna, Ab hamare dil mein hai",
                "It’s a patriotic poem which was given by Bismil Azimabadi, and later, Ramprasad Bismil started to use it as a slogan. It urged people to fight for what’s right."
            ],
            [
                "Dushman ki goliyon ka hum samna karenge, Azad hee rahein hain, Azad hee rahenge",
                "Chandra Shekhar Azad gave this slogan after the Jallianwala Bagh Massacre happened, that led to the loss of hundreds of innocent lives."
            ],
            [
                "Araam Haraam hai",
                "This slogan was given by our former Prime Minister Jawaharlal Nehru. It reflects that our freedom fighters had no rest throughout the freedom struggle."
            ],
            [
                "Tum mujhe khoon do, mai tumhe azaadi doonga.",
                "Netaji Subhash Chandra Bose used this slogan to urge the youth to join Indian Army, and contribute to India’s fight for independence."
            ]
        ]
        slogan = random.choice(slogans)
        await ctx.channel.send(embed=basic_embed(title=slogan[0], desc=f"{slogan[1]}"))


async def setup(bot):
    await bot.add_cog(Freedom(bot))
