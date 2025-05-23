import requests
from config.settings import ALPHAVANTAGE_API_KEY

def get_ticker_news(ticker_symbol, limit=5):
    """
    Retrieves the most recent news about the identified stock from Alpha Vantage.
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
        if response.status_code == 200:
            try:
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
                    return news_items
                elif "Information" in data:
                    print(f"API Error for {ticker_symbol} news: {data['Information']}")
                    return f"API Error for {ticker_symbol} news: {data['Information']}"
                elif "Note" in data:
                    print(f"API call limit Note: {data['Note']}")
                    return f"API Error for {ticker_symbol} news: {data['Note']}"
                else:
                    return f"No news found for {ticker_symbol}."
            except ValueError:
                print(f"Error: Could not decode JSON. Response: {response.text}")
                return f"Error fetching news for {ticker_symbol}: Invalid JSON response."
        else:
            print(f"Error: API request failed. Status Code: {response.status_code}, Response: {response.text}")
            return f"Error fetching news for {ticker_symbol}: HTTP {response.status_code}"
    except Exception as e:
        print(f"Error fetching news for {ticker_symbol}: {str(e)}")
        return f"Error fetching news for {ticker_symbol}: {str(e)}"
    
    
#################################    Checking the functionality   #################################

# if __name__ == "__main__":
#     sample_ticker = "TSLA"
#     news = get_ticker_news(sample_ticker)
#     if isinstance(news, list):
#         for article in news:
#             print(f"Title: {article['title']}")
#             print(f"URL: {article['url']}")
#             print(f"Sentiment: {article['overall_sentiment_label']}")
#             print("-" * 20)
#     else:
#         print(news)