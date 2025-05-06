import streamlit as st
import requests
from textblob import TextBlob
import yfinance as yf

# --- CONFIG ---
NEWS_API_KEY = st.secrets["news_api_key"]
STOCK_TICKERS = {
    'XLE': 'Energy',
    'XLK': 'Technology',
    'XLF': 'Financials',
    'XLV': 'Healthcare',
}
POLITICAL_KEYWORDS = ['election', 'congress', 'president', 'policy', 'inflation']

# --- FUNCTIONS ---

def fetch_political_headlines():
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    headlines = [article['title'] for article in data['articles']]
    return [h for h in headlines if any(k in h.lower() for k in POLITICAL_KEYWORDS)]

def analyze_sentiment(headlines):
    polarity = [TextBlob(h).sentiment.polarity for h in headlines]
    avg_sentiment = sum(polarity) / len(polarity) if polarity else 0
    return avg_sentiment

def fetch_stock_prices(tickers):
    prices = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        prices[ticker] = hist['Close'].iloc[-1] if not hist.empty else None
    return prices

def make_trade_suggestions(sentiment, prices):
    direction = "BUY" if sentiment > 0.1 else "SELL" if sentiment < -0.1 else "HOLD"
    suggestions = []
    for ticker, sector in STOCK_TICKERS.items():
        price = prices.get(ticker)
        if price:
            suggestions.append(f"{direction} {ticker} ({sector}) at ${price:.2f}")
    return suggestions

# --- STREAMLIT UI ---

st.set_page_config(page_title="TradeBot", layout="centered")
st.title("TradeBot: Political Sentiment-Based Stock Advisor")

if st.button("Get Trade Suggestions"):
    with st.spinner("Analyzing news and stock data..."):
        headlines = fetch_political_headlines()
        sentiment = analyze_sentiment(headlines)
        prices = fetch_stock_prices(STOCK_TICKERS.keys())
        suggestions = make_trade_suggestions(sentiment, prices)

        st.subheader("Political Sentiment Score")
        st.write(f"{sentiment:.2f}")

        st.subheader("Top Headlines")
        for h in headlines[:5]:
            st.write("- " + h)

        st.subheader("Trade Suggestions")
        for s in suggestions:
            st.write("• " + s)
