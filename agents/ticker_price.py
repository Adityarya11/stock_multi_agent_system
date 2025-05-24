import requests
import time

def get_ticker_price(ticker_symbol, ALPHAVANTAGE_API_KEY):
    """
    Fetches the current price of the stock from Alpha Vantage.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., "AAPL").
        ALPHAVANTAGE_API_KEY (str): Alpha Vantage API key.
    Returns:
        dict: Price information or error details.
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
        response.raise_for_status()
        data = response.json()
        if "Global Quote" in data and data["Global Quote"]:
            global_quote = data["Global Quote"]
            price_info = {
                "symbol": global_quote.get("01. symbol", ticker_symbol),
                "price": global_quote.get("05. price"),
                "latest_trading_day": global_quote.get("07. latest trading day"),
                "previous_close": global_quote.get("08. previous close"),
                "change": global_quote.get("09. change"),
                "change_percent": global_quote.get("10. change percent")
            }
            if price_info["price"]:
                return price_info
            else:
                return {"error": f"Could not retrieve current price for {ticker_symbol}. The symbol might be invalid or data unavailable."}
        elif "Information" in data or "Note" in data:
            error_msg = data.get("Information", data.get("Note", "API limit reached or invalid key"))
            print(f"API Error for {ticker_symbol} price: {error_msg}")
            if "call frequency" in error_msg.lower() or "limit" in error_msg.lower():
                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return get_ticker_price(ticker_symbol, ALPHAVANTAGE_API_KEY)  # Retry
            return {"error": f"API Error for {ticker_symbol} price: {error_msg}"}
        else:
            print(f"No price data found for {ticker_symbol}. Response: {data}")
            return {"error": f"No price data found for {ticker_symbol}."}
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching price for {ticker_symbol}: {e}")
        return {"error": f"Network error fetching price for {ticker_symbol}: {e}"}
    except ValueError as e:
        print(f"JSON decode error for {ticker_symbol}: {e}")
        return {"error": f"JSON decode error for {ticker_symbol}: {e}"}
    except Exception as e:
        print(f"Unexpected error fetching price for {ticker_symbol}: {e}")
        return {"error": f"Unexpected error fetching price for {ticker_symbol}: {e}"}