import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- PAGE SETUP
st.set_page_config(page_title="Marcus.AI", layout="wide")

st.title("🤖 Marcus.AI Trading Dashboard")

# --- STOCK LIST
stocks = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"]

selected_stock = st.sidebar.selectbox("Choose a stock", stocks)

# --- DOWNLOAD DATA
data = yf.download(selected_stock, period="2y", interval="1d")

# --- SAFETY CHECK
if data is None or data.empty:
    st.error("❌ Failed to load stock data. Try another stock.")
    st.stop()

# --- CLEAN DATA (THIS FIXES EVERYTHING)
data = data.copy()
data = data.dropna()

# --- ENSURE NUMBERS
for col in ["Open", "High", "Low", "Close"]:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data = data.dropna()

# --- INDICATORS
data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

# --- CHART
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
)])

st.subheader(f"{selected_stock} Price Chart")
st.plotly_chart(fig, use_container_width=True)

# --- MAKE SURE WE HAVE ENOUGH DATA
if len(data) < 200:
    st.warning("Not enough data for full analysis yet.")
    st.stop()

# --- SAFE VALUE EXTRACTION
ma50 = data["MA50"].iloc[-1]
ma200 = data["MA200"].iloc[-1]

# --- SIGNAL LOGIC (FULLY SAFE)
signal = "HOLD"
confidence = 50

if pd.notna(ma50) and pd.notna(ma200):
    if float(ma50) > float(ma200):
        signal = "BUY"
        confidence = 75
    elif float(ma50) < float(ma200):
        signal = "SELL"
        confidence = 70

# --- DISPLAY
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
