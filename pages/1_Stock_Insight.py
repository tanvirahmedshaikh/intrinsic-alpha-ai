import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
import time
import datetime
import plotly.graph_objects as go
import math
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IntrinsicAlpha AI",
    page_icon="📈",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "editing_session_id" not in st.session_state:
    st.session_state.editing_session_id = None

# Pre-populate dummy data for demonstration
if not st.session_state.sessions:
    st.session_state.sessions = {
        str(uuid.uuid4()): {"title": "Is GOOG a Growth Stock?"},
        str(uuid.uuid4()): {"title": "PEG Ratio Explained"},
        str(uuid.uuid4()): {"title": "Comparing KO and PEP"},
        str(uuid.uuid4()): {"title": "MSFT Intrinsic Value Analysis"} 
    }
    st.session_state.current_session_id = None

def new_chat_session():
    """Creates a new chat session."""
    session_id = str(uuid.uuid4())
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {"title": "New Chat"}
    st.session_state.editing_session_id = None

# --- SIDEBAR: CHAT HISTORY ---
with st.sidebar:
    st.header("IntrinsicAlpha AI")
    if st.button("New chat", use_container_width=True):
        new_chat_session()
        st.rerun()

    st.markdown("---")
    st.subheader("Recent")

    if st.session_state.sessions:
        for session_id, session_data in reversed(list(st.session_state.sessions.items())):
            is_active = (session_id == st.session_state.current_session_id)
            label = f"**▶ {session_data['title']}**" if is_active else session_data['title']

            # Create a horizontal layout with three columns
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])

            with col1:
                if st.button(label, key=f"load_{session_id}", use_container_width=True):
                    st.session_state.current_session_id = session_id
                    st.session_state.editing_session_id = None
                    st.rerun()

            with col2.container(border=False):
                if st.button("✏️", key=f"start_edit_{session_id}", use_container_width=True):
                    st.session_state.editing_session_id = session_id
                    st.rerun()

            with col3.container(border=False):
                if st.button("🗑️", key=f"delete_{session_id}", use_container_width=True):
                    del st.session_state.sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                    st.rerun()

            # Handle the rename functionality
            if st.session_state.editing_session_id == session_id:
                new_title = st.text_input("New title", value=session_data["title"], key=f"edit_{session_id}", label_visibility="collapsed")
                if new_title and new_title != session_data["title"]:
                    st.session_state.sessions[session_id]["title"] = new_title
                    st.session_state.editing_session_id = None
                    st.rerun()

    st.markdown("---")

# --- HELPER FUNCTIONS ---
def format_large_number(num):
    """
    Formats a large number with a T (trillion) or B (billion) suffix.
    """
    if num is None or not isinstance(num, (int, float)):
        return 'N/A'
    if num >= 1e12:
        return f"{num / 1e12:.2f}T"
    elif num >= 1e9:
        return f"{num / 1e9:.2f}B"
    else:
        return f"{num:,.0f}"

def get_stock_data(ticker, timeframe='1y'):
    """Fetches real historical stock data using yfinance."""
    valid_periods = {'1D': '1d', '5D': '5d', '1M': '1mo', '6M': '6mo', 'YTD': 'ytd', '1Y': '1y', '5Y': '5y', 'MAX': 'max'}
    period = valid_periods.get(timeframe, '1y')
    
    if timeframe in ('1D', '5D'):
        interval = '1m'
    else:
        interval = '1d'

    data = yf.download(ticker, period=period, interval=interval, progress=False)
    
    if data.empty:
        return pd.DataFrame()

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    
    df = pd.DataFrame(data[['Open', 'High', 'Low', 'Close', 'Volume']])
    df.index = df.index.tz_localize(None)
    
    return df

@st.cache_data
def get_key_metrics(ticker):
    """Fetches key metrics for a stock."""
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info
    
    if not info:
        return None
        
    return {
        'Previous Close': info.get('previousClose'),
        'Open': info.get('open'),
        "Day's Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
        "52 Week Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
        'Volume': info.get('volume'),
        'Avg. Volume': info.get('averageVolume'),
        'Market Cap': info.get('marketCap'),
        'Beta (5Y Monthly)': info.get('beta'),
        'PE Ratio (TTM)': info.get('trailingPE'),
        'P/B Ratio': info.get('priceToBook'),
        'Debt-to-Equity Ratio': info.get('debtToEquity'),
        'EPS (TTM)': info.get('trailingEps'),
        'Earnings Date': info.get('earningsDate'),
        'Forward Dividend & Yield': info.get('forwardYield'),
        'Ex-Dividend Date': info.get('exDividendDate'),
        'Current Dividend Yield': info.get('dividendYield'),
        'Dividend Rate': info.get('dividendRate')
    }

@st.cache_data
def get_historical_metrics(ticker):
    """Fetches and calculates mock historical metrics."""
    return {
        'Historical PE Avg (5Y)': 25.00,
        'Historical Dividend Yield Avg (5Y)': 0.52,
        'Historical ROA Avg (5Y)': 18.5,
        'Current ROA': 22.1,
        'Current Dividend Yield': 0.49
    }

@st.cache_data
def generate_valuation_data():
    """Generates mock intrinsic value and margin of safety."""
    return {
        'Intrinsic Value': 295.50,
        'Margin of Safety (%)': 15.65
    }

@st.cache_data
def generate_feature_importance_data():
    """Generates mock feature importance data."""
    data = {
        'Feature': [
            'Durable Business Moat', 'Earnings Power & Stability', 
            'Management Quality', 'Debt-to-Equity Ratio',
            'Brand & Customer Loyalty'
        ],
        'Importance': [0.40, 0.25, 0.15, 0.10, 0.10],
    }
    df = pd.DataFrame(data).sort_values('Importance', ascending=False)
    return df

# --- PAGE TITLE & INPUT ---
st.title("IntrinsicAlpha AI")
st.markdown("Your Co-Pilot for Intelligent Value Investing.")

# Stock Ticker Input
ticker = st.text_input(
    "Enter a Stock Ticker (e.g., AAPL)",
    placeholder="AAPL",
    key="stock_ticker_input",
    label_visibility="collapsed"
)

# --- MAIN CONTENT ---
if not ticker:
    st.info("Enter a stock ticker above to begin your analysis.")
else:
    with st.spinner(f"Analyzing {ticker.upper()}..."):
        stock_data = get_stock_data(ticker, '1y')
        metrics_data = get_key_metrics(ticker)
        hist_metrics = get_historical_metrics(ticker)
        
    if stock_data.empty or not metrics_data:
        st.error(f"Could not find data for ticker: {ticker.upper()}. Please try another one.")
    else:
        # --- HEADER ROW: Ticker + Timeframe ---
        col1, col2 = st.columns([0.45, 0.55])
        with col1:
            st.markdown(
                f"""
                <div style='line-height: 1; margin-bottom: -8px;'>
                    <h1 style='font-size: 3.4em; font-weight: 700; margin-bottom: 0;'>{ticker.upper()}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                """
                <div style='font-weight: 500; margin-top: 25px; margin-bottom: -8px;'>
                    Select Timeframe
                </div>
                """,
                unsafe_allow_html=True
            )
            # Compact radio buttons
            st.markdown(
                """
                <style>
                    div[data-testid="stRadio"] label {
                        padding-top: 0px !important;
                        padding-bottom: 0px !important;
                        margin-top: -35px !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            timeframe = st.radio(
                "",
                ('1D', '5D', '1M', '6M', 'YTD', '1Y', '5Y', 'MAX'),
                horizontal=True,
                key="timeframe_radio"
            )

        # --- PRICE DATA ---
        stock_data_tf = get_stock_data(ticker, timeframe)
        if not stock_data_tf.empty:
            start_price = stock_data_tf['Close'].iloc[0]
            end_price = stock_data_tf['Close'].iloc[-1]
            price_change = end_price - start_price
            percent_change = (price_change / start_price) * 100
        else:
            price_change = 0
            percent_change = 0

        color = "#00b050" if price_change >= 0 else "#ff4d4d"
        arrow = "▲" if price_change >= 0 else "▼"

        # --- PRICE BLOCK ---
        st.markdown(f"""
        <div style="margin-top: -35px; line-height: 1;">
            <span style="font-size: 2.6em; font-weight: 700;">{end_price:.2f}</span>
            <span style="font-size: 0.7em; color: gray;">USD</span>
        </div>
        <div style="color: {color}; font-size: 1.1em; font-weight: 500; margin-top: -5px;">
            {price_change:+.2f} ({percent_change:+.2f}%) <span>{arrow}</span>
        </div>
        """, unsafe_allow_html=True)

        # --- CHART ---
        fig = go.Figure(data=go.Scatter(
            x=stock_data_tf.index,
            y=stock_data_tf['Close'],
            mode='lines',
            line=dict(color=color),
            hovertemplate=(
                "<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br>" +
                "<b>Close:</b> %{y:.2f}<br>" +
                "<b>Open:</b> %{customdata[0]:.2f}<br>" +
                "<b>High:</b> %{customdata[1]:.2f}<br>" +
                "<b>Low:</b> %{customdata[2]:.2f}<br>" +
                "<b>Volume:</b> %{customdata[3]:,}<extra></extra>"
            ),
            customdata=np.stack((
                stock_data_tf['Open'], 
                stock_data_tf['High'], 
                stock_data_tf['Low'], 
                stock_data_tf['Volume']
            ), axis=-1)
        ))

        fig.update_layout(
            height=400,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title='',
            yaxis_title='Stock Price',
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- KEY METRICS TABLE ---
        st.subheader("Key Metrics")

        # Custom CSS for smaller font size in metrics
        st.markdown("""
        <style>
            /* Target the entire metric container */
            div[data-testid="stMetric"] {
                padding: 0.5rem; /* Reduce padding for a tighter layout */
            }

            /* Target the metric label (e.g., "Day's Range") */
            div[data-testid="stMetricLabel"] p {
                font-size: 0.9rem !important; /* Smaller label font */
            }

            /* Target the metric value (the number) */
            div[data-testid="stMetricValue"] {
                font-size: 1.5rem !important; /* Smaller number font to prevent truncation */
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a single list of all metrics to distribute
        all_metrics = [
            {"label": "Previous Close", "value": metrics_data.get('Previous Close'), "help": "The closing price of the stock on the previous trading day.", "format": ".2f"},
            {"label": "Open", "value": metrics_data.get('Open'), "help": "The price at which the stock began trading at the start of the current trading day.", "format": ".2f"},
            {"label": "Day's Range", "value": metrics_data.get("Day's Range"), "help": "The range between the highest and lowest prices at which a stock has traded during the current day."},
            {"label": "Volume", "value": metrics_data.get('Volume'), "help": "The total number of shares of a security that have been traded during a given period. High volume can indicate strong investor interest.", "format_func": format_large_number},
            {"label": "Market Cap", "value": metrics_data.get('Market Cap'), "help": "The total value of a company’s outstanding shares. Used to determine a company's size and compare it to others.", "format_func": format_large_number},
            {"label": "P/B Ratio", "value": metrics_data.get('P/B Ratio'), "help": "The P/B ratio compares a stock's price to the company's net asset value. For a value investor, a P/B ratio under 1 is a traditional signal of an undervalued stock. Apple's P/B of ~58 is exceptionally high, reflecting strong market confidence in its intangible assets like brand and ecosystem, rather than its book value. This is significantly above its own 5-year average of ~29 and the technology industry average of ~13. This indicates the market is placing a very high value on the company's intangible assets, like its brand and ecosystem, rather than its tangible balance sheet. This is a crucial distinction from traditional value investing.", "format": ".2f"},
            {"label": "Debt-to-Equity Ratio", "value": metrics_data.get('Debt-to-Equity Ratio'), "help": "This ratio indicates a company's financial leverage. A low ratio (under 1.5) is a sign of a financially strong company, which is crucial for stability. Apple's ratio of ~154 is high, suggesting a significant amount of debt, which should be considered when assessing risk.", "format": ".2f"},
            {"label": "P/E Ratio (TTM)", "value": metrics_data.get('PE Ratio (TTM)'), "help": "The P/E Ratio (Price-to-Earnings) is a key valuation metric. For a defensive investor, Benjamin Graham suggested a P/E of less than 15. Apple's P/E of ~38.89 is significantly above this historical benchmark, suggesting the market expects substantial future growth. For an investor focused on a significant margin of safety, this metric is a warning sign that the stock may be overvalued.", "format": ".2f"},
            {"label": "P/E vs. Historical Avg (5Y)", "value": hist_metrics.get('Historical PE Avg (5Y)'), "help": "This compares the current P/E to its 5-year historical average (~29). A P/E of ~38.89 is significantly higher, indicating the stock is valued above its own recent history and suggests strong market optimism about future growth.", "format": ".2f"},
            {"label": "EPS (TTM)", "value": metrics_data.get('EPS (TTM)'), "help": "Earnings Per Share (TTM) is the company's profit allocated to each outstanding share. Consistent EPS growth is a hallmark of a high-quality, predictable business. There is no single 'good' EPS number; it's a metric of a company's profitability. A large, stable EPS like Apple's (~$6.59) is a key factor in calculating a company's intrinsic value and is a sign of a strong business.", "format": ".2f"},
            {"label": "Avg. Volume", "value": metrics_data.get('Avg. Volume'), "help": "The average daily trading volume over a specified period. High volume can indicate strong investor interest.", "format_func": format_large_number},
            {"label": "Current ROA", "value": hist_metrics.get('Current ROA'), "help": "Return on Assets (ROA) measures how efficiently a company uses its assets to generate earnings. A good ROA depends on the industry, but generally, a number over 20% is considered excellent. Apple's ROA of ~22.1% is not only a testament to its operational efficiency but is also significantly higher than the technology industry average of ~12%, indicating a strong competitive advantage and high-quality business model. This is a key metric for a value investor assessing a company with a strong 'moat.'", "format": ".1f", "suffix": "%"},
            {"label": "Historical ROA Avg (5Y)", "value": hist_metrics.get('Historical ROA Avg (5Y)'), "help": "Historical Return on Assets shows how a company's efficiency has changed over time. Apple's current ROA (~22.1%) is higher than its historical average (~18.5%), indicating that the company's capital efficiency has improved.", "format": ".1f", "suffix": "%"},
            {"label": "Current Div Yield", "value": metrics_data.get('Current Dividend Yield'), "help": "The dividend yield shows the return on your investment from dividends alone. Apple’s current yield of ~0.41% is low compared to the S&P 500 average of around 1.5–2% and even slightly below the tech sector average of ~0.5–1%. This is typical for a growth-oriented company that reinvests its profits into innovation rather than paying large dividends.", "format": ".2f", "suffix": "%"},
            {"label": "Historical Div Yield Avg (5Y)", "value": hist_metrics.get('Historical Dividend Yield Avg (5Y)'), "help": "The average dividend yield over the last 5 years is ~0.52%. Apple’s current yield of ~0.41% is slightly below this historical average, which mainly reflects its rising stock price rather than a shift in dividend policy. For a stable payer like Apple, changes in yield usually signal price movement, not a change in fundamentals.", "format": ".2f", "suffix": "%"}
        ]

        # Create a 4-column layout for metrics and summary
        col1, col2, col3, col4 = st.columns([0.21, 0.21, 0.21, 0.37])
        
        # Distribute the metrics evenly across the first three columns
        metrics_per_col = len(all_metrics) // 3
        
        with col1:
            for m in all_metrics[0:metrics_per_col]:
                value_to_display = m.get('value')
                if 'format_func' in m:
                    value_to_display = m['format_func'](value_to_display)
                elif m.get('format') and value_to_display is not None:
                    value_to_display = f"{value_to_display:{m['format']}}"
                else:
                    value_to_display = str(value_to_display)

                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']
                
                st.metric(label=m['label'], value=value_to_display, help=m['help'])

        with col2:
            for m in all_metrics[metrics_per_col:metrics_per_col*2]:
                value_to_display = m.get('value')
                if 'format_func' in m:
                    value_to_display = m['format_func'](value_to_display)
                elif m.get('format') and value_to_display is not None:
                    value_to_display = f"{value_to_display:{m['format']}}"
                else:
                    value_to_display = str(value_to_display)

                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']
                
                st.metric(label=m['label'], value=value_to_display, help=m['help'])

        with col3:
            for m in all_metrics[metrics_per_col*2:]:
                value_to_display = m.get('value')
                if 'format_func' in m:
                    value_to_display = m['format_func'](value_to_display)
                elif m.get('format') and value_to_display is not None:
                    value_to_display = f"{value_to_display:{m['format']}}"
                else:
                    value_to_display = str(value_to_display)

                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']
                
                st.metric(label=m['label'], value=value_to_display, help=m['help'])
        
        with col4:
            st.markdown(
                """
                <h3 style="margin-top: -50px; margin-bottom: 10px;">The Big Picture</h3>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 8px; height: 100%; margin-top: -10px;">
                <p>Our analysis on Apple (AAPL) indicates a mixed picture. While it is a high-quality business with a strong competitive advantage (moat), its current valuation metrics—like a P/E ratio of {metrics_data.get('PE Ratio (TTM)', 'N/A'):.2f} and a P/B ratio of {metrics_data.get('P/B Ratio', 'N/A'):.2f}—are significantly higher than what a traditional value investor would look for. However, the company's strong historical performance and high ROA suggest a very efficient business. This means the market is placing a high value on future growth and brand, rather than just the balance sheet. For an investor focused on a significant margin of safety, this stock may not present a compelling opportunity at its current price.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")

        # --- VALUATION DASHBOARD ---
        st.subheader("💰 Intrinsic Value & Margin of Safety")

        # --- Section intro ---
        st.markdown("""
        <div style="background-color:#f0f2f6; padding:1rem; border-radius:10px;">
            <p><strong>How to Read This:</strong> This section estimates Apple’s intrinsic value using 
            discounted cash flow (DCF) analysis under three scenarios — conservative, base, and aggressive.
            The <strong>Margin of Safety (MOS)</strong> shows how much downside protection the investor has 
            if assumptions don’t hold true.</p>
        </div>
        """, unsafe_allow_html=True)

        # --- Philosophical summary ---
        st.markdown("""
        ### 🧠 Investment Verdict
        > **"A Wonderful Business at a Non-Sensible Price."**

        Apple is a world-class company with a wide moat, but the market’s optimism around 
        AI/LLM growth leaves little room for error. Intrinsic value estimates show that 
        the stock offers **no meaningful Margin of Safety** at current prices.
        """)

        st.markdown("---")

        # --- Scenario inputs ---
        st.markdown("### 🧮 DCF Scenario Simulator")

        # Add interactive controls
        current_price = 256.00
        wacc = st.slider("Discount Rate (WACC)", 7.0, 10.0, 8.0, step=0.1)
        tgr = st.slider("Terminal Growth Rate (%)", 2.0, 4.0, 2.5, step=0.1)

        # Mock intrinsic value function (you can connect your actual DCF function later)
        def intrinsic_value_scenario(wacc, tgr):
            if wacc >= 9.5:
                return 142.0
            elif wacc >= 8.5:
                return 193.0
            else:
                return 287.0 + (tgr - 2.5)*15  # adds small variation

        intrinsic_value = intrinsic_value_scenario(wacc, tgr)
        mos = 1 - (current_price / intrinsic_value)

        col1, col2, col3 = st.columns(3)
        col1.metric("Intrinsic Value", f"${intrinsic_value:,.2f}")
        col2.metric("Current Price", f"${current_price:,.2f}")
        mos_color = "🟢" if mos > 0.15 else "🟡" if mos > 0 else "🔴"
        col3.metric("Margin of Safety", f"{mos:.1%} {mos_color}")

        # --- NEW: LLM Market Premium Indicator ---
        st.markdown("### 🤖 LLM Market Premium")

        # Base intrinsic value (fundamental) vs AI optimism (current price)
        llm_premium = (current_price / intrinsic_value - 1)
        premium_color = "🟢" if llm_premium < 0 else "🔴"

        colA, colB = st.columns(2)
        colA.metric("Fundamental Value (Base Case)", f"${intrinsic_value:,.2f}")
        colB.metric("Market Price Premium", f"{llm_premium:.1%} {premium_color}")

        st.markdown(f"""
        > The market is pricing Apple at a **{llm_premium*100:.1f}% premium** above its intrinsic value — 
        an **“LLM optimism surcharge”** driven by expectations that AI and on-device intelligence will 
        unlock new growth. Historically, premiums above 25–30% suggest the market is extrapolating future 
        tech potential rather than present fundamentals.
        """)

        st.markdown("---")

        # --- Visual comparison ---
        st.markdown("### 📊 Valuation Scenarios")
        valuation_data = {
            "Valuation Case": ["Conservative", "Base", "Aggressive (AI/LLM Premium)"],
            "Intrinsic Value ($)": [142, 193, 287],
        }
        valuation_df = pd.DataFrame(valuation_data)

        fig, ax = plt.subplots()
        ax.bar(valuation_df["Valuation Case"], valuation_df["Intrinsic Value ($)"], alpha=0.7)
        ax.axhline(current_price, color='red', linestyle='--', label=f"Current Price (${current_price})")
        ax.set_ylabel("Price ($)")
        ax.legend()
        st.pyplot(fig)

        st.info("Apple trades above its fair value under both conservative and base assumptions. "
                "Only the most optimistic AI/LLM growth scenario supports the current price.")

        st.markdown("---")

        # --- Target Buy Price ---
        st.markdown("### 🎯 Target Buy Price Calculation")

        base_case_intrinsic_value = 193.00
        desired_mos = 0.15
        target_buy_price = base_case_intrinsic_value * (1 - desired_mos)

        buy_col1, buy_col2, buy_col3 = st.columns(3)
        buy_col1.metric("Base Case Intrinsic Value", f"${base_case_intrinsic_value:.2f}")
        buy_col2.metric("Desired Margin of Safety", f"{desired_mos:.0%}")
        buy_col3.metric("Target Buy Price", f"${target_buy_price:.2f}")

        st.markdown(f"""
        > To own Apple with a **15% Margin of Safety**, an investor should wait for the price 
        to fall to **around ${target_buy_price:.2f}**, roughly **{((current_price - target_buy_price)/current_price):.0%} below** its current level.
        """)

        st.markdown("---")

        # --- Buffett vs Graham summary ---
        st.markdown("### 🧭 Graham–Buffett–Modern Framework")

        framework_df = pd.DataFrame({
            "Layer": [
                "Graham: Defensive Deep Value",
                "Buffett: Quality & Moat",
                "Modern: Growth-Adjusted Value"
            ],
            "Criterion": [
                "P/B < 1.5 and P/E < 15",
                "Durable Moat + High ROE (>20%)",
                "PEG ≤ 1.5 and Positive MOS"
            ],
            "Apple’s Result": [
                "❌ Fails – Intangibles distort P/B",
                "✅ Pass – Wide Moat, ROE 154.9%",
                "⚠️ Fails – PEG≈2.9, MOS Negative"
            ]
        })
        st.dataframe(framework_df, use_container_width=True, hide_index=True)

        st.markdown("""
        > **Conclusion:** Apple passes Buffett’s quality screen but fails Graham’s value tests 
        and the modern PEG-MOS standard. It’s a **wonderful business, not a wonderful buy**.
        """)

        st.markdown("---")

        # --- Wisdom quote footer ---
        st.markdown("""
        > *“The intelligent investor is a realist who sells to optimists and buys from pessimists.”*  
        > — Benjamin Graham
        """)

        # --- EXPLAINABILITY & REASONING ---
        st.subheader("🧠 Explainable AI: The Reasoning Behind the Analysis")
        st.markdown("""
        Our AI blends quantitative modeling with the timeless logic of value investing — explaining **why** a decision was made, not just **what** the result is.
        """)

        # --- AI SUMMARY ---
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:1.5rem; border-radius:10px; margin-top:0.5rem;">
            <h4>AI Summary</h4>
            <p>Our analysis concludes that <strong>Apple (AAPL)</strong> is a 
            <strong>"Wonderful Business at a Non-Sensible Price."</strong></p>
            <p>While Apple demonstrates world-class profitability and a wide economic moat, 
            its current market price reflects highly optimistic growth assumptions tied to future AI/LLM opportunities — leaving **no meaningful Margin of Safety** for value-oriented investors.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # --- SPLIT LAYOUT ---
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.markdown("#### 🔍 Feature Importance: What Drove the Decision")
            importance_df = generate_feature_importance_data()

            fig_importance = px.bar(
                importance_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title="Top Drivers of the AI Valuation Decision",
                labels={'Importance': 'Relative Influence (%)', 'Feature': 'Valuation Factor'},
                color_discrete_sequence=['#2563eb']
            )
            fig_importance.update_layout(
                title_x=0.05,
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_importance, use_container_width=True)

        with exp_col2:
            st.markdown("#### 📖 The Story Behind the Data")
            with st.container(border=True):
                st.markdown("""
                - **Graham Filter:** AAPL’s **P/E (38.8)** and **P/B (58.2)** fail the Graham deep value screen — a reflection not of weakness, but of how intangible-heavy tech firms break traditional accounting ratios.  
                - **Buffett Lens:** Apple passes the **Buffett Quality Test**, earning a ✅ for its wide moat, sticky ecosystem, and **ROE of 154.9%**, signaling world-class efficiency.  
                - **AI & Moat Resilience:** The AI detects that much of Apple’s premium valuation is tied to **market optimism around AI/LLM integration**, a story-driven multiple expansion.  
                - **DCF Reality Check:** Discounted cash flow (DCF) results show that the current price is justified only under **aggressive growth** assumptions — removing the Margin of Safety that value investors demand.
                """)

        st.markdown("---")

        # --- DECISION-MAKING FLOW ---
        st.subheader("🧩 AI Decision-Making Framework")
        st.markdown("The AI applies a layered, human-intelligible reasoning chain to reach its investment verdict.")

        with st.container(border=True):
            st.markdown("""
            1. ✅ **Quality Screen (Buffett)** — Tests for a **Durable Economic Moat** and high **Capital Efficiency (ROE/ROIC)**.  
            **Result:** Pass — Apple excels in quality and profitability.  
            2. ❌ **Growth-Adjusted Value (Adapted Graham)** — Evaluates the **PEG Ratio** to balance valuation vs. growth.  
            **Result:** Fail — PEG well above 2.0 indicates overvaluation.  
            3. ❌ **Safety Margin Test (Buffett + Graham)** — Runs a **DCF Analysis** under conservative and base cases to confirm value safety.  
            **Result:** Fail — Negative Margin of Safety across both.  
            4. 🧾 **Final Determination:** The AI issues a **NO-BUY** recommendation at current levels — a great company, but not a great price.
            """)

        st.markdown("---")

        # --- REFLECTIVE QUOTE ---
        st.markdown("""
        > *“Price is what you pay. Value is what you get.”*  
        > — Warren Buffett
        """)

        # --- CHAT INTERFACE ---
        st.header("💬 AI Co-Pilot")
        st.markdown("Ask me anything about this stock or the analysis above.")

        # --- CHAT HISTORY ---
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI Stock Insight Co-Pilot. What stock would you like to analyze today?"})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- CHAT INPUT ---
        if prompt := st.chat_input("Ask about the stock..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    if "buy" in prompt.lower() or "how much" in prompt.lower():
                        response = "Based on our analysis, the current margin of safety of 15.65% is strong enough to justify a buy signal. We recommend a phased approach to take advantage of any short-term volatility."
                    elif "risks" in prompt.lower() or "risk" in prompt.lower():
                        response = "The primary risks for this stock are a slightly elevated P/E ratio and general market volatility. However, its strong business moat and consistent earnings growth help mitigate these risks."
                    else:
                        response = "That is a great question. The AI model is currently processing your request and will update the dashboard and chat with the latest insights. [Placeholder for a real AI response]."

                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})