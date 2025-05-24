import requests
import time

def identify_ticker(company_name, ALPHAVANTAGE_API_KEY):
    """
    Identifies the stock ticker symbol for a given company name using Alpha Vantage's SYMBOL_SEARCH endpoint.
    Args:
        company_name (str): The name of the company (e.g., "Tesla", "Apple").
        ALPHAVANTAGE_API_KEY (str): Alpha Vantage API key.
    Returns:
        str: The ticker symbol (e.g., "TSLA") or None if not found or an error occurs.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": ALPHAVANTAGE_API_KEY,
        "datatype": "json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "bestMatches" in data and data["bestMatches"]:
            for match in data["bestMatches"]:
                ticker = match.get("1. symbol")
                if ticker and "US" in match.get("4. region", ""):
                    return ticker
            return data["bestMatches"][0].get("1. symbol")
        elif "Information" in data or "Note" in data:
            error_msg = data.get("Information", data.get("Note", "API limit reached or invalid key"))
            print(f"API Error for {company_name}: {error_msg}")
            if "call frequency" in error_msg.lower() or "limit" in error_msg.lower():
                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return identify_ticker(company_name, ALPHAVANTAGE_API_KEY)  # Retry
            return None
        else:
            print(f"No matching ticker found for {company_name}. Response: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching ticker for {company_name}: {e}")
        return None
    except ValueError as e:
        print(f"JSON decode error for {company_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {company_name}: {e}")
        return None