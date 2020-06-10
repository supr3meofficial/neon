import discord
from discord.ext import commands
from .utils import checks
from .utils.paginator import FieldPages
import random
import asyncio
import aiohttp
import os
import json
import string
import math

main_dir = os.getcwd()
def root_path():
	return os.path.abspath(main_dir)

data_path = os.path.join(root_path(), 'data')

class Container:
	"""Represents a container"""

	def _load_contents(self):
		"""Loads the container contents"""
		self.special_items = self._set_item_set('Rare Special Items')
		self.covert_skins = self._set_item_set('Covert Skins')
		self.classified_skins = self._set_item_set('Classified Skins')
		self.restricted_skins = self._set_item_set('Restricted Skins')
		self.milspec_skins = self._set_item_set('Mil-Spec Skins')
		self.industrial_skins = self._set_item_set('Industrial Grade Skins')
		self.consumer_skins = self._set_item_set('Consumer Grade Skins')
		self.item_sets = self._get_item_sets()

	def _translate_rarity(self, rarity_set):
		"""Helper function that translates the rarity set name"""
		rarity_translations = {
		'Rare Special Items'     : 'Covert Special',
		'Covert Skins'           : 'Covert',
		'Classified Skins'       : 'Classified',
		'Restricted Skins'       : 'Restricted',
		'Mil-Spec Skins'         : 'Mil-Spec',
		'Industrial Grade Skins' : 'Industrial',
		'Consumer Grade Skins'   : 'Consumer'
		}

		return rarity_translations[rarity_set]

	def _set_item_set(self, rarity_set):
		"""Helper function that sets the container item sets"""

		def add(content, collection_name, item_set):
			# Convert raw data into Item object
			for skin in content:
				item_skin = Item(skin)
				item_skin.collection = collection_name
				item_set.add_item(item_skin)

		# Create item set object
		item_set = ItemSet(rarity_set, self._translate_rarity(rarity_set))
		# Retrieve rarity set content from raw data
		try:
			if self.has_multiple_collections:
				for collection in self.collection_list:
					content = self.raw_data['content'][collection][rarity_set]
					add(content, collection, item_set)
			else:
				content = self.raw_data['content'][rarity_set]
				add(content, self.collection_name, item_set)
		except KeyError:
			pass

		return item_set

	def _get_odds(self, rarity):
		"""Helper function that sets the rarity odds"""
		odds = {
		'Covert Special' : 'Extremely Rare',
		'Covert'         : 'Super Rare',
		'Classified'     : 'Rare',
		'Restricted'     : 'Uncommon',
		'Mil-Spec'       : 'Common',
		'Industrial'     : 'Super Common',
		'Consumer'       : 'Extremely Common'
		}

		return odds[rarity]

	def _get_item_sets(self):
		"""Helper function that sets the real container item sets"""
		sets = [
		self.special_items,
		self.covert_skins,
		self.classified_skins,
		self.restricted_skins,
		self.milspec_skins,
		self.industrial_skins,
		self.consumer_skins
		]

		item_sets = []
		for set in sets:
			if not set.content == []:
				item_sets.append(set)

		return item_sets

	def get_random_item_set(self):
		"""Returns a random item set using weighted random selection"""

		odds_weights = {
		'Extremely Rare'   : 0.02,
		'Super Rare'       : 0.08,
		'Rare'             : 0.1,
		'Uncommon'         : 0.25,
		'Common'           : 0.55,
		'Super Common'     : 0.8,
		'Extremely Common' : 1.2
		}

		weights = []
		for set in self.item_sets:
			weight = odds_weights[self._get_odds(set.rarity)]
			weights.append(weight)

		return random.choices(self.item_sets, cum_weights=weights)[0]

class Case(Container):
	"""A derived class of Container: Represents a Case"""
	def __init__(self, name):
		self.raw_data = Case._get_raw_data()[name]
		self.name = name
		self.type = 'Case'
		self.image_url = self.raw_data['image_url']
		self.collection_name = f'The {self.name} Collection'
		self.has_multiple_collections = False
		self.content = self.raw_data['content']

	@staticmethod
	def _get_raw_data():
		"""Helper function that returns raw json data"""
		file_path = f'{data_path}\cases.json'
		with open(file_path, 'r') as fp:
			content = json.load(fp)
		return content

	@staticmethod
	def get_all_containers():
		"""Returns all Case containers in a list"""
		container_list = []
		for container_name in Case._get_raw_data():
			container_list.append(Case(container_name))
		return container_list # Returns list of Case objects

	@staticmethod
	def get_container(container_name):
		"""Looks up a container by name and returns matching results in a list"""
		results = []
		for container in Case.get_all_containers():
			if container_name.lower() in container.name.lower():
				results.append(container)
		return results

class SouvenirPackage(Container):
	"""A derived class of Container: Represents a Souvenir Package"""
	def __init__(self, name):
		self.raw_data = SouvenirPackage._get_raw_data()[name]
		self.name = name
		self.type = 'Souvenir Package'
		self.image_url = self.raw_data['image_url']
		self.collection_name = self.raw_data['collection_name']
		self.has_multiple_collections = False

		if type(self.collection_name) is list:
			self.has_multiple_collections = True
			self.collection_list = self.collection_name
			self.collection_name = ', '.join(self.collection_name)

		self.content = self.raw_data['content']

	@staticmethod
	def _get_raw_data():
		"""Helper function that returns raw json data"""
		file_path = f'{data_path}/souvenir_packages.json'
		with open(file_path, 'r') as fp:
			content = json.load(fp)
		return content

	@staticmethod
	def get_all_containers():
		"""Returns all Souvenir Package containers in a list"""
		container_list = []
		for container_name in SouvenirPackage._get_raw_data():
			container_list.append(SouvenirPackage(container_name))
		return container_list

	@staticmethod
	def get_container(container_name):
		"""Looks up a container by name and returns matching results in a list"""
		results = []
		for container in SouvenirPackage.get_all_containers():
			if container_name.lower() in container.name.lower():
				results.append(container)
		return results

class ItemSet:
	"""Represents an Item Set"""
	def __init__(self, name, rarity):
		self.name = name
		self.rarity = rarity
		self.content = []

	def add_item(self, item):
		"""Adds an item to the Item Set"""
		item.rarity = self.rarity
		if self.rarity == 'Covert Special' and 'Gloves' not in item.name:
			item.has_stattrak = False
		self.content.append(item)

	def get_random_skin(self):
		"""Returns a random item from the item set"""
		return random.choice(self.content)

	def get_skin(self, skin_name):
		"""Looks up a skin by name and returns matching results in a list"""
		results = []
		for item in self.content:
			if skin_name in item.name:
				results.append(item)
		return results

class Item:
	"""Represents an Item Skin"""
	def __init__(self, data):
		self.name = data['title']
		self.skin_wears = data['possible_wears']
		self.description = data['desc']
		self.lore = data['lore']
		self.collection = None
		self.rarity = None
		self.has_stattrak = False
		self.is_stattrak = False
		self.is_souvenir = False

	def _get_random_wear(self):
		"""Helper function that returns a random wear"""
		return random.choice(list(self.skin_wears.keys()))

	def _translate_wear(self, wear):
		"""Helper function that translates the wear into proper format"""
		translation = {"fn" : "(Factory New)", "mw" : "(Minimal Wear)", "ft" : "(Field-Tested)", "ww" : "(Well-Worn)", "bs" : "(Battle-Scarred)", "vanilla" : ""}
		return translation[wear]

	def _set_prefix(self):
		"""Helper function to set StatTrak or Souvenir prefix in random skin variation"""
		if self.has_stattrak:
			st_odds = random.randint(0,10)
			if st_odds == 10:
				self.is_stattrak = True
				return 'StatTrak™ '

		if self.is_souvenir:
			return 'Souvenir '

		return ''

	def get_random_variation(self):
		"""Returns a random skin variation"""
		skin_wear = self._get_random_wear()
		skin_image = self.skin_wears[skin_wear]
		skin_variation = f'{self._set_prefix()}{self.name} {self._translate_wear(skin_wear)}'
		return skin_variation, skin_image

	def get_rarity_colour(self):
		"""Returns the embed colour that matches the skin rarity"""
		colours = {
		'Consumer'       : discord.Colour(0xafafaf),
		'Industrial'     : discord.Colour(0x6496e1),
		'Mil-Spec'       : discord.Colour(0x177cc7),
		'Restricted'     : discord.Colour(0x872de0),
		'Classified'     : discord.Colour(0xc917e0),
		'Covert'         : discord.Colour(0xe7191b),
		'Covert Special' : discord.Colour(0xe7191b)
		}
		return colours[self.rarity]

class SelectionMenu:
	"""Selection Menu Class"""
	EMOJI_LAST_PAGE = '\N{BLACK LEFT-POINTING TRIANGLE}'
	EMOJI_NEXT_PAGE = '\N{BLACK RIGHT-POINTING TRIANGLE}'
	EMOJI_CHECK = '\N{WHITE HEAVY CHECK MARK}'
	EMOJI_LIST= [EMOJI_LAST_PAGE, EMOJI_NEXT_PAGE, EMOJI_CHECK]

	def __init__(self, ctx, message_object, selection_list, selection_type):
		self.selection_list = selection_list
		self.selection_type = selection_type
		self.total_pages = len(self.selection_list)
		self.ctx = ctx
		self.embed = discord.Embed(title=f"{self.selection_type} Selection Menu", description="")
		self.msg_embed = message_object
		self.selected_option = None

	async def show_menu(self):
		"""Displays the loading menu"""
		self.embed.add_field(name=f'Selected {self.selection_type}:', value='Loading..', inline=False)
		await self.msg_embed.edit(embed=self.embed)

		if self.total_pages > 1:
			await self.msg_embed.add_reaction(self.EMOJI_LAST_PAGE)
			await self.msg_embed.add_reaction(self.EMOJI_CHECK)
			await self.msg_embed.add_reaction(self.EMOJI_NEXT_PAGE)
		else:
			await self.msg_embed.add_reaction(self.EMOJI_CHECK)

	async def _destroy(self):
		"""Helper function that deletes the message embed with error handling"""
		try:
			await self.msg_embed.delete()
		except discord.HTTPException:
			pass

	async def _reaction_remove(self):
		"""Helper function for reaction removal with error handling"""
		try:
			await self.reaction.remove(self.user)
		except discord.HTTPException:
			pass

	async def _action_first_page(self):
		"""Helper function for embed action: first page"""
		await self._reaction_remove()
		await self.show_page(1)

	async def _action_last_page(self):
		"""Helper function for embed action: last page"""
		await self._reaction_remove()
		await self.show_page(self.total_pages)

	async def _action_next_page(self):
		"""Helper function for embed action: next page"""
		await self._reaction_remove()
		await self.show_page(self.current_page+1)

	async def _action_back_page(self):
		"""Helper function for embed action: last page"""
		await self._reaction_remove()
		await self.show_page(self.current_page-1)

	async def _action_select(self):
		"""Helper function for embed action: select option"""
		self.selected_option = self.selection_list[self.current_index]

	async def _wait_for_action(self):
		"""Message Reaction Check"""
		def check(reaction, user):
			return user == self.ctx.author and reaction.message.id == self.msg_embed.id and reaction.emoji in self.EMOJI_LIST

		try:
			self.reaction, self.user = await self.ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
		except asyncio.TimeoutError:
			await self._action_select()
		else:
			if self.reaction.emoji == self.EMOJI_NEXT_PAGE and self.current_page != self.total_pages:
				await self._action_next_page()
			elif self.reaction.emoji == self.EMOJI_CHECK:
				await self._action_select()
			elif self.reaction.emoji == self.EMOJI_LAST_PAGE and self.current_page != 1:
				await self._action_back_page()
			elif self.reaction.emoji == self.EMOJI_NEXT_PAGE and self.current_page == self.total_pages:
				await self._action_first_page()
			elif self.reaction.emoji == self.EMOJI_LAST_PAGE and self.current_page == 1:
				await self._action_last_page()

class OpeningSelectionMenu(SelectionMenu):
	"""Opening Selection Menu Object"""

	def __init__(self, ctx, message_object, selection_list, selection_type):
		super().__init__(ctx, message_object, selection_list, selection_type)

	async def show_page(self, page):
		"""Displays a menu page and sets selected item"""
		self.current_page = page
		self.current_index = self.current_page-1

		self.embed.clear_fields()
		self.embed.add_field(name=f"Selected {self.selection_type}:", value=self.selection_list[self.current_index]['name'], inline=False)
		self.embed.set_thumbnail(url=self.selection_list[self.current_index]['thumbnail'])
		self.embed.set_footer(text=f"{self.ctx.bot.user.name} • Page {self.current_page}/{self.total_pages}")
		await self.msg_embed.edit(embed=self.embed)
		await self._wait_for_action()
		return

class ContainerSelectionMenu(SelectionMenu):
	"""A derived class of SelectionMenu for containers"""

	def __init__(self, ctx, message_object, selection_list, selection_type):
		super().__init__(ctx, message_object, selection_list, selection_type)

	async def show_page(self, page):
		"""Displays a menu page and sets selected item"""
		self.current_page = page
		self.current_index = self.current_page-1

		container_name = self.selection_list[self.current_index].name
		container_collection_name = self.selection_list[self.current_index].collection_name
		container_image_url = self.selection_list[self.current_index].image_url

		self.embed.clear_fields()
		self.embed.add_field(name=f"Selected {self.selection_type}:", value=container_name, inline=False)
		if self.selection_type == 'Souvenir Package':
			self.embed.add_field(name=f"Collection:", value=container_collection_name, inline=False)
		self.embed.set_thumbnail(url=container_image_url)
		self.embed.set_footer(text=f"{self.ctx.bot.user.name} • Page {self.current_page}/{self.total_pages}")
		await self.msg_embed.edit(embed=self.embed)
		await self._wait_for_action()
		return

class OpeningItemEmbedAnimation:
	"""Opening Item Embed Animation Class"""
	def __init__(self, ctx, container, item):
		self.ctx = ctx
		self.container = container
		self.skin_name, self.skin_image = item.get_random_variation()
		self.skin_description = item.description
		self.skin_lore = item.lore
		self.skin_collection = item.collection
		self.embed_colour = item.get_rarity_colour()

	def first(self):
		embed = discord.Embed(title="", description="", colour=0xc7c7c7)
		embed.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Opening your {self.container.name}..')
		return embed

	def full_detail(self):
		embed = discord.Embed(title=self.skin_name, description=self.skin_description, colour=self.embed_colour)
		embed.set_author(icon_url=self.ctx.author.avatar_url, name=f'You have 1 new item!')
		embed.add_field(name="Lore:", value=self.skin_lore, inline=False)
		if self.container.type == 'Souvenir Package':
			embed.add_field(name="Collection:", value=self.skin_collection, inline=False)
		embed.set_image(url=self.skin_image)
		return embed

	def min_detail(self):
		embed = discord.Embed(title="", description=self.skin_name, colour=self.embed_colour)
		embed.set_author(icon_url=self.ctx.author.avatar_url, name=f'{self.ctx.author.name} received a new item:')
		embed.set_footer(text=f"{self.ctx.bot.user.name} • This item was unboxed from a {self.container.name}")
		embed.set_thumbnail(url=self.skin_image)
		return embed

	async def send(self):
		msg = await self.ctx.send(embed=self.first())
		await asyncio.sleep(3)
		await msg.edit(embed=self.full_detail())
		await asyncio.sleep(10)
		await msg.edit(embed=self.min_detail())

class CaseOpening(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group(name='open')
	@commands.guild_only()
	@commands.cooldown(1, 8, commands.BucketType.user)
	@checks.member_in_guild(714585630289559664)
	async def open_(self, ctx):
		"""
		open case <name> - Opens a Case
		open souvenir <name> - Opens a Souvenir Package
		"""
		pass

	@open_.error
	async def command_error(self, ctx, error):
		"""Local command error handler"""
		if isinstance(error, checks.NotInGuild):
			embed = discord.Embed(title='', description='This command is exclusive to Neon Lounge members. \nPlease join our discord here: https://discord.gg/qDszrcF', colour=ctx.author.colour)
			embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
			await ctx.send(embed=embed)

		if isinstance(error, commands.CommandOnCooldown):
			msg="This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after))
			embed = discord.Embed(title="Cooling Down",
			description=msg,
			colour=0xbf0000)
			embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
			await ctx.send(embed=embed)
			return

	@open_.command(name='menu')
	async def menu(self, ctx):
		"""Displays the opening menu"""

		loading = discord.Embed(title="", description="", colour=0xc7c7c7)
		loading.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Loading options..')
		msg_embed = await ctx.send(embed=loading)

		menu_options = [{'name'      : 'Cases',
						 'thumbnail' : 'https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsRVx4MwFo5_T3eAQ3i6DMIW0X7ojiwoHax6egMOKGxj4G68Nz3-jCp4itjFWx-ktqfSmtcwqVx6sT/256fx256f',
						 'command'   : self.open_case(ctx)},
						{'name'      : 'Souvenir Packages',
						 'thumbnail' : 'https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsVlBndFBopqiqJggu0qHLIDkS7ou3lYXdxvOsMb-GxT9Vv8F12e-SrN3ziQDmqRU5Nm_3J5jVLFGaU5xorQ/256fx256f',
						 'command'   : self.open_souvenir_package(ctx)}]

		menu = OpeningSelectionMenu(ctx, msg_embed, menu_options, 'Opening')
		await menu.show_menu()
		await menu.show_page(1)
		await menu._destroy()
		await menu.selected_option['command']

	@open_.command(name='case')
	async def open_case(self, ctx, *, search_case : str = None):
		"""Opens a case"""

		loading = discord.Embed(title="", description="", colour=0xc7c7c7)
		loading.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Loading cases..')
		msg_embed = await ctx.send(embed=loading)

		if search_case:
			case_list = Case.get_container(search_case)
		else:
			case_list = Case.get_all_containers()

		if len(case_list) > 0:
			menu = ContainerSelectionMenu(ctx, msg_embed, case_list, 'Case')
			await menu.show_menu()
			await menu.show_page(1)

			selected_case = menu.selected_option
			await menu._destroy()
			selected_case._load_contents()
			item_set = selected_case.get_random_item_set()
			item = item_set.get_random_skin()
			item.has_stattrak = True

			opening_embed = OpeningItemEmbedAnimation(ctx, selected_case, item)
			await opening_embed.send()
		else:
			await ctx.send('I can\'t find the case you were looking for :(', delete_after=5)

	@open_.command(name='souvenir')
	async def open_souvenir_package(self, ctx, *, search_package : str = None):
		"""Opens a Souvenir Package"""

		loading = discord.Embed(title="", description="", colour=0xc7c7c7)
		loading.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name=f'Loading packages..')
		msg_embed = await ctx.send(embed=loading)

		if search_package:
			package_list = SouvenirPackage.get_container(search_package)
		else:
			package_list = SouvenirPackage.get_all_containers()

		if len(package_list) > 0:
			menu = ContainerSelectionMenu(ctx, msg_embed, package_list,'Souvenir Package')
			await menu.show_menu()
			await menu.show_page(1)

			selected_package = menu.selected_option
			await menu._destroy()
			selected_package._load_contents()
			item_set = selected_package.get_random_item_set()
			item = item_set.get_random_skin()
			item.is_souvenir = True

			opening_embed = OpeningItemEmbedAnimation(ctx, selected_package, item)
			await opening_embed.send()
		else:
			await ctx.send('I can\'t find a Souvenir Package you were looking for :(', delete_after=5)

	@open_.command(name='dev')
	@commands.is_owner()
	async def open_dev(self, ctx, selected_rarity : int, *, case : str = None):
		"""Opens a CS:GO case or pin capsule"""


def setup(bot):
	bot.add_cog(CaseOpening(bot))
