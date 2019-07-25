import discord
from discord.ext import commands
import random


class MiscCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def dab(self, ctx, member = "everyone"):

        msg = "<:Dab:443893837388316673> {} just dabbed on {}".format(ctx.author.name, member)
        embed = discord.Embed(title="<:Dab:443893837388316673> Dabbing on the haters", description=msg, colour=ctx.author.colour)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/443893837388316673.png")
        await ctx.send(embed=embed)
		

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def mitochondria(self, ctx):

        embed = discord.Embed(title="Mitochondria", description="", colour=ctx.author.colour)
        embed.set_image(url="https://i.imgur.com/80iINul.jpg")
        requested_by = "Requested by {}".format(ctx.author.name)
        embed.set_footer(text=requested_by)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def literallyme(self, ctx):

        literallyme = ["https://i.imgur.com/J56l01s.jpg","https://i.imgur.com/BE1Roa6.jpg","https://i.imgur.com/EOn4t0v.jpg","https://i.imgur.com/GOmd9sE.jpg","https://i.imgur.com/b4RCKxD.jpg","https://i.imgur.com/u45VL8K.jpg","https://i.imgur.com/b9Z1f0H.png","https://cdn.discordapp.com/attachments/390888617536651265/441616070302760960/17493891_1009834615783993_1976996299869782016_n.jpg","https://cdn.discordapp.com/attachments/367744546752430082/442416104611250177/20180505_195713.JPG"]
        embed = discord.Embed(title="Literally me", description="", colour=ctx.author.colour)
        embed.set_image(url=random.choice(literallyme))
        requested_by = "Requested by {}".format(ctx.author.name)
        embed.set_footer(text=requested_by)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def nani(self, ctx, nanid: discord.Member = None):

        member = ctx.message.author
        members = ctx.guild.members

        if nanid == None:
            nanid = random.choice(members)

        embed = discord.Embed(title="", description="Nani!?")
        embed.set_author(icon_url=nanid.avatar_url, name=nanid.name)
        await ctx.send(embed=embed)

        embed = discord.Embed(title="", description="Omae wa mou shindeiru!")
        embed.set_author(icon_url=member.avatar_url, name=member.name)
        await ctx.send(embed=embed)    

def setup(bot):
    bot.add_cog(MiscCog(bot))
