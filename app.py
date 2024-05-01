#Stock bot
#import discord and dependencies to access stock market
from typing import Final
import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message
from stockCommands import get_response

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
    #IF author is user, return. 
    if message.author == client.user:
        return 
    
    message_lowered = message.content.lower()
    username: str = str(message.author)
    userMessage: str = message.content
    discordID: str = message.author.id
    channel: str = str(message.channel)
    if (message_lowered.startswith("$sb")):
        print(f'[{channel}] {username}: "{userMessage}"')
        await send_message(message, userMessage[3:0])
    elif (message.content.startswith("$sb /addaccount")):
        database.createTable()
        database.addUser(username, discordID)
    elif (message.content.startswith("$sb /addstock")):
        addStockName = message_lowered[14:17]
        addStockPrice = message_lowered[17:]
        database.addStock(discordID,addStockName,addStockPrice)
    elif (message.content.startswith("$sb /removestock")):
        removeStockName = message.lowered[17:]
        database.deleteStock(discordID,removeStockName)
    elif (message.content.startswith("$sb /editstock")):
        editStockName = message.lowered[15:18]
        editStockPrice = message.lowered[20:]
        database.updateStock(discordID, editStockName, editStockPrice)
    elif (message.content.startswith("$sb /liststocks")):
        stockList = database.retrieveAll(discordID)
    elif (message.content.startswith("$sb /deleteaccount")):
        database.deleteUser(discordID)
    else: 
        await message.author.send("Invalid Response (Please check spelling/formmating)\n Type $SB for the list of available commands")


    


#main entry point/ do not touch  
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


