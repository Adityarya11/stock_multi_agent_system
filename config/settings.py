import os
from dotenv import load_dotenv

load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"