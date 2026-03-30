import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Marcus.AI", layout="wide")

# -------------------- STATE --------------------
if "balance" not in st.session_state:
    st.session_state.balance = 10000

if "positions" not in st.session_state:
    st.session_state.positions = []

if "journal" not in st.session_state:
    st.session_state.journal = []

# -------------------- UI --------------------
st.title("🤖 Marcus.AI")

tab1, tab2, tab3 = st.tabs(["📊 Trading", "💰 Paper Trading", "📒 Journal"])

# -------------------- STOCK LIST (150+) --------------------
stocks = [
    "AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","NFLX","AMD","INTC",
    "BABA","UBER","DIS","PYPL","SHOP","SQ","CRM","ORCL","IBM","CSCO",
    "KO","PEP","WMT","COST","NKE","MCD","SBUX","BA","GE","F",
    "GM","T","VZ","JPM","BAC","GS","MS","AXP","C","WFC",
    "SPY","QQQ","DIA","IWM","ARKK",
    "RY.TO","TD.TO","BNS.TO","ENB.TO","SU.TO","SHOP.TO"
]

# -------------------- FUNCTIONS --------------------
def get_data(stock):
    data = yf.download(stock, period="1y", interval="1d", auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    if data is None or data.empty:
        return None
    
    data = data.dropna()

    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()

    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data

def get_signal(data):
    latest = data.iloc[-1]

    ma20 = latest["MA20"]
    ma50 = latest["MA50"]
    rsi = latest["RSI"]

    score = 0

    if pd.notna(ma20) and pd.notna(ma50):
        if ma20 > ma50:
            score += 1
        else:
            score -= 1

    if pd.notna(rsi):
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1

    if score >= 2:
        return "BUY", 80
    elif score == 1:
        return "BUY", 65
    elif score == -1:
        return "SELL", 65
    elif score <= -2:
        return "SELL", 80
    else:
        return "HOLD", 50

# -------------------- TAB 1: TRADING --------------------
with tab1:
    selected_stock = st.selectbox("Choose Stock", stocks)
    refresh = st.slider("Auto Refresh (sec)", 10, 120, 30)

    data = get_data(selected_stock)

    if data is None:
        st.error("Failed to load data")
    else:
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        ))

        fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20"))
        fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50"))

        st.plotly_chart(fig, use_container_width=True)

        signal, confidence = get_signal(data)

        st.subheader("📊 Signal")
        st.write(f"**{signal}**")
        st.write(f"Confidence: **{confidence}%**")

        latest = data.iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("RSI", round(latest["RSI"], 2))
        col2.metric("Price", round(latest["Close"], 2))
        col3.metric("Trend", "Bullish" if signal == "BUY" else "Bearish" if signal == "SELL" else "Neutral")

    time.sleep(refresh)
    st.rerun()

# -------------------- TAB 2: PAPER TRADING --------------------
with tab2:
    st.subheader("💰 Paper Trading")

    st.write(f"Balance: ${st.session_state.balance}")

    selected_stock = st.selectbox("Trade Stock", stocks, key="trade_stock")
    amount = st.number_input("Amount ($)", min_value=1)

    data = get_data(selected_stock)

    if data is not None:
        price = data["Close"].iloc[-1]

        if st.button("BUY"):
            shares = amount / price
            st.session_state.positions.append((selected_stock, shares, price))
            st.session_state.balance -= amount

            st.session_state.journal.append(f"BUY {selected_stock} at {price}")

        if st.button("SELL"):
            for pos in st.session_state.positions:
                if pos[0] == selected_stock:
                    value = pos[1] * price
                    st.session_state.balance += value
                    st.session_state.positions.remove(pos)

                    st.session_state.journal.append(f"SELL {selected_stock} at {price}")
                    break

    st.write("Positions:")
    for pos in st.session_state.positions:
        st.write(pos)

# -------------------- TAB 3: JOURNAL --------------------
with tab3:
    st.subheader("📒 Trading Journal")

    for entry in st.session_state.journal:
        st.write(entry)
