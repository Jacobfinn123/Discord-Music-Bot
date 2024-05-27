import discord, datetime, logging
from discord.ext import commands, tasks
from discord.ui.view import View
from Song import Song
from util import get_song, format_search_query
from typing import List

with open("discord_token.txt", 'r') as r:
	token = r.read()

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)


class LeftButton(discord.ui.Button):
	def __init__(
		self,
		message_obj,
		song_queue: List[Song],
		index: int
	):
		self.message_obj = message_obj
		self.song_queue = song_queue
		self.index = index
		super().__init__(label="", style=discord.ButtonStyle.primary, emoji="⬅️", disabled=((index+1)*10)-10 <= 0)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		await send_queue_message(self.message_obj, self.song_queue, self.index-1)


class DeleteButton(discord.ui.Button):
	def __init__(
		self,
		message_obj,
	):
		self.message_obj = message_obj
		super().__init__(label="", style=discord.ButtonStyle.primary, emoji="❌")

	async def callback(self, interaction: discord.Interaction):
		# Display song queue
		await interaction.response.defer()
		await self.message_obj.delete()


class RightButton(discord.ui.Button):
	def __init__(
		self,
		message_obj,
		song_queue: List[Song],
		index: int
	):
		self.message_obj = message_obj
		self.song_queue = song_queue
		self.index = index
		super().__init__(label="", style=discord.ButtonStyle.primary, emoji="➡️", disabled=(index+1)*10 >= len(song_queue))

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		await send_queue_message(self.message_obj, self.song_queue, self.index+1)


async def send_queue_message(message_obj, song_queue, index: int = 0):
	view = View(timeout=None)
	view.add_item(LeftButton(message_obj, song_queue, index))
	view.add_item(DeleteButton(message_obj))
	view.add_item(RightButton(message_obj, song_queue, index))

	# Display song queue
	upcoming_queue = "\n".join(f"{(x + 1) + (index*10)}: {i.title} ({Song.format_song_length(i.song_length)})" for x, i in enumerate(song_queue[index*10:index*10+10]))
	if not upcoming_queue:
		upcoming_queue = "Empty!"

	embed = discord.Embed(description='MUSICAL BOT', color=5143545)
	embed.set_author(name="MUSIC", icon_url='https://i.imgur.com/8HisluE.png')
	embed.add_field(name="Upcoming Queue:", value=upcoming_queue, inline=False)
	embed.timestamp = datetime.datetime.utcnow()
	embed.set_footer(text="Powered by powerful guy")

	await message_obj.edit(content="", embed=embed, view=view)


@client.event
async def on_ready():
	logging.info(f'{client.user} has connected to Discord!')
	await client.add_cog(Commands())


class Commands(commands.Cog):
	def __init__(self):
		self.song_queue: List[Song] = []
		self.disconnect_timer = datetime.datetime.now().timestamp() + 1e9
		self.current_playing_song: Song = None
		self.voice_channel = None
		self.message_id: int = None

		self.play_queue.start()

	async def get_upcoming_queue(self):
		upcoming_queue = "\n".join(f"{index + 1}: {i.title} ({Song.format_song_length(i.song_length)})" for index, i in enumerate(self.song_queue[:10]))
		if not upcoming_queue:
			upcoming_queue = "Empty!"

		return upcoming_queue

	async def send_queue_webhook(self, song: Song = None):
		if not song:
			song = self.current_playing_song

		embed = discord.Embed(description='MUSICAL BOT', color=5143545)
		embed.set_author(name="MUSIC", icon_url='https://i.imgur.com/8HisluE.png')
		embed.add_field(name="Song:", value=f"[{song.title}]({song.video_url})", inline=False)
		embed.add_field(name="Duration:", value=Song.format_song_length(song.song_length), inline=False)
		embed.set_image(url=song.thumbnail_url)
		embed.add_field(name="Requested by:", value=F"<@{song.requester_discord_id}>", inline=False)
		embed.add_field(name="Upcoming Queue:", value=await self.get_upcoming_queue(), inline=False)
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_footer(text="Powered by powerful guy")

		# TODO: Check if there are x messages between editable message, if y > x: send new message
		channel = client.get_channel(song.requester_channel_id)
		if not self.message_id:
			message = await channel.send(embed=embed)
			self.message_id = message.id
		else:
			message = client.get_channel(song.requester_channel_id).get_partial_message(self.message_id)
			await message.edit(embed=embed)

	@tasks.loop(seconds=1)
	async def play_queue(self):
		if datetime.datetime.now().timestamp() > self.disconnect_timer and self.voice_channel.is_connected():
			logging.info("Leaving channel for inactivity")
			await self.voice_channel.disconnect()

		if not self.song_queue:
			return

		if not self.voice_channel.is_playing():
			logging.info("Resetting disconnect timer")
			self.disconnect_timer = datetime.datetime.now().timestamp() + 300  # 5 minutes
			current_song = self.song_queue.pop(0)
			self.current_playing_song = current_song

			ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
			source = await discord.FFmpegOpusAudio.from_probe(current_song.audio_url, **ffmpeg_options)

			self.voice_channel.play(source)
			self.voice_channel.is_playing()
			await self.send_queue_webhook()

	@commands.command(pass_context=True)
	async def play(self, ctx, *url):

		if str(ctx.channel.id) != "746444482349629465":
			await ctx.reply("Wrong channel.")

		query = format_search_query(" ".join(url))

		if not query:
			await ctx.reply("No song found with that search query!")
			return

		# Bot join channel and set voice_channel
		member = ctx.guild.get_member(ctx.author.id)

		vc = self.voice_channel
		if not self.voice_channel:
			vc = await member.voice.channel.connect()
		elif not self.voice_channel.is_connected():
			vc = await member.voice.channel.connect()

		self.voice_channel = vc

		# Get & Add Song to queue
		song = get_song(query)
		song.requester_discord_id = ctx.message.author.id
		song.requester_channel_id = ctx.message.channel.id
		self.song_queue.append(song)
		await ctx.message.delete()

		# Send queue added webhook (ignores otherwise as webhook is sent during play)
		if len(self.song_queue) > 1:
			await self.send_queue_webhook(song)

	@commands.command(pass_context=True)
	async def skip(self, ctx):
		if self.voice_channel.is_playing():
			self.voice_channel.stop()
			await self.send_queue_webhook()
			self.current_playing_song = None
		else:
			await ctx.send("Nothing playing!")

		await ctx.message.delete()

	@commands.command(pass_context=True)
	async def clear(self, ctx):
		# Clears queue
		self.song_queue = []
		await ctx.reply("Song queue cleared!", delete_after=3)
		await ctx.message.delete()
		if self.voice_channel.is_playing():
			self.voice_channel.stop()

	@commands.command(pass_context=True)
	async def queue(self, ctx):
		# Displays queue
		await ctx.message.delete()
		message = await ctx.send(".")
		await send_queue_message(message, self.song_queue)

	@commands.command(pass_context=True)
	async def stop(self, ctx):
		if self.voice_channel.is_playing():
			await self.voice_channel.disconnect()  # Disconnect

		# Delete command after the audio is done playing.
		await ctx.message.delete()


client.run(token)
