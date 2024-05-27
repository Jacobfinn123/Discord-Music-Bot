import re, urllib.parse, urllib.request, yt_dlp
from Song import Song


def format_search_query(query: str) -> str:
	"""
	Generates a youtube link based on the query inputted.
	:param query: The search term used in "!play" command, either a link or search query.
	:return: Youtube URL
	"""
	if "shorts" in query:  # Youtube shorts link posted
		formatted_query = f"https://www.youtube.com/watch?v={query.split('shorts/')[1]}"
	elif "watch?v=" in query:  # Direct youtube link posted
		return query
	else:
		formatted_query = search_music(query)  # Search query posted

	return formatted_query


def search_music(music_name: str) -> str:
	"""
	Searches Youtube for relevant results of search query.
	:param music_name: Search query
	:return: Youtube URL
	"""
	query_string = urllib.parse.urlencode({"search_query": music_name})
	response = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

	search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode())
	if not search_results:
		return None

	if len(search_results) == 1:
		return f"https://www.youtube.com/watch?v={search_results[0]}"

	return f"https://www.youtube.com/watch?v={search_results[1]}"  # Skips 0th index for accuracy


def get_song(url: str) -> Song:
	"""
	Gets the Song object from Youtube URL
	:param url: Youtube URL
	:return: Song object
	"""
	ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{	'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}

	new_song = Song()
	new_song.video_url = url
	new_song.video_id = url.split("v=")[1]

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		title = info['title']
		new_song.title = title
		# Gets the Audio File URL (at different index for each info)
		new_song.thumbnail_url = info['thumbnails'][-1]['url']
		for i in info['formats']:
			if new_song.song_length is None:
				if i.get("fragments"):
					new_song.song_length = info['formats'][0]['fragments'][0]['duration']
			if "googlevideo.com" in i['url']:
				audio_url = i['url']
				new_song.audio_url = audio_url
				break

	return new_song
