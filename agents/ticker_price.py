import requests
from config.settings import ALPHAVANTAGE_API_KEY

def get_ticker_price(ticker_symbol):
    """
    Fetches the current price of the stock from Alpha Vantage.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker_symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
        "datatype": "json"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                if "Global Quote" in data and data["Global Quote"]:
                    global_quote = data["Global Quote"]
                    price_info = {
                        "symbol": global_quote.get("01. symbol"),
                        "price": global_quote.get("05. price"),
                        "latest_trading_day": global_quote.get("07. latest trading day"),
                        "previous_close": global_quote.get("08. previous close"),
                        "change": global_quote.get("09. change"),
                        "change_percent": global_quote.get("10. change percent")
                    }
                    if price_info["price"]:
                        return price_info
                    else:
                        return f"Could not retrieve current price for {ticker_symbol}. The symbol might be invalid or data unavailable."
                elif "Information" in data:
                    print(f"API Error for {ticker_symbol} price: {data['Information']}")
                    return f"API Error for {ticker_symbol} price: {data['Information']}"
                elif "Note" in data:
                    print(f"API call limit Note: {data['Note']}")
                    return f"API Error for {ticker_symbol} price: {data['Note']}"
                else:
                    return f"No price data found for {ticker_symbol}."
            except ValueError:
                print(f"Error: Could not decode JSON. Response: {response.text}")
                return f"Error fetching price for {ticker_symbol}: Invalid JSON response."
        else:
            print(f"Error: API request failed. Status Code: {response.status_code}, Response: {response.text}")
            return f"Error fetching price for {ticker_symbol}: HTTP {response.status_code}"
    except Exception as e:
        print(f"Error fetching price for {ticker_symbol}: {str(e)}")
        return f"Error fetching price for {ticker_symbol}: {str(e)}"

if __name__ == "__main__":
    sample_ticker = "NVDA"
    price_data = get_ticker_price(sample_ticker)
    if isinstance(price_data, dict):
        print(f"Symbol: {price_data['symbol']}")
        print(f"Current Price: {price_data['price']}")
        print(f"Change Percent: {price_data['change_percent']}")
    else:
        print(price_data)


#####################################       Checking the Functionality of the code       #####################################
# if __name__ == '__main__':
#     # Example usage:
#     sample_ticker = "NVDA" # From identify_ticker
#     price_data = get_ticker_price(sample_ticker)
#     if isinstance(price_data, dict):
#         print(f"Symbol: {price_data['symbol']}")
#         print(f"Current Price: {price_data['price']}")
#         print(f"Change Percent: {price_data['change_percent']}")
#     else:
#         print(price_data)

#     sample_ticker_invalid = "NONEXISTENTTICKER"
#     price_data_invalid = get_ticker_price(sample_ticker_invalid)
#     print(price_data_invalid)