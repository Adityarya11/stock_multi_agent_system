import requests
from datetime import datetime, timedelta
import time

def parse_timeframe(timeframe_str):
    today = datetime.today()
    timeframe_str = timeframe_str.lower()
    
    if "today" in timeframe_str:
        start_date = today - timedelta(days=1)
        end_date = today
    elif "last week" in timeframe_str:
        start_of_this_week = today - timedelta(days=today.weekday())
        end_of_last_week = start_of_this_week - timedelta(days=1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        start_date = start_of_last_week
        end_date = end_of_last_week
    elif "days" in timeframe_str:
        try:
            days = int(''.join(filter(str.isdigit, timeframe_str)))
            start_date = today - timedelta(days=days)
            end_date = today
        except ValueError:
            return None, None
    elif "last month" in timeframe_str:
        first_day_of_current_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        start_date = first_day_of_last_month
        end_date = last_day_of_last_month
    else:
        start_date = today - timedelta(days=7)
        end_date = today
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def get_ticker_price_change(ticker_symbol, timeframe="today", ALPHAVANTAGE_API_KEY=None):
    """
    Calculates how the stock's price has changed in a given timeframe using Alpha Vantage API.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., "TSLA").
        timeframe (str): The timeframe (e.g., "today", "last 7 days"). Defaults to "today".
        ALPHAVANTAGE_API_KEY (str): Alpha Vantage API key.
    Returns:
        dict or str: Price change information or error message.
    """
    if not ALPHAVANTAGE_API_KEY:
        return "Alpha Vantage API key is required."

    url = "https://www.alphavantage.co/query"
    start_date_str, end_date_str = parse_timeframe(timeframe)
    if not start_date_str:
        return f"Invalid timeframe provided: {timeframe}"

    if timeframe.lower() == "today":
        params_quote = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker_symbol,
            "apikey": ALPHAVANTAGE_API_KEY,
            "datatype": "json"
        }
        try:
            response = requests.get(url, params=params_quote)
            response.raise_for_status()
            quote_data = response.json()
            if "Global Quote" in quote_data and quote_data["Global Quote"]:
                current_price = float(quote_data["Global Quote"].get("05. price", 0))
                prev_close_price = float(quote_data["Global Quote"].get("08. previous close", 0))
                if current_price and prev_close_price:
                    change = current_price - prev_close_price
                    percent_change = (change / prev_close_price) * 100 if prev_close_price else 0
                    return {
                        "ticker": ticker_symbol,
                        "timeframe": "today (vs previous close)",
                        "start_price (previous_close)": prev_close_price,
                        "end_price (current)": current_price,
                        "price_change": round(change, 2),
                        "percent_change": round(percent_change, 2)
                    }
                else:
                    return f"Could not get current or previous close price for {ticker_symbol} for 'today' calculation."
            elif "Information" in quote_data or "Note" in quote_data:
                error = quote_data.get("Information", quote_data.get("Note", "API limit reached or invalid key"))
                print(f"API Error for {ticker_symbol} quote: {error}")
                if "call frequency" in error.lower() or "limit" in error.lower():
                    print("Rate limit reached. Waiting 60 seconds...")
                    time.sleep(60)
                    return get_ticker_price_change(ticker_symbol, timeframe, ALPHAVANTAGE_API_KEY)  # Retry
                return f"API Error for {ticker_symbol} quote: {error}"
            else:
                return f"No quote data found for {ticker_symbol}."
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching quote for {ticker_symbol}: {e}")
            return f"Error fetching quote for {ticker_symbol}: {e}"
        except ValueError as e:
            print(f"JSON decode error for {ticker_symbol}: {e}")
            return f"Error fetching quote for {ticker_symbol}: Invalid JSON response."
        except Exception as e:
            print(f"Unexpected error fetching quote for {ticker_symbol}: {e}")
            return f"Error fetching quote for {ticker_symbol}: {e}"

    params_historical = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker_symbol,
        "outputsize": "compact",
        "apikey": ALPHAVANTAGE_API_KEY,
        "datatype": "json"
    }
    try:
        response = requests.get(url, params=params_historical)
        response.raise_for_status()
        data = response.json()
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            available_dates = sorted(time_series.keys())
            
            actual_end_date = None
            for date in reversed(available_dates):
                if date <= end_date_str:
                    actual_end_date = date
                    break
            
            actual_start_date_for_price = None
            temp_start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
            current_check_date = temp_start_dt - timedelta(days=1)
            while current_check_date >= datetime.strptime(available_dates[0], '%Y-%m-%d'):
                check_date_str = current_check_date.strftime('%Y-%m-%d')
                if check_date_str in time_series:
                    actual_start_date_for_price = check_date_str
                    break
                current_check_date -= timedelta(days=1)
            
            if not actual_start_date_for_price and available_dates[0] >= start_date_str:
                actual_start_date_for_price = available_dates[0]
            elif not actual_start_date_for_price:
                return f"Could not find a suitable start date for historical data for {ticker_symbol} around {start_date_str}. Earliest data: {available_dates[0]}"
            
            if not actual_end_date:
                return f"Could not find a suitable end date for historical data for {ticker_symbol} around {end_date_str}. Latest data: {available_dates[-1]}"
            
            try:
                start_price = float(time_series[actual_start_date_for_price]["4. close"])
                end_price = float(time_series[actual_end_date]["4. close"])
            except KeyError as e:
                return f"Missing data for date {e} in series for {ticker_symbol}."
            except ValueError:
                return f"Could not convert price to float for {ticker_symbol}."
            
            price_change_val = end_price - start_price
            percent_change_val = (price_change_val / start_price) * 100 if start_price else 0
            
            return {
                "ticker": ticker_symbol,
                "timeframe_requested": timeframe,
                "start_date_used": actual_start_date_for_price,
                "end_date_used": actual_end_date,
                "start_price": start_price,
                "end_price": end_price,
                "price_change": round(price_change_val, 2),
                "percent_change": round(percent_change_val, 2)
            }
        elif "Information" in data or "Note" in data:
            error = data.get("Information", data.get("Note", "API limit reached or invalid key"))
            print(f"API Error for {ticker_symbol} historical data: {error}")
            if "call frequency" in error.lower() or "limit" in error.lower():
                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return get_ticker_price_change(ticker_symbol, timeframe, ALPHAVANTAGE_API_KEY)  # Retry
            return f"API Error for {ticker_symbol} historical data: {error}"
        else:
            return f"No historical price data found for {ticker_symbol}."
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching historical data for {ticker_symbol}: {e}")
        return f"Error fetching historical data for {ticker_symbol}: {e}"
    except ValueError as e:
        print(f"JSON decode error for {ticker_symbol}: {e}")
        return f"Error fetching historical data for {ticker_symbol}: Invalid JSON response."
    except Exception as e:
        print(f"Unexpected error fetching historical data for {ticker_symbol}: {e}")
        return f"Error fetching historical data for {ticker_symbol}: {e}"