from agents.ticker_news import get_ticker_news
from agents.ticker_price_change import get_ticker_price_change

def analyze_ticker(ticker_symbol, timeframe_for_change="last 7 days", news_limit=3):
    """
    Analyzes and summarizes the reason behind recent price movements
    using news and historical price data.
    """
    analysis_summary = {
        "ticker": ticker_symbol,
        "price_analysis": None,
        "recent_news_summary": None,
        "combined_notes": []
    }

    price_change_data = get_ticker_price_change(ticker_symbol, timeframe_for_change)
    analysis_summary["price_analysis"] = price_change_data

    news_data = get_ticker_news(ticker_symbol, limit=news_limit)
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

if __name__ == "__main__":
    sample_ticker = "TSLA"
    analysis = analyze_ticker(sample_ticker, timeframe_for_change="last 7 days", news_limit=3)
    
    print(f"--- Analysis for {analysis['ticker']} ---")
    if isinstance(analysis['price_analysis'], dict):
        print(f"Price Change ({analysis['price_analysis'].get('timeframe_requested')} from {analysis['price_analysis'].get('start_date_used')} to {analysis['price_analysis'].get('end_date_used')}): {analysis['price_analysis'].get('percent_change')}%")
    else:
        print(f"Price Analysis: {analysis['price_analysis']}")
    
    print("\nRecent News:")
    if isinstance(analysis['recent_news_summary'], list):
        for news_item in analysis['recent_news_summary']:
            print(f"- ({news_item['time_published']}) {news_item['title']} (Sentiment: {news_item['overall_sentiment_label']})")
    else:
        print(analysis['recent_news_summary'])
        
    print("\nCombined Notes:")
    for note in analysis['combined_notes']:
        print(f"- {note}")

#####################################       Checking the Functionality of the code       #####################################

# if __name__ == '__main__':
#     sample_ticker = "TSLA"
#     analysis = analyze_ticker(sample_ticker, timeframe_for_change="last 7 days", news_limit=3)
    
#     print(f"--- Analysis for {analysis['ticker']} ---")
#     if isinstance(analysis['price_analysis'], dict):
#         print(f"Price Change ({analysis['price_analysis'].get('timeframe_requested')} from {analysis['price_analysis'].get('start_date_used')} to {analysis['price_analysis'].get('end_date_used')} ): {analysis['price_analysis'].get('percent_change')}%")
#     else:
#         print(f"Price Analysis: {analysis['price_analysis']}")
    
#     print("\nRecent News:")
#     if isinstance(analysis['recent_news_summary'], list):
#         for news_item in analysis['recent_news_summary']:
#             print(f"- ({news_item['time_published']}) {news_item['title']} (Sentiment: {news_item['overall_sentiment_label']})")
#     else:
#         print(analysis['recent_news_summary'])
        
#     print("\nCombined Notes:")
#     for note in analysis['combined_notes']:
#         print(f"- {note}")

#     print("\n--- Analysis for another ticker (NVDA) ---")
#     analysis_nvda = analyze_ticker("NVDA", timeframe_for_change="today", news_limit=2)
#     if isinstance(analysis_nvda['price_analysis'], dict):
#          print(f"Price Change ({analysis_nvda['price_analysis'].get('timeframe')}): {analysis_nvda['price_analysis'].get('percent_change')}%")
#     else:
#         print(f"Price Analysis: {analysis_nvda['price_analysis']}")

#     print("\nRecent News:")
#     if isinstance(analysis_nvda['recent_news_summary'], list):
#         for news_item in analysis_nvda['recent_news_summary']:
#             print(f"- ({news_item['time_published']}) {news_item['title']} (Sentiment: {news_item['overall_sentiment_label']})")
#     else:
#         print(analysis_nvda['recent_news_summary'])

#     print("\nCombined Notes:")
#     for note in analysis_nvda['combined_notes']:
#         print(f"- {note}")