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
    if message.author == client.user:
        return 
    
    if message.content.startswith('$sb'): 
        command_line = message.content[len('$sb'):].strip()
        command_parts = command_line.split() 
        command = command_parts[0] if command_parts else ''
        args = command_parts[1:]

        username: str = str(message.author)
        discordID: str = message.author.id
        print('Passed prefix check')


        # Command routing
        if command == '/addaccount':
            print('started Add Account')
            await addAccount(args, username, discordID)
        elif command == '/addstock':
            await addStock(message, args, discordID)
        elif command == '/removestock':
            await removeStock(message, args, discordID)
        elif command == '/liststocks':
            await listStocks(message, discordID)
        elif command == '/deleteaccount':
            await deleteAccount(message, args, discordID)
        elif command == '/editstock':
            await editStock(message, args, discordID)
        else:
            await message.channel.send("""Sorry, I didn't recognize that command. Here is a list of my available commands:
                                       \n - $sb /addaccount
                                       \n - $sb /addstock [stock name] [notification price] [1 for above or 0 for below]
                                       \n - $sb /removestock [stock name]
                                       \n - $sb /listStocks
                                       \n - $sb /deleteAccount
                                       \n - $sb /editstock [stock name] [new price] [1 for above or 0 for below]""")

#Function to add account (Creates Tables if not exists and adds user)        
async def addAccount(message: Message, args: list, username: str, discordID: str):
    database.initializeTables(username, discordID)
    database.addUser(username, discordID)
    await message.channel.send(f"{message.author.mention}, your account has been created!")

#Adds stock to stocks table 
async def addStock(message: Message, args: list, discordID: str):
    if (len(args) == 3):
        addStockName = args[0]
        try:
            addStockNPrice = args[1]
            if (args[2]):
                    database.addStock(discordID,addStockName,addStockNPrice, True)
            else:
                    database.addStock(discordID,addStockName,addStockNPrice, False)
            await message.channel.send(f"{message.author.mention}, you have added {addStockName} at ${addStockNPrice}!")
        except ValueError:
            await message.channel.send("Please enter a valid Price")
    else: 
        await message.channel.send("Sorry, please check syntax\nUsage: $sb /addstock [stock name] [notification price] [1 for above or 0 for below]")

#removes stock from stocks table 
async def removeStock(message: Message, args: list, discordID: str):
    if (len(args) == 1):
        removeStockName = args[0]
        database.deleteStock(discordID,removeStockName)
        await message.channel.send(f"{message.author.mention}, {removeStockName} has been deleted!")
    else:
        await message.channel.send("Sorry, please check syntax\nUsage: $sb /removestock [stock name]")

#Lists active stocks being monitored 
async def listStocks(message: Message, discordID: str):
    stockList = '```\n' + '\n'.join(database.retrieveAll(discordID)) + '\n```'
    await message.channel.send(f"{message.author.mention}'s stocks:\n{stockList}")

#Deletes account and associated stocks 
async def deleteAccount(message: Message, discordID: str):
    database.deleteUser(discordID)
    await message.channel.send(f"{message.author.mention}, thank you for using Stock Bot!")

#Edit the notification price or direction 
async def editStock(message: Message, args: list, discordID: str):
    if (len(args) == 3):
        editStockName = args[0]
        editStockPrice = args[1]
        editStockAboveBelow = args[2]
        database.updateStock(discordID, editStockName, editStockPrice, editStockAboveBelow)
        await message.channel.send(f"{message.author.mention}, thank you for using Stock Bot!")
    else: 
        await message.channel.send("Sorry, please check syntax\nUsage: $sb /editstock [stock name] [new price] [1 for above or 0 for below]")


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


