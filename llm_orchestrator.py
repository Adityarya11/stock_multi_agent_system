import google.generativeai as genai
from google.generativeai.types import Tool
from google.generativeai.protos import FunctionDeclaration, Schema, Type
from agents.identify_ticker import identify_ticker
from agents.ticker_news import get_ticker_news
from agents.ticker_price import get_ticker_price
from agents.ticker_price_change import get_ticker_price_change
from agents.ticker_analysis import analyze_ticker

# Prompt for API keys
ALPHAVANTAGE_API_KEY = input("Enter your Alpha Vantage API Key: ")
GEMINI_API_KEY = input("Enter your Gemini API Key: ")

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"An error occurred configuring Gemini API: {e}")
    print("Please ensure your Gemini API key is valid.")
    exit()

# Define Tools
tools = [
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name='identify_ticker',
                description='Parses a company name from the user query and identifies its stock ticker symbol (e.g., "Tesla" -> "TSLA").',
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        'company_name': Schema(type=Type.STRING, description='The name of the company.')
                    },
                    required=['company_name']
                )
            ),
            FunctionDeclaration(
                name='get_ticker_news',
                description='Retrieves the most recent news about a given stock ticker symbol.',
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        'ticker_symbol': Schema(type=Type.STRING, description='The stock ticker symbol (e.g., "TSLA").'),
                        'limit': Schema(type=Type.INTEGER, description='Number of news articles to retrieve. Defaults to 5.')
                    },
                    required=['ticker_symbol']
                )
            ),
            FunctionDeclaration(
                name='get_ticker_price',
                description='Fetches the current real-time price of a stock using its ticker symbol.',
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        'ticker_symbol': Schema(type=Type.STRING, description='The stock ticker symbol (e.g., "TSLA").')
                    },
                    required=['ticker_symbol']
                )
            ),
            FunctionDeclaration(
                name='get_ticker_price_change',
                description='Calculates how the stock\'s price has changed over a specified timeframe (e.g., "today", "last 7 days").',
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        'ticker_symbol': Schema(type=Type.STRING, description='The stock ticker symbol.'),
                        'timeframe': Schema(type=Type.STRING, description='The timeframe for the price change (e.g., "today", "last 7 days"). Defaults to "today".')
                    },
                    required=['ticker_symbol']
                )
            ),
            FunctionDeclaration(
                name='analyze_ticker',
                description='Analyzes and summarizes the reasons behind recent stock price movements, considering news and price data.',
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        'ticker_symbol': Schema(type=Type.STRING, description='The stock ticker symbol.'),
                        'timeframe_for_change': Schema(type=Type.STRING, description='The timeframe for price change analysis (e.g., "last 7 days"). Defaults to "last 7 days".'),
                        'news_limit': Schema(type=Type.INTEGER, description='Number of news articles to consider. Defaults to 3.')
                    },
                    required=['ticker_symbol']
                )
            )
        ]
    )
]

# Initialize the Generative Model with Tools
model = genai.GenerativeModel('gemini-2.0-flash', tools=tools)

# Main Orchestration Loop
def run_stock_analysis_agent():
    print("Welcome to the Stock Analysis Agent! Type 'exit' to quit.")
    chat_session = model.start_chat()

    while True:
        user_query = input("\nEnter your stock query: ")
        if user_query.lower() == 'exit':
            print("Exiting Stock Analysis Agent. Goodbye!")
            break

        try:
            # Send the user query to the model
            response = chat_session.send_message(user_query)

            # Collect all function calls in the response
            function_responses = []
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = {key: value for key, value in function_call.args.items()}

                    # Map 'symbol' to 'ticker_symbol' for relevant functions
                    if function_name in ['get_ticker_news', 'get_ticker_price', 'get_ticker_price_change', 'analyze_ticker']:
                        if 'symbol' in function_args:
                            function_args['ticker_symbol'] = function_args.pop('symbol')

                    print(f"\nDEBUG: Model requested function call: {function_name} with args: {function_args}")

                    # Execute the requested function
                    tool_response = None
                    if function_name == 'identify_ticker':
                        tool_response = identify_ticker(function_args['company_name'], ALPHAVANTAGE_API_KEY)
                    elif function_name == 'get_ticker_news':
                        tool_response = get_ticker_news(function_args['ticker_symbol'], ALPHAVANTAGE_API_KEY, function_args.get('limit', 5))
                    elif function_name == 'get_ticker_price':
                        tool_response = get_ticker_price(function_args['ticker_symbol'], ALPHAVANTAGE_API_KEY)
                    elif function_name == 'get_ticker_price_change':
                        tool_response = get_ticker_price_change(function_args['ticker_symbol'], function_args.get('timeframe', 'today'), ALPHAVANTAGE_API_KEY)
                    elif function_name == 'analyze_ticker':
                        tool_response = analyze_ticker(function_args['ticker_symbol'], function_args.get('timeframe_for_change', 'last 7 days'), function_args.get('news_limit', 3), ALPHAVANTAGE_API_KEY)
                    else:
                        tool_response = {"error": f"Unknown function: {function_name}"}

                    print(f"DEBUG: Function '{function_name}' returned: {tool_response}")

                    # Handle string responses (fallback for legacy sub-agent behavior)
                    if isinstance(tool_response, str):
                        tool_response = {"error": tool_response}

                    # Append the function response
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response=tool_response
                            )
                        )
                    )

            # Send all function responses back to the model in one message
            if function_responses:
                response_after_tool = chat_session.send_message(function_responses)
                print("\nAgent Response:")
                print(response_after_tool.text)
            else:
                # Handle non-function-call responses
                print("\nAgent Response:")
                for part in response.candidates[0].content.parts:
                    if part.text:
                        print(part.text)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    run_stock_analysis_agent()