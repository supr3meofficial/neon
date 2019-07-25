import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

class AboutCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):

        embed=discord.Embed(title="<:discord:434011189656158219> BOT Invite Link", url="https://discordapp.com/oauth2/authorize?&client_id=603989887125028904&scope=bot&permissions=8", description="Click the link above to invite the bot to your discord!", color=0x80ff00)
        await ctx.send(embed=embed)

    @commands.command()
    async def discord(self, ctx):

        embed=discord.Embed(title="<:discord:434011189656158219> Discord", url="https://discord.gg/Awt7krm", description="Please join our discord using the link above", color=0x80ff00)
        await ctx.send(embed=embed)

    @commands.command()
    async def donate(self, ctx):

        embed=discord.Embed(title="<:steam:434018638748581898> Trade Link", url="https://steamcommunity.com/tradeoffer/new/?partner=342778939&token=tS1Rd02f", description="If you would like to help me, click the link above, thank you!", color=0x80ff00)
        await ctx.send(embed=embed)
        embed=discord.Embed(title="<:PayPal:437213765923241986> Paypal Link", url="https://www.paypal.me/supr3medonate", description="If you would like to help me, click the link above, thank you!", color=0x80ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def github(self, ctx):

        embed=discord.Embed(title="<:GitHub:449612764751593472> GitHub", url="https://github.com/supr3meofficial/neon", description="Click this link to see my insides", color=0x80ff00)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AboutCog(bot))
