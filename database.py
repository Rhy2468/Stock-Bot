import mysql.connector
from dotenv import load_dotenv
import stockCommands

database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="localhostroot",
    database="StockBotData"
)

mycursor = database.cursor()

# Create tables if not exists
# Initialize tables
def initializeTables(username, discordID):
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        username VARCHAR(50),
        discordID VARCHAR(50) PRIMARY KEY
    )
    """)

    mycursor.execute("""
    INSERT INTO User (username, discordID) VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE username = VALUES(username)
    """, (username, discordID))

    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Stocks (
        discordID VARCHAR(50),
        stockname VARCHAR(50),
        notificationPrice INT,
        aboveBelow BOOLEAN,
        PRIMARY KEY (discordID, stockname),
        FOREIGN KEY (discordID) REFERENCES User(discordID)
    )
    """)
    
    database.commit()

# Add user to User table
def addUser(username, discordID):
    mycursor.execute("INSERT INTO User (username, discordID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = VALUES(username)", (username, discordID))
    database.commit()

# Add stock to Stocks table
def addStock(discordID, stockName, notificationPrice, aboveBelow):
    if discordID and stockCommands.getStockPrice(stockName):
        mycursor.execute("INSERT INTO Stocks (discordID, stockname, notificationPrice, aboveBelow) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE notificationPrice = VALUES(notificationPrice), aboveBelow = VALUES(aboveBelow)", (discordID, stockName, notificationPrice, aboveBelow))
        database.commit()
        return True
    return False

# Delete stock from Stocks table
def deleteStock(discordID, stockName):
    mycursor.execute("DELETE FROM Stocks WHERE discordID = %s AND stockname = %s", (discordID, stockName))
    database.commit()

# Delete user and associated stocks
def deleteUser(discordID):
    mycursor.execute("DELETE FROM Stocks WHERE discordID = %s", (discordID,))
    mycursor.execute("DELETE FROM User WHERE discordID = %s", (discordID,))
    database.commit()

# Retrieve all stocks associated with a user
def retrieveAll(discordID):
    mycursor.execute("SELECT username FROM User WHERE discordID = %s", (discordID,))
    username = mycursor.fetchone()[0]
    mycursor.execute("SELECT stockname, notificationPrice, aboveBelow FROM Stocks WHERE discordID = %s", (discordID,))
    stocks = mycursor.fetchall()
    stock_list = [f"{username}'s Stocks:"]
    for stock in stocks:
        status = "ABOVE" if stock[2] else "BELOW"
        stock_list.append(f"Stock Name: {stock[0]}, Notification Price: {stock[1]}, Status: {status}")
    return '\n'.join(stock_list)

#Returns list of all active stocks 
def retrieveMonitoringAll(discordID):
    mycursor.execute("SELECT username FROM User WHERE discordID = %s", (discordID,))
    mycursor.execute("SELECT stockname FROM Stocks WHERE discordID = %s", (discordID,))
    stocks = mycursor.fetchall()
    stock_list = []
    for stock in stocks:
        stock_list.append(f"Stock Name: {stock[0]}")
    return stock_list

#Returns notification price of a stock
def getNotificationPrice(discordID, stockName):
    mycursor.execute("SELECT notificationPrice FROM Stocks WHERE discordID = %s AND stockname = %s", (discordID, stockName))
    result = mycursor.fetchone()
    return result[0] if result else None

# Update notification price
def updateStock(discordID, stockName, newPrice, aboveBelow):
    mycursor.execute("UPDATE Stocks SET notificationPrice = %s, aboveBelow = %s WHERE discordID = %s AND stockname = %s", (newPrice, aboveBelow, discordID, stockName))
    database.commit()

#Returns if user wants to be notified when price is above or below target
def getAboveBelowStatus(discordID, stockName):
    mycursor.execute("SELECT aboveBelow FROM Stocks WHERE discordID = %s AND stockname = %s", (discordID, stockName))
    result = mycursor.fetchone()
    return result[0] if result else None
