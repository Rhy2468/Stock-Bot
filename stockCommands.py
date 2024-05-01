import yfinance as yf 
import time 
import threading 

#import database
import database

def getStockPrice(stockName):
    stock = yf.Ticker(stockName)
    todays_data = stock.history(period="id")
    return todays_data['Close'][-1] if not todays_data.empty else None 

def monitor_stocks(discordID, interval=60, stop_event = None):
    def run():
        while not stop_event.is_set(): 
            stockList = database.retrieveMonitoringAll(discordID)
            notifyStocks = []
            for stockName in stockList:
                notificationPrice = database.getNotificationPrice(discordID, stockName)
                price = getStockPrice(stockName)
                print(f"Current price of {stockName}: {price}")
                aboveBelow = database.getAboveBelowStatus(discordID, stockName)

                if aboveBelow and price >= notificationPrice:
                    notifyStocks.append(stockName)
                
                if not aboveBelow and price <= notificationPrice:
                    notifyStocks.append(stockName)
                
                time.sleep(interval)/len(stockList)
            return notifyStocks
    
    #keep function monitoring in different thread 
    thread = threading.Thread(target=run)
    thread.start()
    return thread 


# ticker_symbol = "AAPL"  # Example ticker symbol for Apple Inc.
# print("Current stock price:", get_stock_price(ticker_symbol))
# monitor_stocks(ticker_symbol, interval=300)  # Monitors every 5 minutes