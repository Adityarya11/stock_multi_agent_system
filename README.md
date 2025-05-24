# Stock Analysis Multi-Agent System

## Overview

This project is a multi-agent system for stock analysis, built using the Google AI SDK (assumed to be Google ADK) and the Alpha Vantage API. It processes stock-related queries through five modular sub-agents, supporting both natural language and structured inputs. The system provides insights into stock price movements, recent news, and analysis, fulfilling the requirements of the intern task for an AI Software Engineer role.

The web-based demo (`app.py`) uses Streamlit, meeting the Google ADK Web requirement. A command-line interface (`llm_orchestrator.py`) is also provided for testing. The system handles queries like "Why did Tesla stock drop today?" and "What's happening with Palantir stock recently?" Users input their Alpha Vantage and Gemini API keys via the web interface or command-line prompts, ensuring flexibility and security.

## Features

- **Modular Sub-Agents**: Five independent agents for ticker identification, news retrieval, price fetching, price change calculation, and movement analysis.
- **Natural Language Processing**: Processes queries using Google's Gemini AI model for dynamic agent orchestration.
- **Structured Inputs**: Web interface supports direct input of company names, timeframes, and news limits.
- **Dynamic API Key Input**: Users provide Alpha Vantage and Gemini API keys through the Streamlit sidebar or command-line prompts.
- **Alpha Vantage Integration**: Real-time stock data and news via API calls.
- **Web Demo**: Streamlit-based interface for user-friendly query submission and response display.
- **Error Handling**: Manages API rate limits (with retries), invalid tickers, and key validation.

## Project Structure

```
stock_multi_agent_system/
├── agents/
│   ├── identify_ticker.py        # Resolves company names to ticker symbols
│   ├── ticker_news.py            # Fetches recent stock news
│   ├── ticker_price.py           # Retrieves current stock prices
│   ├── ticker_price_change.py    # Calculates price changes over timeframes
│   ├── ticker_analysis.py        # Analyzes price movements with news context
├── app.py                        # Streamlit web interface
├── llm_orchestrator.py           # Command-line interface with AI and NLP
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── Images/
│   ├── 1.png                     # CLI response screenshot
│   ├── 2.png                     # Web UI response screenshot
├── demo.mp4                      # Video demo (<5 minutes)
```

## Setup Instructions

**Note**: API keys used in this project will be revoked after May 25, 2025. Ensure you obtain your own keys for testing.

### Prerequisites

- Python 3.9 or higher
- Git
- API keys for:
  - Alpha Vantage (free tier, obtain at https://www.alphavantage.co/support/#api-key)
  - Google Cloud (Gemini API key, obtain from Google Cloud Console)

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Adityarya11/stock_multi_agent_system.git
   cd stock_multi_agent_system
   ```

2. **Create a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` includes:

   ```
   google-generativeai
   streamlit
   requests
   ```

### Running the Application

1. **Web Interface (Google ADK Web Demo)**:

   ```bash
   streamlit run app.py
   ```

   - Open `http://localhost:8501` in a browser.
   - In the sidebar, enter your Alpha Vantage and Gemini API keys.
   - Choose "Natural Language" for queries like "What's happening with Palantir stock recently?" or "Structured Input" to specify company name, timeframe, and news limit.
   - Responses include price changes, news, and analysis with debug logs for transparency.

2. **Command-Line Interface**:

   ```bash
   python llm_orchestrator.py
   ```

   - Enter your Alpha Vantage and Gemini API keys when prompted.
   - Input stock queries (e.g., "Why did Tesla stock drop today?") or type `exit` to quit.
   - Debug logs show function calls and responses.

3. **Optional Deployed Demo** (if hosted):

   - Deploy to Streamlit Cloud by linking your GitHub repo and setting `app.py` as the main file.
   - Access at `https://your-app-name.streamlit.app` (update with your URL).
   - Enter API keys in the sidebar.

## Sample Queries and Expected Outputs

Below are example queries from the task with expected outputs (actual data depends on Alpha Vantage API responses; replace with real outputs after testing):

1. **Query**: "Why did Tesla stock drop today?"

   - **Expected Output**:

     ```
     Tesla's stock (TSLA) dropped by 2.5% today (from $250.00 to $243.75, a change of -$6.25). Recent news includes: "Tesla Q2 earnings miss expectations"; "New EV regulations announced". The price drop might be related to the disappointing earnings report.
     ```

2. **Query**: "What's happening with Palantir stock recently?"

   - **Expected Output**:

     ```
     Palantir (PLTR) stock increased by 5% over the last 7 days (from $120.00 to $126.00). Recent news includes: "Palantir wins new DoD contract"; "Partnership with Divergent Technologies". The price rise may be driven by positive contract news.
     ```

3. **Query**: "HPQ stock price"

   - **Expected Output**:

     ```
     The current price of HPQ is $28.50. It is down $0.11 from its previous close of $28.61, representing a change of -0.38%.
     ```

**Structured Input Example** (via web interface):

- **Input**: Company Name = "Apple", Timeframe = "last month", News Limit = 3

- **Expected Output**:

  ```
  Ticker: AAPL
  Price Change (last month from 2025-04-23 to 2025-05-23): +4.5%
  Recent News:
  - (2025-05-20) Apple announces new iPhone features (Sentiment: Positive)
  - (2025-05-18) Apple faces supply chain delays (Sentiment: Negative)
  - (2025-05-15) Apple stock upgraded by analysts (Sentiment: Positive)
  Combined Notes:
  - Over the last month, AAPL stock price has increased by 4.5% (changed by $8.50).
  - The price increase might be related to positive analyst upgrades and new product announcements.
  ```

## Architecture

The system is designed with modularity and extensibility:

- **Sub-Agents**:
  - `identify_ticker`: Maps company names to ticker symbols (e.g., "Palantir" → "PLTR") using Alpha Vantage’s `SYMBOL_SEARCH`.
  - `ticker_news`: Fetches news via `NEWS_SENTIMENT` endpoint.
  - `ticker_price`: Retrieves current prices using `GLOBAL_QUOTE`.
  - `ticker_price_change`: Calculates price changes with `TIME_SERIES_DAILY_ADJUSTED` or `GLOBAL_QUOTE` (for "today").
  - `ticker_analysis`: Combines price and news data, correlating significant changes (>5%) with news events.
- **Orchestration**:
  - The Google AI SDK (`google.generativeai`) uses the Gemini model to parse queries and trigger sub-agents via function calls.
  - `app.py` provides a Streamlit web interface with natural language and structured input modes.
  - `llm_orchestrator.py` offers a command-line interface for testing.
- **API Key Management**:
  - Users input API keys via the Streamlit sidebar or command-line prompts, stored in session state or variables.
- **Error Handling**:
  - Handles API rate limits (retries after 60 seconds), invalid tickers, and key validation.

## Images

- Reference screenshots:
  - ![CLI response](Images/1.png)
  - ![Web UI response](Images/2.png)

## Web Demo

The web demo, implemented in `app.py` using Streamlit, fulfills the Google ADK Web requirement:

- **Natural Language Input**: Users enter queries like "Why did Tesla stock drop today?".
- **Structured Input**: Users specify company name, timeframe (e.g., "today", "last 7 days"), and news limit (1-10).
- **API Key Input**: Sidebar fields for Alpha Vantage and Gemini API keys.
- **Deployment**: Run locally at `http://localhost:8501` or deploy to Streamlit Cloud.
- **Debugging**: Displays function call logs and API responses.

## Video Demo

A video demo (`demo.mp4`) is included, showcasing:

- The Streamlit web interface handling the three example queries.
- Both natural language and structured input modes, including API key input.
- A narrated explanation of the architecture, highlighting modularity and API integration.
- Duration: <5 minutes.

**Recording Instructions**:
- Use screen recording software (e.g., OBS Studio, Camtasia).
- Show:
  - Entering API keys in the Streamlit sidebar.
  - Running queries: "Why did Tesla stock drop today?", "What's happening with Palantir stock recently?", "HPQ stock price".
  - Structured input for "Apple" with "last month" timeframe.
  - Briefly explain each sub-agent’s role (e.g., `identify_ticker` resolves "Tesla" to "TSLA").
  - Display code structure (`agents/`, `app.py`).
- Keep under 5 minutes, narrate clearly, and save as `demo.mp4`.
- Commit to the repository or host on Google Drive if large.

## Notes

- **Alpha Vantage Rate Limits**: Free tier allows 5 API calls per minute and 500 per day. Sub-agents retry after 60 seconds on rate limit errors.
- **Stock Support**: Supports US and international stocks (e.g., RELIANCE.BSE).
- **Extensibility**: New sub-agents or APIs can be added by updating the `tools` list.
- **Testing**: Test with varied queries (e.g., invalid companies, different timeframes).

## Troubleshooting

- **ModuleNotFoundError**: Ensure dependencies are installed (`pip install -r requirements.txt`).
- **API Key Issues**: Verify keys are valid. Test Alpha Vantage key with:
  ```bash
  curl "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=Tesla&apikey=YOUR_KEY&datatype=json"
  ```
- **Streamlit Errors**: Check port 8501 is free or use `--server.port 8502`. Run with `--logger.level=debug`.
- **Rate Limits**: Wait 60 seconds if Alpha Vantage returns a "Note" or "Information" error.

## Contact

For questions or issues, please open a GitHub issue or contact *arya050411@gmail.com*.

---

*Developed by Aditya Arya as part of the AI Software Engineer Intern Task.*