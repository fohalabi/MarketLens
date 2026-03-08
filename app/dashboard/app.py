import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# CONFIG 

API_BASE = "https://marketlens-production-96d7.up.railway.app/"  # inside Docker network
API_BASE = "http://host.docker.internal:8000/api"  # use this for local testing

st.set_page_config(
    page_title="MarketLens",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# HELPERS

def fetch(endpoint: str) -> dict:
    """Make a GET request to the FastAPI backend."""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"API error: {str(e)}")
        return {}


def color_metric(value: float) -> str:
    """Return green for positive, red for negative."""
    return "normal" if value >= 0 else "inverse"


# SIDEBAR 

st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("MarketLens")
st.sidebar.caption("Real-time market intelligence")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["📊 Market Overview", "📈 Stock Analyzer", "💼 Portfolio", "🔔 Alerts"]
)

st.sidebar.divider()
st.sidebar.caption("Built with FastAPI + Python")


# PAGE 1: MARKET OVERVIEW 

if page == "📊 Market Overview":
    st.title("📊 Market Overview")
    st.caption("Live snapshot of major market assets")
    st.divider()

    # Quick stock snapshots
    st.subheader("Major Stocks")
    symbols = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
    cols = st.columns(len(symbols))

    for i, symbol in enumerate(symbols):
        with cols[i]:
            with st.spinner(f"Loading {symbol}..."):
                data = fetch(f"/stocks/{symbol}")
                if data:
                    price = data.get("current_price", 0)
                    prev = data.get("previous_close", 0)
                    change = round(price - prev, 2) if price and prev else 0
                    change_pct = round((change / prev) * 100, 2) if prev else 0
                    st.metric(
                        label=symbol,
                        value=f"${price:,.2f}" if price else "N/A",
                        delta=f"{change_pct}%"
                    )


    st.divider()

    # Market signals
    st.subheader("Technical Signals")
    signal_cols = st.columns(len(symbols))

    for i, symbol in enumerate(symbols):
        with signal_cols[i]:
            data = fetch(f"/stocks/{symbol}?period=3mo")
            if data and "analysis" in data:
                signal = data["analysis"]["signal"]["overall_signal"]
                rsi = data["analysis"]["indicators"].get("rsi", 0)
                color = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                st.markdown(f"**{symbol}**")
                st.markdown(f"{color} {signal}")
                st.caption(f"RSI: {rsi}")


# PAGE 2: STOCK ANALYZER 

elif page == "📈 Stock Analyzer":
    st.title("📈 Stock Analyzer")
    st.caption("Deep dive into any stock with technical analysis")
    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1)
    with col3:
        interval = st.selectbox("Interval", ["1d", "1wk"], index=0)

    # Auto load on symbol change
    # No button needed — loads automatically like useEffect in React
    with st.spinner(f"Analyzing {symbol}..."):

        # Fetch stock data + analysis
        data = fetch(f"/stocks/{symbol}?period={period}")

        # Try stored history first, fall back to live fetch
        history = fetch(f"/stocks/{symbol}/history/stored?interval={interval}")
        if not history or not history.get("data"):
            history = fetch(f"/stocks/{symbol}/history?period={period}&interval={interval}")

        if data and history:
            # ── Key Metrics ──
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                price = data.get("current_price", 0)
                prev = data.get("previous_close", 0)
                change_pct = round(((price - prev) / prev) * 100, 2) if prev else 0
                st.metric("Current Price", f"${price:,.2f}", delta=f"{change_pct}%")
            with col2:
                market_cap = data.get("market_cap", 0)
                st.metric("Market Cap", f"${market_cap/1e9:.2f}B" if market_cap else "N/A")
            with col3:
                st.metric("P/E Ratio", f"{data.get('pe_ratio', 'N/A')}")
            with col4:
                if "analysis" in data:
                    signal = data["analysis"]["signal"]["overall_signal"]
                    color = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                    st.metric("Signal", f"{color} {signal}")

            st.divider()

            # ── Candlestick Chart — auto loads ──
            st.subheader(f"{symbol} Price Chart")
            df = pd.DataFrame(history.get("data", []))

            if not df.empty:
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.7, 0.3]
                )

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df["date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price"
                ), row=1, col=1)

                # SMA 20 overlay
                if "analysis" in data:
                    sma_20 = data["analysis"]["indicators"].get("sma_20")
                    if sma_20:
                        fig.add_hline(
                            y=sma_20,
                            line_dash="dash",
                            line_color="orange",
                            annotation_text="SMA 20",
                            row=1, col=1
                        )

                # Volume bars
                fig.add_trace(go.Bar(
                    x=df["date"],
                    y=df["volume"],
                    name="Volume",
                    marker_color="rgba(100, 149, 237, 0.5)"
                ), row=2, col=1)

                fig.update_layout(
                    height=500,
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # ── Indicators ──
            if "analysis" in data:
                indicators = data["analysis"]["indicators"]

                st.subheader("Technical Indicators")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    rsi = indicators.get("rsi", 0)
                    rsi_signal = indicators.get("rsi_signal", "neutral")
                    rsi_color = "🟢" if rsi_signal == "oversold" else "🔴" if rsi_signal == "overbought" else "🟡"
                    st.metric("RSI (14)", f"{rsi} {rsi_color}")
                    st.caption(rsi_signal)
                with col2:
                    st.metric("SMA 20", indicators.get("sma_20", "N/A"))
                with col3:
                    st.metric("EMA 20", indicators.get("ema_20", "N/A"))
                with col4:
                    st.metric("ATR", indicators.get("atr", "N/A"))

                # ── Bollinger Bands ──
                st.subheader("Bollinger Bands")
                bb = indicators.get("bollinger_bands", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Upper Band", bb.get("upper", "N/A"))
                with col2:
                    st.metric("Middle Band", bb.get("middle", "N/A"))
                with col3:
                    st.metric("Lower Band", bb.get("lower", "N/A"))

                # ── MACD ──
                st.subheader("MACD")
                macd = indicators.get("macd", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("MACD Line", macd.get("macd_line", "N/A"))
                with col2:
                    st.metric("Signal Line", macd.get("signal_line", "N/A"))
                with col3:
                    histogram = macd.get("histogram", 0)
                    st.metric(
                        "Histogram",
                        histogram,
                        delta="Bullish" if histogram and histogram > 0 else "Bearish"
                    )

                st.divider()

                # ── Signal Breakdown ──
                st.subheader("Signal Breakdown")
                signals = data["analysis"]["signal"]["signals"]
                score = data["analysis"]["signal"]["score"]
                overall = data["analysis"]["signal"]["overall_signal"]

                color = "green" if overall == "BUY" else "red" if overall == "SELL" else "orange"
                st.markdown(f"### :{color}[{overall}] (Score: {score})")
                for s in signals:
                    st.markdown(f"• {s}")
        else:
            st.warning(f"Could not load data for {symbol}. Check the symbol and try again.")

# PAGE 3: PORTFOLIO 

elif page == "💼 Portfolio":
    st.title("💼 Portfolio")
    st.caption("Track your holdings and P&L")
    st.divider()

    # ── Add holding form ──
    with st.expander("➕ Add New Holding"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            p_symbol = st.text_input("Symbol", value="AAPL").upper()
        with col2:
            p_type = st.selectbox("Asset Type", ["stock", "crypto", "forex", "commodity"])
        with col3:
            p_qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=0.1)
        with col4:
            p_price = st.number_input("Buy Price ($)", min_value=0.0, value=100.0, step=0.01)

        if st.button("Add to Portfolio", type="primary"):
            try:
                response = requests.post(
                    f"{API_BASE}/portfolio/",
                    json={
                        "symbol": p_symbol,
                        "asset_type": p_type,
                        "quantity": p_qty,
                        "buy_price": p_price
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    st.success(f"✅ {p_symbol} added to portfolio!")
                    st.rerun()
                else:
                    st.error("Failed to add holding")
            except Exception as e:
                st.error(str(e))

    # ── Portfolio data ──
    portfolio = fetch("/portfolio/")

    if portfolio and portfolio.get("holdings"):
        summary = portfolio["summary"]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Invested", f"${summary['total_invested']:,.2f}")
        with col2:
            st.metric("Current Value", f"${summary['total_current_value']:,.2f}")
        with col3:
            st.metric(
                "Total P&L",
                f"${summary['total_profit_loss']:,.2f}",
                delta=f"{summary['total_return_percent']}%"
            )
        with col4:
            st.metric("Holdings", summary["number_of_holdings"])

        st.divider()

        # Holdings table
        st.subheader("Your Holdings")
        holdings_df = pd.DataFrame(portfolio["holdings"])
        holdings_df = holdings_df[[
            "symbol", "asset_type", "quantity",
            "buy_price", "current_price",
            "profit_loss", "return_percent"
        ]]
        holdings_df.columns = [
            "Symbol", "Type", "Quantity",
            "Buy Price", "Current Price",
            "P&L", "Return %"
        ]
        st.dataframe(holdings_df, use_container_width=True)

        # Allocation pie chart
        st.subheader("Portfolio Allocation")
        fig = go.Figure(go.Pie(
            labels=holdings_df["Symbol"],
            values=[h["current_value"] for h in portfolio["holdings"]],
            hole=0.4
        ))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No holdings yet — add your first asset above!")


# PAGE 4: ALERTS 

elif page == "🔔 Alerts":
    st.title("🔔 Price Alerts")
    st.caption("Get notified when assets hit your target price")
    st.divider()

    # Create alert form 
    with st.expander("➕ Create New Alert"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            a_symbol = st.text_input("Symbol", value="AAPL").upper()
        with col2:
            a_type = st.selectbox("Asset Type", ["stock", "crypto", "forex", "commodity"])
        with col3:
            a_condition = st.selectbox("Condition", ["above", "below"])
        with col4:
            a_price = st.number_input("Target Price ($)", min_value=0.0, value=150.0, step=0.01)

        if st.button("Create Alert", type="primary"):
            try:
                response = requests.post(
                    f"{API_BASE}/alerts/",
                    json={
                        "symbol": a_symbol,
                        "asset_type": a_type,
                        "condition": a_condition,
                        "target_price": a_price
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    st.success(f"✅ Alert created for {a_symbol}!")
                    st.rerun()
                else:
                    st.error("Failed to create alert")
            except Exception as e:
                st.error(str(e))

    # ── Alerts list ──
    alerts_data = fetch("/alerts/")

    if alerts_data and alerts_data.get("alerts"):
        st.subheader(f"Active Alerts ({alerts_data['count']})")

        for alert in alerts_data["alerts"]:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{alert['symbol']}**")
            with col2:
                st.markdown(alert["asset_type"])
            with col3:
                arrow = "⬆️" if alert["condition"] == "above" else "⬇️"
                st.markdown(f"{arrow} {alert['condition']}")
            with col4:
                st.markdown(f"${alert['target_price']:,.2f}")
            with col5:
                status = "✅ Triggered" if alert["is_triggered"] else "🟡 Active"
                st.markdown(status)
    else:
        st.info("No alerts yet — create your first alert above!")