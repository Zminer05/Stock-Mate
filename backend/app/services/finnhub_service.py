import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")


def get_stock_quote(ticker: str):
    url = (
        f"https://finnhub.io/api/v1/quote"
        f"?symbol={ticker}"
        f"&token={API_KEY}"
    )

    response = requests.get(url)

    return response.json()