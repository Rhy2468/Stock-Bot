#Stock bot
#import discord and dependencies to access stock market
from typing import Final
import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

#import database 
import database

#Load token from safe location 
load_dotenv() 
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

#Bot setup 
intents: Intents = Intents.default() 
intents.message_content = True 
client: Client = Client(intents=intents)

#Message 
async def send_message(message: Message, user_message: str) -> None:
    #Check if Intents was enabled
    if not user_message:
        print('Message was empty')
        return
    
    #Check if user wants to response in private using '?' as a prefix 
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


#Startup
@client.event
async def on_ready() -> None:
    print(F'{client.user} is now running!')

#Handling messages 
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return 
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


#main entry point/ do not touch  
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


