import streamlit as st
import google.generativeai as genai
from google.generativeai.types import Tool
from google.generativeai.protos import FunctionDeclaration, Schema, Type, Part, FunctionResponse
from agents.identify_ticker import identify_ticker
from agents.ticker_news import get_ticker_news
from agents.ticker_price import get_ticker_price
from agents.ticker_price_change import get_ticker_price_change
from agents.ticker_analysis import analyze_ticker

# Configure Streamlit page
st.set_page_config(page_title="Stock Analysis Agent", page_icon="📈", layout="wide")

# Sidebar for API key inputs
st.sidebar.header("API Key Configuration")
alpha_vantage_key = st.sidebar.text_input("Alpha Vantage API Key:", type="password", key="alpha_vantage_key")
gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password", key="gemini_api_key")

# Store keys in session state
if alpha_vantage_key:
    st.session_state['ALPHAVANTAGE_API_KEY'] = alpha_vantage_key
if gemini_api_key:
    st.session_state['GEMINI_API_KEY'] = gemini_api_key

# Check if both keys are provided
if not (st.session_state.get('ALPHAVANTAGE_API_KEY') and st.session_state.get('GEMINI_API_KEY')):
    st.warning("Please enter both Alpha Vantage and Gemini API keys in the sidebar to proceed.")
    st.stop()

# Configure Gemini API
import os
try:
    os.environ["GOOGLE_API_KEY"] = st.session_state['GEMINI_API_KEY']
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}. Please verify your Gemini API key.")
    st.stop()

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

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.0-flash', tools=tools)

# Streamlit UI
st.title("Stock Analysis Agent")
st.header("Query Options")
query_type = st.radio("Choose query type:", ("Natural Language", "Structured Input"))

def extract_value(val, default, typ):
    try:
        if hasattr(val, 'value'):
            return typ(val.value)
        return typ(val)
    except Exception:
        return default

if query_type == "Natural Language":
    query = st.text_input("Enter your stock query:", key="nl_query")
    if st.button("Submit", key="nl_submit"):
        if query:
            with st.spinner("Processing..."):
                try:
                    chat_session = model.start_chat()
                    response = chat_session.send_message(query)
                    response_text = ""
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            function_call = part.function_call
                            function_name = function_call.name
                            function_args = {key: value for key, value in function_call.args.items()}
                            # Remap parameter names
                            if function_name in ['get_ticker_news', 'get_ticker_price', 'get_ticker_price_change', 'analyze_ticker']:
                                if 'symbol' in function_args:
                                    function_args['ticker_symbol'] = function_args.pop('symbol')
                            st.write(f"DEBUG: Function call: {function_name} with args: {function_args}")
                            tool_response = None
                            # Pass API key and extract values robustly
                            if function_name == 'get_ticker_price_change':
                                function_args['timeframe'] = extract_value(function_args.get('timeframe', 'today'), 'today', str)
                            if function_name == 'analyze_ticker':
                                function_args['timeframe_for_change'] = extract_value(function_args.get('timeframe_for_change', 'last 7 days'), 'last 7 days', str)
                                function_args['news_limit'] = extract_value(function_args.get('news_limit', 3), 3, int)
                            st.write(f"DEBUG: Function call: {function_name} with args: {function_args}")
                            tool_response = None
                            # Pass API key where needed
                            if function_name == 'identify_ticker':
                                tool_response = identify_ticker(function_args['company_name'], st.session_state['ALPHAVANTAGE_API_KEY'])
                            elif function_name == 'get_ticker_news':
                                tool_response = get_ticker_news(function_args['ticker_symbol'], st.session_state['ALPHAVANTAGE_API_KEY'], function_args['limit'])
                            elif function_name == 'get_ticker_price':
                                tool_response = get_ticker_price(function_args['ticker_symbol'], st.session_state['ALPHAVANTAGE_API_KEY'])
                            elif function_name == 'get_ticker_price_change':
                                tool_response = get_ticker_price_change(function_args['ticker_symbol'], function_args['timeframe'], st.session_state['ALPHAVANTAGE_API_KEY'])
                            elif function_name == 'analyze_ticker':
                                tool_response = analyze_ticker(function_args['ticker_symbol'], function_args['timeframe_for_change'], function_args['news_limit'], st.session_state['ALPHAVANTAGE_API_KEY'])
                            else:
                                tool_response = {"error": f"Unknown function: {function_name}"}
                            st.write(f"DEBUG: Function '{function_name}' returned: {tool_response}")
                            response_after_tool = chat_session.send_message(
                                Part(
                                    function_response=FunctionResponse(
                                        name=function_name,
                                        response=tool_response
                                    )
                                )
                            )
                            response_text = response_after_tool.text
                        else:
                            response_text = part.text
                    st.write("**Response:**")
                    st.markdown(response_text)
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
            with st.spinner("Analyzing..."):
                try:
                    ticker = identify_ticker(company_name, st.session_state['ALPHAVANTAGE_API_KEY'])
                    if ticker:
                        tool_response = analyze_ticker(ticker_symbol=ticker, timeframe_for_change=timeframe, news_limit=news_limit, ALPHAVANTAGE_API_KEY=st.session_state['ALPHAVANTAGE_API_KEY'])
                        st.write("**Response:**")
                        if isinstance(tool_response, dict):
                            st.markdown(f"**Ticker**: {tool_response.get('ticker', ticker)}")
                            price_analysis = tool_response.get('price_analysis')
                            if isinstance(price_analysis, dict):
                                st.markdown(f"**Price Change** ({price_analysis.get('timeframe_requested', timeframe)} from {price_analysis.get('start_date_used', '')} to {price_analysis.get('end_date_used', '')}): {price_analysis.get('percent_change', 'N/A')}%")
                            else:
                                st.markdown(f"**Price Analysis**: {price_analysis}")
                            st.markdown("**Recent News**:")
                            news_summary = tool_response.get('recent_news_summary')
                            if isinstance(news_summary, list):
                                for news_item in news_summary:
                                    st.markdown(f"- ({news_item.get('time_published', '')}) {news_item.get('title', '')} (Sentiment: {news_item.get('overall_sentiment_label', '')})")
                            else:
                                st.markdown(news_summary)
                            st.markdown("**Combined Notes**:")
                            for note in tool_response.get('combined_notes', []):
                                st.markdown(f"- {note}")
                        else:
                            st.error(tool_response)
                    else:
                        st.error(f"Could not find ticker for {company_name}.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a company name.")

st.markdown("""
    <div style='margin-top: 2em;' class="footer">
        © 2025 Stock Multi Agent System | Powered by Aditya Arya
    </div>
""", unsafe_allow_html=True)