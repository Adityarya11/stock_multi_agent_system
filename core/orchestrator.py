import re
from agents.identify_ticker import identify_ticker, COMMON_TICKERS
from agents.ticker_news import get_ticker_news
from agents.ticker_price import get_ticker_price
from agents.ticker_price_change import get_price_change
from agents.ticker_analysis import analyze_ticker

def handle_query(user_query):
    """
    Orchestrates the response to a user query by calling appropriate agents.
    """
    print(f"Received query: \"{user_query}\"")
    response = {"ticker_identified": None, "data": None, "error": None}

    ticker = identify_ticker(user_query)
    if not ticker:
        potential_tickers = re.findall(r'\b([A-Z]{1,5})\b', user_query)
        if potential_tickers:
             if any(company in user_query.lower() for company in COMMON_TICKERS.keys()):
                response["error"] = f"Could not definitively identify a supported stock ticker for a known company in your query: '{user_query}'. Please be more specific or use the ticker symbol."
                return response
             elif potential_tickers:
                  ticker = potential_tickers[0] # Take the first one
                  print(f"Identified potential ticker symbol based on ALL CAPS: {ticker}")
             else:
                response["error"] = f"Could not identify a stock ticker in your query: '{user_query}'. Supported companies are: {', '.join(COMMON_TICKERS.keys())}."
                return response
        else:
             response["error"] = f"Could not identify a stock ticker in your query: '{user_query}'. Supported companies are: {', '.join(COMMON_TICKERS.keys())}."
             return response


    response["ticker_identified"] = ticker
    print(f"Identified ticker: {ticker}")

    query_lower = user_query.lower()

    if "why" in query_lower and ("drop" in query_lower or "down" in query_lower or "up" in query_lower or "rally" in query_lower or "change" in query_lower or "move" in query_lower) or \
       "what's happening" in query_lower or "analysis" in query_lower or "analyze" in query_lower:
        timeframe = "today" 
        if "today" in query_lower:
            timeframe = "today"
        elif "last week" in query_lower or "past week" in query_lower :
             timeframe = "last 7 days" 
        elif "last 7 days" in query_lower: 
             timeframe = "last 7 days"
        elif "last month" in query_lower:
             timeframe = "last month"
        elif "recently" in query_lower:
            timeframe = "last 7 days" 
        
        print(f"Calling ticker_analysis for {ticker} with timeframe '{timeframe}'")
        response["data"] = analyze_ticker(ticker, timeframe_for_change=timeframe)

    elif "news" in query_lower:
        print(f"Calling ticker_news for {ticker}")
        response["data"] = get_ticker_news(ticker)

    elif ("how has" in query_lower and "changed" in query_lower) or "price change" in query_lower:
        timeframe = "today" # Default
        match_days = re.search(r"last (\d+) days", query_lower)
        match_week = re.search(r"last week", query_lower)
        match_month = re.search(r"last month", query_lower)

        if "today" in query_lower:
            timeframe = "today"
        elif match_days:
            timeframe = f"last {match_days.group(1)} days"
        elif match_week:
             timeframe = "last week" # parse_timeframe will handle this
        elif match_month:
             timeframe = "last month"
        
        print(f"Calling ticker_price_change for {ticker} with timeframe '{timeframe}'")
        response["data"] = get_price_change(ticker, timeframe)

    elif "price" in query_lower or "current stock price" in query_lower or "what is the stock price" in query_lower:
        print(f"Calling ticker_price for {ticker}")
        response["data"] = get_ticker_price(ticker)
        
    else:

        print(f"Unclear intent for {ticker}, providing general analysis for 'last 7 days'.")
        response["data"] = analyze_ticker(ticker, timeframe_for_change="last 7 days")
        if not response["data"]: # If analyze_ticker had an issue
            response["error"] = f"Could not retrieve a default analysis for {ticker}."


    if isinstance(response["data"], str) and ("API Error" in response["data"] or "Could not" in response["data"] or "No " in response["data"] or "issue" in response["data"]):
        response["error"] = response["data"]
    elif isinstance(response["data"], dict) and ("error" in response["data"] or "API Error" in response["data"].get("price_analysis", {}) or "API Error" in response["data"].get("price_analysis", "")): # check nested error for analysis
        if isinstance(response["data"].get("price_analysis"), str) and "API Error" in response["data"]["price_analysis"]:
            response["error"] = response["data"]["price_analysis"]
        elif isinstance(response["data"].get("price_analysis"), dict) and "error" in response["data"]["price_analysis"]:
             response["error"] = response["data"]["price_analysis"]["error"]
        elif "error" in response["data"]:
            response["error"] = response["data"]["error"]

    return response


#####################################       Checking the Functionality of the code       #####################################

# if __name__ == '__main__':
#     # Test cases based on example queries [cite: 7, 8]
#     queries = [
#         "Why did Tesla stock drop today?",
#         "What's happening with Palantir stock recently?",
#         "How has Nvidia stock changed in the last 7 days?",
#         "What is the current stock price for Google?",
#         "Tell me the news for MSFT.",
#         "Analyze Amazon stock.",
#         "Price change for AAPL last week",
#         "HPQ stock price", # HPQ not in COMMON_TICKERS, test direct symbol
#         "gibberish query" # Test ticker identification failure
#     ]

#     for q in queries:
#         result = handle_query(q)
#         print(f"Query: \"{q}\"")
#         if result.get("error"):
#             print(f"  Error: {result['error']}")
#         else:
#             print(f"  Ticker: {result['ticker_identified']}")
#             print(f"  Data: {result['data']}")
#         print("-" * 30)