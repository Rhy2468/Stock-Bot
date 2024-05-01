import yfinance as yf 
import time 
import threading 

def getStockPrice(stockName):
    stock = yf.Ticker(stockName)
    todays_data = stock.history(period="id")
    return todays_data['Close'][-1] if not todays_data.empty else None 

def monitor_stocks(stockList, interval=60):
    def run():
        while True: 
            for stocks in stockList:
                price = getStockPrice(stockName)
                print(f"Current price of {stockName}: {price}")
                time.sleep(interval)/len(stockList)
    
    #keep function monitoring in different thread 
    thread = threading.Thread(target=run)
    thread.start()
    return thread 


# ticker_symbol = "AAPL"  # Example ticker symbol for Apple Inc.
# print("Current stock price:", get_stock_price(ticker_symbol))
# monitor_stocks(ticker_symbol, interval=300)  # Monitors every 5 minutes