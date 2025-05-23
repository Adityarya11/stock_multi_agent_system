import requests
from config.settings import ALPHAVANTAGE_API_KEY

def identify_ticker(company_name):
    """
    Identifies the stock ticker symbol for a given company name using Alpha Vantage's SYMBOL_SEARCH endpoint.
    Args:
        company_name (str): The name of the company (e.g., "Tesla", "Apple").
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
        if response.status_code == 200:
            try:
                data = response.json()
                if "bestMatches" in data and data["bestMatches"]:
                    
                    ticker = data["bestMatches"][0].get("1. symbol")
                    if ticker:
                        return ticker
                    else:
                        print(f"No ticker found for company: {company_name}")
                        return None
                elif "Information" in data:
                    print(f"API Error for {company_name} symbol search: {data['Information']}")
                    return None
                elif "Note" in data:
                    print(f"API call limit Note: {data['Note']}")
                    return None
                else:
                    print(f"No matching ticker found for {company_name}.")
                    return None
            except ValueError:
                print(f"Error: Could not decode JSON. Response: {response.text}")
                return None
        else:
            print(f"Error: API request failed. Status Code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching ticker for {company_name}: {str(e)}")
        return None


#################################    Checking the functionality   #################################
# if __name__ == "__main__":
   
#     test_companies = ["Tesla", "Apple", "Nonexistent Company"]
#     for company in test_companies:
#         ticker = identify_ticker(company)
#         print(f"Company: {company}, Ticker: {ticker}")