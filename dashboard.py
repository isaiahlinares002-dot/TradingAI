import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Marcus.AI", layout="wide")

st.title("🤖 Marcus.AI Trading Dashboard")

# --- STOCK LIST (you can expand later to 150)
stocks = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"]

selected_stock = st.sidebar.selectbox("Choose a stock", stocks)

# --- DOWNLOAD DATA
data = yf.download(selected_stock, period="6mo", interval="1d")

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

# --- SIMPLE SIGNAL LOGIC
data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

latest = data.iloc[-1]

signal = "HOLD"
confidence = 50

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

# --- AUTO REFRESH
st.caption("🔄 Auto refresh every 60 seconds")
