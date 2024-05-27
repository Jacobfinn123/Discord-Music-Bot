from dataclasses import dataclass
import random


@dataclass()
class Song:
	video_url: str = None
	video_id: str = None
	thumbnail_url: str = None
	title: str = None
	audio_url: str = None
	song_length: int = None  # In seconds
	requester_discord_id: int = None
	requester_channel_id: int = None

	def __repr__(self):
		return f"Song("f"video_url={self.video_url!r}, "f"video_id={self.video_id!r}, "f"title={self.title!r}, "f"audio_url={self.audio_url!r}, "f"song_length={self.song_length!r}"f")"

	@staticmethod
	def format_song_length(song_length: int) -> str:
		hours = int(song_length // 3600)
		minutes = int((song_length % 3600) // 60)
		seconds = int(song_length % 60)

		if hours > 0:
			return f"{hours}:{minutes:02}:{seconds:02}"
		else:
			return f"{minutes}:{seconds:02}"

	@staticmethod
	def _generate_random_songs(n):  # Used for testing
		songs = []
		for i in range(n):
			song = Song(
				video_url=f"https://example.com/video{i}",
				video_id=f"video{i}",
				thumbnail_url=f"https://example.com/thumbnail{i}.jpg",
				title=f"Song Title {i}",
				audio_url=f"https://example.com/audio{i}.mp3",
				song_length=random.randint(60, 7200),  # Random length between 1 minute and 2 hours
				requester_discord_id=random.randint(100000, 999999),
				requester_channel_id=random.randint(1000, 9999)
			)
			songs.append(song)
		return songs
