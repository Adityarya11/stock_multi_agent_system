import requests
import time

def get_ticker_news(ticker_symbol, ALPHAVANTAGE_API_KEY, limit=5):
    """
    Retrieves the most recent news about the identified stock from Alpha Vantage.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., "AAPL").
        ALPHAVANTAGE_API_KEY (str): Alpha Vantage API key.
        limit (int): Number of news articles to retrieve. Defaults to 5.
    Returns:
        dict: News items or error details.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker_symbol,
        "limit": str(limit),
        "apikey": ALPHAVANTAGE_API_KEY,
        "datatype": "json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "feed" in data:
            news_items = []
            for item in data["feed"][:limit]:
                news_items.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "time_published": item.get("time_published"),
                    "overall_sentiment_label": item.get("overall_sentiment_label")
                })
            return {"news": news_items}
        elif "Information" in data or "Note" in data:
            error_msg = data.get("Information", data.get("Note", "API limit reached or invalid key"))
            print(f"API Error for {ticker_symbol} news: {error_msg}")
            if "call frequency" in error_msg.lower() or "limit" in error_msg.lower():
                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return get_ticker_news(ticker_symbol, ALPHAVANTAGE_API_KEY, limit)  # Retry
            return {"error": f"API Error for {ticker_symbol} news: {error_msg}"}
        else:
            print(f"No news found for {ticker_symbol}. Response: {data}")
            return {"error": f"No news found for {ticker_symbol}."}
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching news for {ticker_symbol}: {e}")
        return {"error": f"Network error fetching news for {ticker_symbol}: {e}"}
    except ValueError as e:
        print(f"JSON decode error for {ticker_symbol}: {e}")
        return {"error": f"JSON decode error for {ticker_symbol}: {e}"}
    except Exception as e:
        print(f"Unexpected error fetching news for {ticker_symbol}: {e}")
        return {"error": f"Unexpected error fetching news for {ticker_symbol}: {e}"}