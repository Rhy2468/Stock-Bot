#Stock bot
#import discord and dependencies to access stock market
from typing import Final
import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message
import threading

#import database 
import database

#import stockCommands
import stockCommands

#Load token from safe location 
load_dotenv() 
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

#Bot setup 
intents: Intents = Intents.default() 
intents.message_content = True 
client: Client = Client(intents=intents)

#Stock monitoring
stop_event = threading.Event() 

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
    parts = message_lowered.split()
    if (message_lowered.startswith("$sb")):
        print(f'[{channel}] {username}: "{userMessage}"')
        
    elif (message.content.startswith("$sb /addaccount")):
        database.initializeTablesTable(username, discordID)
        database.addUser(username, discordID)
    elif (message.content.startswith("$sb /addstock")):

        if (len(parts >= 4)):
            addStockName = parts[2]
            try:
                addStockNPrice = parts[3]
                if (parts[4]):
                    database.addStock(discordID,addStockName,addStockNPrice, True)
                else:
                    database.addStock(discordID,addStockName,addStockNPrice, False)
                await message.channel.send(f"{message.author.mention}, you have added {addStockName} at ${addStockNPrice}!")
            except ValueError:
                await message.channel.send("Please enter a valid Price")
        else: 
            await message.channel.send("Usage: $sb /addstock [stock name] [notification price] [1 for above or 0 for below]")
        startMonitoring(message.author, discordID)
    elif (message.content.startswith("$sb /removestock")):
        removeStockName = message.lowered[17:]
        database.deleteStock(message,removeStockName)
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


async def startMonitoring(message, discordID):
    notifyList = stockCommands.monitor_stocks(discordID, interval=60, stop_event=stop_event)
    if notifyList:
        for stock in notifyList:
            await message.channel.send(f"{message.author.mention}, {stock} has reached its goal!")
        return True
    return False 



#main entry point/ do not touch  
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


