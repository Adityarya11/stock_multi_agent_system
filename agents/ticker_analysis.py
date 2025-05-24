from agents.ticker_news import get_ticker_news
from agents.ticker_price_change import get_ticker_price_change

def analyze_ticker(ticker_symbol, timeframe_for_change="last 7 days", news_limit=3, ALPHAVANTAGE_API_KEY=None):
    """
    Analyzes and summarizes the reason behind recent price movements using news and historical price data.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., "TSLA").
        timeframe_for_change (str): The timeframe for analysis (e.g., "last 7 days"). Defaults to "last 7 days".
        news_limit (int): Number of news articles to consider. Defaults to 3.
        ALPHAVANTAGE_API_KEY (str): Alpha Vantage API key.
    Returns:
        dict: Analysis summary with price, news, and notes.
    """
    if not ALPHAVANTAGE_API_KEY:
        return {"error": "Alpha Vantage API key is required."}

    analysis_summary = {
        "ticker": ticker_symbol,
        "price_analysis": None,
        "recent_news_summary": None,
        "combined_notes": []
    }

    price_change_data = get_ticker_price_change(ticker_symbol, timeframe_for_change, ALPHAVANTAGE_API_KEY)
    analysis_summary["price_analysis"] = price_change_data

    news_data = get_ticker_news(ticker_symbol, ALPHAVANTAGE_API_KEY, news_limit)
    if isinstance(news_data, list) and news_data:
        analysis_summary["recent_news_summary"] = news_data
        news_titles = [n['title'] for n in news_data]
        analysis_summary["combined_notes"].append(f"Recent news headlines: {'; '.join(news_titles)}.")
    elif isinstance(news_data, str):
        analysis_summary["combined_notes"].append(f"News fetching issue: {news_data}")
    else:
        analysis_summary["combined_notes"].append("No recent news found.")

    if isinstance(price_change_data, dict):
        percent_change = price_change_data.get("percent_change", 0)
        change_direction = "increased" if percent_change > 0 else "decreased" if percent_change < 0 else "remained relatively stable"
        note = f"Over the {timeframe_for_change} (from {price_change_data.get('start_date_used')} to {price_change_data.get('end_date_used')}), {ticker_symbol} stock price has {change_direction} by {abs(percent_change)}% (changed by ${price_change_data.get('price_change',0)})."
        analysis_summary["combined_notes"].insert(0, note)

        if abs(percent_change) > 5 and isinstance(news_data, list) and news_data:
            analysis_summary["combined_notes"].append(f"The significant price change might be related to the recent news. Check news details for correlation.")
        elif abs(percent_change) <= 1 and isinstance(news_data, list) and news_data:
            analysis_summary["combined_notes"].append(f"Price movement was minor. News context is still important for overall outlook.")
    elif isinstance(price_change_data, str):
        analysis_summary["combined_notes"].insert(0, f"Price change analysis issue: {price_change_data}")

    return analysis_summary