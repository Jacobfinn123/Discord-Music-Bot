### This project is for demonstration purposes only!
#
Discord Music Bot is a tool which can be used to play songs (or any youtube video) in your discord channel. This tool supports search querying, queues, skipping, and more.

Want to use a hosted version of this bot? Use the discord invite link [here](https://discord.com/oauth2/authorize?client_id=1028041338349944832)
# Table of Contents
- [Setup](#setup)
- [Commands](#commands)
  - [Play](#!play)
  - [Skip](#!skip)
  - [Stop](#!stop)
  - [Queue](#!queue)

# Setup
1. Clone/download the repository.
2. Install Python 3.10.
3. Open the repository folder in a terminal window.
   1. Create a virtual environment. ```python -m venv env```
   2. Activate the newly created virtual environment. ```.\env\Scripts\activate```
   3. Install the depedencies. ```pip install -r requirements.txt```
4. Open the project folder in your IDE (PyCharm preferred).
5. Run *main.py*
## Commands
## !play
This command will add a song to the queue.
Type ```!play <search query>``` in any channel. 

Example of !play command with a search query<br>
![Discord_LxPFCGENM8](https://github.com/Jacobfinn123/Discord-Music-Bot/assets/25854089/fa3d18ec-9d22-477a-9d1d-b1886cbf8d5c)

Example of !play command with a Youtube URL<br>
![Discord_m1GAnjdyco](https://github.com/Jacobfinn123/Discord-Music-Bot/assets/25854089/389fa77f-4b21-4b81-ab4c-43af170647e1)

The bot will reply with the song you've just added to the queue and other details such as the duration and upcoming queue.<br>
![Discord_t5HQQx4FU4](https://github.com/Jacobfinn123/Discord-Music-Bot/assets/25854089/520484e8-8b24-4786-8253-04b48fd32474)


## !skip
This command will skip the song currently playing.<br>
Type ```!skip``` in any channel. 

## !stop
This command will make the bot leave the channel and clear the queue.<br>
Type ```!stop``` in any channel. 

## !queue
This command will display all songs currently in the queue, you paginate through 10 songs at a time.<br>
Type ```!queue``` in any channel. 

Example of !queue command<br>
![Discord_84CPsALarf](https://github.com/Jacobfinn123/Discord-Music-Bot/assets/25854089/db434096-89c6-4ea5-9b6f-2770beeb4e3c)

**_NOTE:_** Press the "✖️" to delete the message.
