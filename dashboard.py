import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- PAGE SETUP
st.set_page_config(page_title="Marcus.AI", layout="wide")

st.title("🤖 Marcus.AI Trading Dashboard")

# --- STOCK LIST (expand later)
stocks = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"]

selected_stock = st.sidebar.selectbox("Choose a stock", stocks)

# --- DOWNLOAD DATA (FIXED: more data)
data = yf.download(selected_stock, period="2y", interval="1d")

# --- SAFETY CHECK (FIXES EMPTY DATA ERROR)
if data.empty:
    st.error("❌ Failed to load stock data. Try another stock.")
    st.stop()

# --- CALCULATE INDICATORS
data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

# --- CANDLESTICK CHART
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
)])

st.subheader(f"{selected_stock} Price Chart")
st.plotly_chart(fig, use_container_width=True)

# --- GET LATEST ROW (SAFE NOW)
latest = data.iloc[-1]

# --- SIGNAL LOGIC (FIXED NaN ISSUE)
signal = "HOLD"
confidence = 50

if pd.notna(latest["MA50"]) and pd.notna(latest["MA200"]):
    if latest["MA50"] > latest["MA200"]:
        signal = "BUY"
        confidence = 75
    elif latest["MA50"] < latest["MA200"]:
        signal = "SELL"
        confidence = 70

# --- DISPLAY SIGNAL
st.subheader("📊 AI Signal")
st.write(f"Signal: **{signal}**")
st.write(f"Confidence: **{confidence}%**")

# --- EXPLANATION
if signal == "BUY":
    st.success("Short-term trend is above long-term trend → bullish momentum")
elif signal == "SELL":
    st.error("Short-term trend is below long-term trend → bearish momentum")
else:
    st.warning("No strong trend detected")
