import mysql.connector
from dotenv import load_dotenv

database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="localhostroot",
    database="StockBotData"
)

mycursor = database.cursor()

# Create tables if not exists
def createTable():
    mycursor.execute("CREATE TABLE IF NOT EXISTS User (username VARCHAR(50), discordID VARCHAR(50) PRIMARY KEY)")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Stocks (discordID VARCHAR(50), stockname VARCHAR(50), stockprice int, notificationPrice int, PRIMARY KEY (discordID, stockname), FOREIGN KEY(discordID) REFERENCES User(discordID))")

# Add user to User table
def addUser(username, discordID):
    mycursor.execute("INSERT INTO User (username, discordID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = VALUES(username)", (username, discordID))
    database.commit()

# Add stock to Stocks table
def addStock(discordID, stockName, stockPrice, notificationPrice):
    if discordID:
        mycursor.execute("INSERT INTO Stocks (discordID, stockname, stockprice, notificationPrice) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE stockprice = VALUES(stockprice), notificationPrice = VALUES(notificationPrice)", (discordID, stockName, stockPrice, notificationPrice))
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
    mycursor.execute("SELECT stockname, stockprice, notificationPrice FROM Stocks WHERE discordID = %s", (discordID,))
    stocks = mycursor.fetchall()
    stock_list = [f"{username}'s Stocks:"]
    for stock in stocks:
        stock_list.append(f"Stock Name: {stock[0]}, Stock Price: {stock[1]}, Notification Price: {stock[2]}")
    return '\n'.join(stock_list)

# Update stock price
def updateStock(discordID, stockName, newPrice):
    mycursor.execute("UPDATE Stocks SET stockprice = %s WHERE discordID = %s AND stockname = %s", (newPrice, discordID, stockName))
    database.commit()