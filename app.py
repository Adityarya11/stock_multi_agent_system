import streamlit as st
import google.generativeai as genai
from google.generativeai.types import Tool
from google.generativeai.protos import FunctionDeclaration, Schema, Type
from agents.identify_ticker import identify_ticker
from agents.ticker_news import get_ticker_news
from agents.ticker_price import get_ticker_price
from agents.ticker_price_change import get_ticker_price_change
from agents.ticker_analysis import analyze_ticker
from config.settings import GEMINI_API_KEY

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# Define Tools (same as main.py)
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

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.0-flash', tools=tools)

# Streamlit UI
st.title("Stock Analysis Agent")
st.header("Query Options")
query_type = st.radio("Choose query type:", ("Natural Language", "Structured Input"))

if query_type == "Natural Language":
    query = st.text_input("Enter your stock query:", key="nl_query")
    if st.button("Submit", key="nl_submit"):
        if query:
            try:
                chat_session = model.start_chat()
                response = chat_session.send_message(query)
                response_text = ""
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = {key: value for key, value in function_call.args.items()}
                        if function_name in ['get_ticker_news', 'get_ticker_price', 'get_ticker_price_change', 'analyze_ticker']:
                            if 'symbol' in function_args:
                                function_args['ticker_symbol'] = function_args.pop('symbol')
                        st.write(f"DEBUG: Function call: {function_name} with args: {function_args}")
                        tool_response = None
                        if function_name == 'identify_ticker':
                            tool_response = identify_ticker(**function_args)
                        elif function_name == 'get_ticker_news':
                            tool_response = get_ticker_news(**function_args)
                        elif function_name == 'get_ticker_price':
                            tool_response = get_ticker_price(**function_args)
                        elif function_name == 'get_ticker_price_change':
                            tool_response = get_ticker_price_change(**function_args)
                        elif function_name == 'analyze_ticker':
                            tool_response = analyze_ticker(**function_args)
                        else:
                            tool_response = {"error": f"Unknown function: {function_name}"}
                        st.write(f"DEBUG: Function '{function_name}' returned: {tool_response}")
                        response_after_tool = chat_session.send_message(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response=tool_response
                                )
                            )
                        )
                        response_text = response_after_tool.text
                    else:
                        response_text = part.text
                st.write("**Response:**")
                st.write(response_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a query.")
else:
    company_name = st.text_input("Company Name (e.g., Tesla):", key="company_name")
    timeframe = st.selectbox("Timeframe:", ["today", "last 7 days", "last month"], key="timeframe")
    news_limit = st.number_input("Number of News Articles:", min_value=1, max_value=10, value=3, key="news_limit")
    if st.button("Submit", key="structured_submit"):
        if company_name:
            try:
                ticker = identify_ticker(company_name)
                if ticker:
                    tool_response = analyze_ticker(ticker_symbol=ticker, timeframe_for_change=timeframe, news_limit=news_limit)
                    st.write("**Response:**")
                    if isinstance(tool_response, dict):
                        st.write(f"**Ticker**: {tool_response['ticker']}")
                        if isinstance(tool_response['price_analysis'], dict):
                            st.write(f"**Price Change** ({tool_response['price_analysis'].get('timeframe_requested')} from {tool_response['price_analysis'].get('start_date_used')} to {tool_response['price_analysis'].get('end_date_used')}): {tool_response['price_analysis'].get('percent_change')}%")
                        else:
                            st.write(f"**Price Analysis**: {tool_response['price_analysis']}")
                        st.write("**Recent News**:")
                        if isinstance(tool_response['recent_news_summary'], list):
                            for news_item in tool_response['recent_news_summary']:
                                st.write(f"- ({news_item['time_published']}) {news_item['title']} (Sentiment: {news_item['overall_sentiment_label']})")
                        else:
                            st.write(tool_response['recent_news_summary'])
                        st.write("**Combined Notes**:")
                        for note in tool_response['combined_notes']:
                            st.write(f"- {note}")
                    else:
                        st.error(tool_response)
                else:
                    st.error(f"Could not find ticker for {company_name}.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a company name.")