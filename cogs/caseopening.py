import discord
from discord.ext import commands
from .utils.paginator import FieldPages
import random
import asyncio
import aiohttp
import os
import json

class DataHandler():

	def __init__(self):
		if not 'neon\data' in os.getcwd():
			os.chdir('data')
		with open('output.json') as fp:
			self.case_data = json.load(fp)

	def get_case_data(self):
		self.case_list = []
		for case_data_single in self.case_data:
			self.case_name = case_data_single
			self.case_img = self.case_data[case_data_single]['image_url']
			self.case_list.append((self.case_name, self.case_img))
		return self.case_list

	def get_case_skins(self, case):
		return self.case_data[case]


class CaseOpening(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	async def show_main_menu(self, ctx):
		"""Displays main menu and returns what to open"""
		main_menu = discord.Embed(
		title="",
		description=
		"""
**Select your preferred opening and click the matching reaction:**

<:csgocase:433064927645925386> Open skin case
		""",
		#<:csgopin:671062353948835850> Open pin capsule
		colour=0xc7c7c7)
		main_menu.set_author(
		icon_url=self.bot.user.avatar_url,
		name='Neon Case Opening')

		_main_menu = await ctx.send(embed=main_menu) # Send Embed
		await _main_menu.add_reaction('<:csgocase:433064927645925386>') # Add reactions
		#await _main_menu.add_reaction('<:csgopin:671062353948835850>')

		# Check for user reactions
		def check(reaction, user):
			return user == ctx.author and str(reaction.emoji) in [
			'<:csgocase:433064927645925386>'
			#'<:csgopin:671062353948835850>'
			]
		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			_main_menu_r = str(reaction.emoji)
		except asyncio.TimeoutError:
			what_to_open = 'case'
		else:
			if _main_menu_r == "<:csgocase:433064927645925386>":
				what_to_open = 'case'
			#elif _main_menu_r == "<:csgopin:671062353948835850>":
			#	what_to_open = 'pin'

		await _main_menu.delete()
		return what_to_open

	async def show_case_selection_menu(self, ctx, page=1, init=False, invalid=False):
		"""Displays case selection menu and returns selected case"""
		case_list = DataHandler().get_case_data()

		max_page = len(case_list)
		i = page-1
		EMBED_INSTANCE = {}
		EMBED_INSTANCE[f'{ctx.author.id}'] = discord.Embed(title="Case Selection Menu", description="")
		# Display case
		if init:
			EMBED_INSTANCE[f'{ctx.author.id}'].add_field(name="Selected case:", value="Loading cases..", inline=False)
			global _main_menu
			_main_menu = await ctx.send(embed=EMBED_INSTANCE[f'{ctx.author.id}'] ) # Editable object
			if max_page == 1:
				pass
			else:
				await _main_menu.add_reaction('\N{BLACK LEFT-POINTING TRIANGLE}')
				await _main_menu.add_reaction('\N{WHITE HEAVY CHECK MARK}')
				await _main_menu.add_reaction('\N{BLACK RIGHT-POINTING TRIANGLE}')

		if not invalid:
			EMBED_INSTANCE[f'{ctx.author.id}'].clear_fields()
			EMBED_INSTANCE[f'{ctx.author.id}'].add_field(name="Selected case:", value=case_list[i][0], inline=False)
			EMBED_INSTANCE[f'{ctx.author.id}'].set_thumbnail(url=case_list[i][1])
			EMBED_INSTANCE[f'{ctx.author.id}'].set_footer(text=f"{self.bot.user.name} • Page {page}/{max_page}")
			await _main_menu.edit(embed=EMBED_INSTANCE[f'{ctx.author.id}'] )

		# Get reactions from menu
		if max_page != 1:
			def check(reaction, user):
				return user == ctx.author and str(reaction.emoji) in ['\N{WHITE HEAVY CHECK MARK}','\N{BLACK LEFT-POINTING TRIANGLE}','\N{BLACK RIGHT-POINTING TRIANGLE}']
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
				_main_menu_r = str(reaction.emoji)
			except asyncio.TimeoutError:
				await _main_menu.delete()
				return case_list[i][0]
			else:
				if _main_menu_r == '\N{BLACK RIGHT-POINTING TRIANGLE}' and page != max_page:
					await reaction.remove(user)
					await self.show_case_selection_menu(ctx, page+1)
				elif _main_menu_r == '\N{WHITE HEAVY CHECK MARK}':
					await _main_menu.delete()
					global selected_case
					selected_case = case_list[i][0]
				elif _main_menu_r == '\N{BLACK LEFT-POINTING TRIANGLE}' and page != 1:
					await reaction.remove(user)
					await self.show_case_selection_menu(ctx, page-1)
				else:
					await reaction.remove(user)
					await self.show_case_selection_menu(ctx, page, False, True)

	@commands.group(name='open')
	@commands.guild_only()
	@commands.cooldown(1, 8, commands.BucketType.user)
	async def open_(self, ctx):
		"""open case - Opens a CS:GO case"""
		pass

	async def cog_command_error(self, ctx, error):
		if isinstance(error, commands.MaxConcurrencyReached):
			await ctx.send(content='You can only open 1 case at a time!',delete_after=5)

	@open_.command(name='menu')
	async def menu(self, ctx):
		what_to_open = await self.show_main_menu(ctx)
		if what_to_open == 'case': await self.open_case()
		else: pass

	@open_.command(name='case')
	@commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
	async def open_case(self, ctx, *, case : str = None):
		"""Opens a CS:GO case or pin capsule"""
		global selected_case
		if case != None:
			selected_case = ''
			case_list = DataHandler().get_case_data()
			for _case in case_list:
				if case.lower() in _case[0].lower():
					selected_case = _case[0]
			if not selected_case: return
		else:
			await self.show_case_selection_menu(ctx, 1, True)
		# Handle case contents
		can_be_stattrak = True
		case_data = DataHandler().get_case_skins(selected_case)
		knives = case_data['content']['Knives']
		gloves = case_data['content']['Gloves']
		if len(knives) != 0:
			special_items = knives
		elif len(gloves) != 0:
			special_items = gloves
			can_be_stattrak = False
		if selected_case != 'X-Ray P250 Package':
			covert_skins = case_data['content']['Covert Skins']
			classified_skins = case_data['content']['Classified Skins']
			milspec_skins = case_data['content']['Mil-Spec Skins']
		restricted_skins = case_data['content']['Restricted Skins']

		# StatTrak™ Odds
		st = ''
		if can_be_stattrak:
			st_odds = random.randint(0,10)
			if st_odds == 10: st = 'StatTrak™'
			else: st = ''

		# Rarity Odds
		drop_odds = random.randint(0,100)

		# Skin Selection
		if selected_case != 'X-Ray P250 Package':
			if drop_odds == 100: # 100: 1% chance
				tier = 'covert'
				selected_skin_data = random.choice(special_items)
			elif drop_odds >= 91: # 99-91: 8% chance
				tier = 'covert'
				selected_skin_data = random.choice(covert_skins)
			elif drop_odds >= 76: #90-76: 14% chance
				tier = 'classified'
				selected_skin_data = random.choice(classified_skins)
			elif drop_odds >= 52: #75-52: 23% Chance
				tier = 'restricted'
				selected_skin_data = random.choice(restricted_skins)
			elif drop_odds >= 0: #51-0: 51% Chance
				tier = 'milspec'
				selected_skin_data = random.choice(milspec_skins)
		else:
			tier = 'restricted'
			selected_skin_data = restricted_skins[0]

		skin_title = selected_skin_data['title']
		skin_wears = selected_skin_data['possible_wears']
		skin_wear = random.choice(list(skin_wears.keys()))
		wear = {"fn" : "(Factory New)", "mw" : "(Minimal Wear)", "ft" : "(Field-Tested)", "ww" : "(Well-Worn)", "bs" : "(Battle-Scarred)", "vanilla" : ""}
		skin_image = skin_wears[skin_wear]
		skin_desc = selected_skin_data['desc']
		skin_lore = selected_skin_data['lore']
		skin_name = f'{st} {skin_title} {wear[skin_wear]}'

		# Skin Tier and Embed Colour
		def tier_colour():
			if tier == "milspec":
				return discord.Colour(0x177cc7)
			elif tier == "restricted":
				return discord.Colour(0x872de0)
			elif tier == "classified":
				return discord.Colour(0xc917e0)
			elif tier == "covert":
				return discord.Colour(0xe7191b)
			elif tier == "knife_gloves":
				return discord.Colour(0xe7191b)
			elif tier == "pin":
				return discord.Colour(0xe0d029)
			elif tier == "trophy":
				return discord.Colour(0x71e4cb)

		# Embed Animation
		embed_opening = discord.Embed(title="", description="", colour=0xc7c7c7)
		embed_opening.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Opening your {selected_case}..')

		embed_full_detail = discord.Embed(title=skin_name, description=skin_desc, colour=tier_colour())
		embed_full_detail.set_author(icon_url=ctx.author.avatar_url, name=f'You have 1 new item!')
		embed_full_detail.add_field(name="Lore:", value=skin_lore, inline=False)
		embed_full_detail.set_image(url=skin_image)

		embed_min_detail = discord.Embed(title="", description=skin_name, colour=tier_colour())
		embed_min_detail.set_author(icon_url=ctx.author.avatar_url, name=f'{ctx.author.name} received a new item:')
		embed_min_detail.set_footer(text=f"{self.bot.user.name} • This item is found in the {selected_case}")
		embed_min_detail.set_thumbnail(url=skin_image)

		# Send Embed
		msg = await ctx.send(embed=embed_opening)
		await asyncio.sleep(3)
		await msg.edit(embed=embed_full_detail)
		await asyncio.sleep(10)
		await msg.edit(embed=embed_min_detail)

	@open_.command(name='dev')
	@commands.is_owner()
	async def open_dev(self, ctx, selected_rarity : int, *, case : str = None):
		"""Opens a CS:GO case or pin capsule"""
		global selected_case
		global selected_skin_data
		if case != None:
			selected_case = ''
			case_list = DataHandler().get_case_data()
			for _case in case_list:
				if case.lower() in _case[0].lower():
					selected_case = _case[0]
			if not selected_case: return
		else:
			await self.show_case_selection_menu(ctx, 1, True)
		# Handle case contents
		case_data = DataHandler().get_case_skins(selected_case)
		if selected_case != 'X-Ray P250 Package':
			special_items = case_data['content']['Rare Special Items']
			covert_skins = case_data['content']['Covert Skins']
			classified_skins = case_data['content']['Classified Skins']
			milspec_skins = case_data['content']['Mil-Spec Skins']
		restricted_skins = case_data['content']['Restricted Skins']

		if selected_case != 'X-Ray P250 Package':
			if selected_rarity == 0:
				tier = 'covert'
				selected_skin_data = random.choice(special_items)
			elif selected_rarity == 1:
				tier = 'covert'
				selected_skin_data = random.choice(covert_skins)
			elif selected_rarity == 2:
				tier = 'classified'
				selected_skin_data = random.choice(classified_skins)
			elif selected_rarity == 3:
				tier = 'restricted'
				selected_skin_data = random.choice(restricted_skins)
			elif selected_rarity == 4:
				tier = 'milspec'
				selected_skin_data = random.choice(milspec_skins)
		else:
			tier = 'restricted'
			selected_skin_data = restricted_skins[0]

		skin_title = selected_skin_data['title']
		skin_wears = selected_skin_data['possible_wears']
		skin_wear = random.choice(list(skin_wears.keys()))
		wear = {"fn" : "(Factory New)", "mw" : "(Minimal Wear)", "ft" : "(Field-Tested)", "ww" : "(Well-Worn)", "bs" : "(Battle-Scarred)", "vanilla" : ""}
		skin_image = skin_wears[skin_wear]
		skin_desc = selected_skin_data['desc']
		skin_lore = selected_skin_data['lore']
		skin_name = f'{skin_title} {wear[skin_wear]}'

		# Skin Tier and Embed Colour
		def tier_colour():
			if tier == "milspec":
				return discord.Colour(0x177cc7)
			elif tier == "restricted":
				return discord.Colour(0x872de0)
			elif tier == "classified":
				return discord.Colour(0xc917e0)
			elif tier == "covert":
				return discord.Colour(0xe7191b)
			elif tier == "knife_gloves":
				return discord.Colour(0xe7191b)
			elif tier == "pin":
				return discord.Colour(0xe0d029)
			elif tier == "trophy":
				return discord.Colour(0x71e4cb)

		# Embed Animation
		embed_opening = discord.Embed(title="", description="", colour=0xc7c7c7)
		embed_opening.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Opening your {selected_case}..')

		embed_full_detail = discord.Embed(title=skin_name, description=skin_desc, colour=tier_colour())
		embed_full_detail.set_author(icon_url=ctx.author.avatar_url, name=f'You have 1 new item!')
		embed_full_detail.add_field(name="Lore:", value=skin_lore, inline=False)
		embed_full_detail.set_image(url=skin_image)

		embed_min_detail = discord.Embed(title="", description=skin_name, colour=tier_colour())
		embed_min_detail.set_author(icon_url=ctx.author.avatar_url, name=f'{ctx.author.name} received a new item:')
		embed_min_detail.set_footer(text=f"{self.bot.user.name} • This item is found in the {selected_case}")
		embed_min_detail.set_thumbnail(url=skin_image)

		# Send Embed
		msg = await ctx.send(embed=embed_opening)
		await asyncio.sleep(3)
		await msg.edit(embed=embed_full_detail)
		await asyncio.sleep(10)
		await msg.edit(embed=embed_min_detail)

def setup(bot):
	bot.add_cog(CaseOpening(bot))
