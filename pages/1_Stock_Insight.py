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

@st.cache_data
def get_historical_financials(ticker):
    """Fetches historical financials for 5 years."""
    ticker_obj = yf.Ticker(ticker)
    
    try:
        # Get annual financials for the last ~5 years
        income_statement = ticker_obj.income_stmt
        balance_sheet = ticker_obj.balance_sheet
        cash_flow = ticker_obj.cash_flow
        
        # Pull key metrics from the fetched data
        # Note: yfinance data is not always clean and might require more robust error handling
        # This is a simplified version for the prototype.
        
        # Financials
        revenue = income_statement.loc['Total Revenue'].iloc[:5]
        net_income = income_statement.loc['Net Income'].iloc[:5]
        
        # Cash Flow & Balance Sheet
        operating_cash_flow = cash_flow.loc['Cash Flow From Continuing Operating Activities'].iloc[:5]
        capital_expenditures = cash_flow.loc['Capital Expenditures'].iloc[:5]
        
        # Calculate Free Cash Flow (FCF)
        # FCF = Operating Cash Flow - Capital Expenditures
        fcf = operating_cash_flow.values - np.abs(capital_expenditures.values)
        fcf = pd.Series(fcf, index=operating_cash_flow.index)
        
        # Metrics
        total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[:5]
        total_equity = balance_sheet.loc['Stockholders Equity'].iloc[:5]
        debt_to_equity = total_liabilities.values / total_equity.values
        debt_to_equity = pd.Series(debt_to_equity, index=total_equity.index)

        # Calculate ROE
        roe = net_income.values / total_equity.values
        roe = pd.Series(roe, index=total_equity.index)
        
        return {
            'revenue': revenue,
            'net_income': net_income,
            'fcf': fcf,
            'debt_to_equity': debt_to_equity,
            'roe': roe
        }
        
    except Exception as e:
        st.error(f"Could not fetch detailed financial data for {ticker.upper()}. Error: {e}")
        return None

@st.cache_data
def get_moat_and_management_rating(ticker):
    """Generates mock qualitative ratings."""
    return {
        "moat": {
            "rating": "Very Wide Moat",
            "explanation": "Powered by a deep ecosystem, brand loyalty, and significant switching costs. This is not just a product, but a lifestyle."
        },
        "management": {
            "rating": "Exceptional",
            "explanation": "Proven track record of innovation, efficient capital allocation, and strong shareholder returns. Consistently outpaces rivals."
        }
    }

@st.cache_data
def get_similar_stocks(ticker):
    """Returns mock data for similar stocks."""
    if ticker.upper() == 'AAPL':
        return ['MSFT', 'GOOG', 'NVDA']
    return ['MSFT', 'GOOG', 'NVDA']


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
            {"label": "P/B Ratio", "value": metrics_data.get('P/B Ratio'), "help": "The P/B (Price-to-Book) ratio compares a stock's price to the company's net asset value. For a value investor, a P/B ratio under 1 is a traditional signal of an undervalued stock. Apple's P/B of ~58 is exceptionally high, reflecting strong market confidence in its intangible assets like brand and ecosystem, rather than its book value. This is significantly above its own 5-year average of ~29 and the technology industry average of ~13. This indicates the market is placing a very high value on the company's intangible assets, like its brand and ecosystem, rather than its tangible balance sheet. This is a crucial distinction from traditional value investing.", "format": ".2f"},
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

        # --- CONSOLIDATED INTRINSIC VALUE & MARGIN OF SAFETY SECTION ---
        # This replaces the previous two sections entirely.

        st.subheader("🎯 Intrinsic Value & Margin of Safety")
        st.markdown("""
        The **Margin of Safety (MOS)** is the cornerstone of value investing, providing a crucial buffer against potential losses. It's the difference between a stock's estimated **intrinsic value** (its real worth) and its **market price**. A strong margin of safety is generally considered to be in the **20% to 30%** range.
        """)

        # Get current price
        current_price = metrics_data.get('Previous Close', 0)
        # Mock calculation using the base case intrinsic value
        base_case_intrinsic_value = 193.00

        # Calculate the actual MOS
        if base_case_intrinsic_value > 0:
            actual_mos_percent = ((base_case_intrinsic_value - current_price) / base_case_intrinsic_value) * 100
        else:
            actual_mos_percent = 0

        if actual_mos_percent > 15:
            verdict_text = "presents a strong"
            color = "green"
            arrow = "▲"
        elif actual_mos_percent > 0:
            verdict_text = "offers a thin"
            color = "orange"
            arrow = "↔"
        else:
            verdict_text = "offers no meaningful"
            color = "red"
            arrow = "▼"

        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="font-size: 1.1em; font-weight: 500; color: #555;">Current Price:</p>
                    <p style="font-size: 2em; font-weight: 700; margin-top: -10px;">${current_price:.2f}</p>
                </div>
                <div>
                    <p style="font-size: 1.1em; font-weight: 500; color: #555;">Base Case Intrinsic Value:</p>
                    <p style="font-size: 2em; font-weight: 700; margin-top: -10px;">${base_case_intrinsic_value:.2f}</p>
                </div>
                <div>
                    <p style="font-size: 1.1em; font-weight: 500; color: #555;">Calculated MOS:</p>
                    <p style="font-size: 2em; font-weight: 700; margin-top: -10px; color: {color};">{actual_mos_percent:.1f}%</p>
                </div>
            </div>
            <hr style="border: 1px solid #ddd; margin: 15px 0;">
            <p style="font-size: 1.1em; font-weight: 500;">
            Our analysis indicates the stock is currently trading at a 
            <span style="color: {color};"><strong>
            {abs(actual_mos_percent):.1f}% { 'discount' if actual_mos_percent > 0 else 'premium' }
            </strong></span> relative to its estimated intrinsic value, and {verdict_text} margin of safety for a value investor.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # --- DCF Scenario Simulator ---
        st.subheader("🧮 DCF Scenario Simulator")

        st.markdown("""
        We use a **Discounted Cash Flow (DCF)** model to estimate what a company is truly worth — its **intrinsic value**.

        DCF is like asking:  
        > “If I owned this business and it kept generating cash every year, how much would all that future cash be worth to me today?”

        It’s one of the most reliable valuation tools because it’s grounded in **cash generation**, not short-term market emotions.
        """)

        with st.expander("💡 How far into the future do we project?"):
            st.markdown("""
            Typically, our model projects **10 years** of future **Free Cash Flows (FCF)**.

            - The first 10 years capture the **growth phase** — where sales, profits, and efficiency may improve.  
            - After year 10, we assume the company settles into a **steady-state**, growing at a modest, stable pace.

            This steady pace is captured by the **Terminal Growth Rate**, which usually ranges from **2–3%**, in line with long-term inflation and GDP growth.
            """)

        with st.expander("🧠 Why use DCF instead of other valuation models?"):
            st.markdown("""
            - **DCF** focuses on *cash generation* — it values the business like an owner, not a trader.  
            - Models like **P/E** or **P/S multiples** depend on market sentiment and comparable companies.  
            - **DCF** tells you what the business is *worth*, not just what others *pay* for it.
            """)

        with st.expander("📘 Quick Analogy"):
            st.markdown("""
            Imagine you own a **money machine** that prints \$10 every year.  
            Would you pay \$100 for it? \$200?  

            It depends on:
            - How much you expect it to grow (the **FCF Growth Rate**)  
            - How risky it is (your **Discount Rate**, or WACC)  
            - And how long it can keep printing money (your **Projection Period** + **Terminal Growth Rate**)  

            DCF ties all these together to find the fair price *today*.
            """)

        st.markdown("---")

        # --- Valuation Scenarios ---
        st.subheader("📊 Valuation Scenarios")

        st.markdown("""
        Before playing with the sliders, here’s how small changes in assumptions can shift a stock’s value dramatically.  

        💡 **Why these numbers?**
        - **Free Cash Flow (FCF) Growth →** How fast the company’s cash generation grows.  
        Think of it as the *engine power* of the business. 5–15% is typical for stable firms, 15–25%+ for high-growth companies.
        - **Discount Rate (WACC) →** Your required rate of return, adjusted for risk.  
        Like a *risk premium* — the more uncertain the company, the higher the WACC you demand.
        - **Terminal Growth Rate →** The company’s long-term, steady-state growth after your forecast period.  
        Typically close to inflation (2–3%), since no company can outgrow the economy forever.
        """)

        st.markdown("---")

        # --- Example Scenario Table ---
        valuation_data = {
            "Valuation Case": ["Conservative", "Base", "Aggressive"],
            "FCF Growth (5Y)": ["5%", "10%", "18%"],
            "WACC": ["9.5%", "8.5%", "7.5%"],
            "Terminal Growth Rate": ["2%", "2.5%", "3%"],
            "Intrinsic Value ($)": [142, 193, 287],
        }
        valuation_df = pd.DataFrame(valuation_data)
        st.dataframe(valuation_df, use_container_width=True, hide_index=True)

        st.markdown("""
        💡 **Why these numbers?**

        - **Free Cash Flow (FCF) Growth** → Represents how fast the company’s cash generation grows.  
        Think of it as the **engine power** of the business. 5–15% is typical for stable firms, 15–25%+ for fast growers.

        - **Discount Rate (WACC)** → This is your *required rate of return*, adjusted for risk.  
        Like a **risk premium** — the more uncertain the company, the higher the WACC you demand.

        - **Terminal Growth Rate** → The company’s long-term, steady-state growth after your forecast period.  
        Typically close to inflation (2–3%), since no company can outgrow the economy forever.

        ---

        ### 🧠 The DCF Formula (Simplified)

        > **Intrinsic Value = Σ (FCFₜ / (1 + WACC)ᵗ) + (Terminal Value / (1 + WACC)ⁿ)**  
        > where **Terminal Value = FCFₙ × (1 + g) / (WACC - g)**

        In plain English:
        - Project **future cash flows** (like forecasting your salary growth).
        - **Discount** them back to today (since money today is worth more than tomorrow).
        - Add the **terminal value** for all years beyond your forecast.

        ---

        ### 🎛️ Your DCF Playground
        Now, adjust the assumptions below — see how small changes in growth or risk completely shift the company’s intrinsic value.
        """)

        # --- User Inputs (Sliders) ---
        col_fcf, col_wacc, col_term = st.columns(3)

        with col_fcf:
            st.markdown("#### FCF Growth Rate")
            st.markdown("*Higher = faster-growing cash flow engine.*")
            fcf_growth = st.slider("Projected FCF Growth (5–10 years)", 0.05, 0.20, 0.10, step=0.01, label_visibility="collapsed")
            st.caption("Typically 5–15% for mature firms, 15–25%+ for fast growers.")

        with col_wacc:
            st.markdown("#### Discount Rate (WACC)")
            st.markdown("*Think of this as your ‘risk hurdle.’ Higher WACC = higher required return.*")
            wacc = st.slider("Discount Rate (WACC)", 0.07, 0.10, 0.085, step=0.005, label_visibility="collapsed")
            st.caption("Usually 7–9% for stable firms, 9–12% for risky ones.")

        with col_term:
            st.markdown("#### Terminal Growth Rate")
            st.markdown("*The company’s long-term steady growth after 10 years.*")
            terminal_growth = st.slider("Terminal Growth Rate (%)", 0.02, 0.04, 0.025, step=0.005, label_visibility="collapsed")
            st.caption("Typically near inflation (~2–3%).")

        # --- DCF Calculation Function ---
        def calculate_dcf(fcf_growth, wacc, terminal_growth, base_fcf=10000, years=10, shares_outstanding=16_000):
            """
            Simplified DCF model:
            - fcf_growth: annual growth rate in FCF
            - wacc: discount rate
            - terminal_growth: long-term growth rate after forecast
            - base_fcf: starting free cash flow (in millions)
            - shares_outstanding: in millions
            """
            # Project future FCFs
            fcfs = [base_fcf * ((1 + fcf_growth) ** t) for t in range(1, years + 1)]

            # Discount each FCF to present value
            discounted_fcfs = [fcf / ((1 + wacc) ** t) for t, fcf in enumerate(fcfs, start=1)]

            # Terminal value
            terminal_value = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
            discounted_terminal = terminal_value / ((1 + wacc) ** years)

            # Enterprise value (in millions)
            total_value = sum(discounted_fcfs) + discounted_terminal

            # Per-share value
            intrinsic_value = total_value / shares_outstanding
            return intrinsic_value

        # --- Live DCF Calculation ---
        intrinsic_value = calculate_dcf(fcf_growth, wacc, terminal_growth)
        current_price = 230  # example

        st.success(f"💰 **Estimated Intrinsic Value:** ${intrinsic_value:.2f} per share")

        st.markdown("""
        Use this as a **guide**, not an exact prediction.  
        The real insight comes from understanding how **each assumption** changes the valuation.
        """)

        # --- Interactive Plotly Chart ---
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Intrinsic Value"],
            y=[intrinsic_value],
            name="Intrinsic Value ($)",
            marker_color="#4CAF50",
            text=[f"${intrinsic_value:.2f}"],
            textposition="auto"
        ))
        fig.add_trace(go.Bar(
            x=["Current Price"],
            y=[current_price],
            name="Current Price ($)",
            marker_color="#FF6B6B",
            text=[f"${current_price:.2f}"],
            textposition="auto"
        ))
        fig.update_layout(
            title="Intrinsic Value vs Current Market Price",
            yaxis_title="Price ($)",
            barmode="group",
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"""
        At your chosen assumptions:
        - **FCF Growth:** {fcf_growth*100:.1f}%
        - **WACC:** {wacc*100:.1f}%
        - **Terminal Growth:** {terminal_growth*100:.1f}%

        👉 The intrinsic value changes dynamically — move the sliders to explore best and worst cases.
        """)

        st.markdown("""
        > *“Price is what you pay. Value is what you get.”*  
        > — **Warren Buffett**
        """)


                # --- MOAT, MANAGEMENT & SIMILAR STOCKS ---
        st.subheader("💡 Qualitative Insights")
        qual_col1, qual_col2 = st.columns(2)
        
        ratings = get_moat_and_management_rating(ticker)
        
        with qual_col1:
            st.markdown("#### The Moat: Competitive Advantage")
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 8px;">
                <p><strong>Rating:</strong> {ratings['moat']['rating']}</p>
                <p><strong>Explanation:</strong> {ratings['moat']['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Management & Capital Allocation")
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 8px;">
                <p><strong>Rating:</strong> {ratings['management']['rating']}</p>
                <p><strong>Explanation:</strong> {ratings['management']['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with qual_col2:
            st.markdown("#### 🔄 Stocks Like This")
            similar_stocks = get_similar_stocks(ticker)
            
            # Create a comparison dataframe
            compare_data = {'Ticker': [ticker] + similar_stocks}
            compare_data['P/E Ratio'] = [get_key_metrics(t).get('PE Ratio (TTM)') for t in compare_data['Ticker']]
            compare_data['P/B Ratio'] = [get_key_metrics(t).get('priceToBook') for t in compare_data['Ticker']]
            compare_data['ROE'] = [get_key_metrics(t).get('returnOnEquity') for t in compare_data['Ticker']]
            
            compare_df = pd.DataFrame(compare_data)
            
            st.markdown(f"Our AI has identified the following stocks with similar business models or valuation characteristics to {ticker.upper()}.")
            
            st.dataframe(compare_df, use_container_width=True)

            # Customizable comparison chart
            chart_metric = st.selectbox(
                "Select a metric to compare:",
                ['P/E Ratio', 'P/B Ratio', 'ROE']
            )

            fig_comp = px.bar(
                compare_df.melt(id_vars='Ticker', value_vars=[chart_metric]),
                x='Ticker',
                y='value',
                title=f'Comparison by {chart_metric}',
                labels={'value': chart_metric, 'Ticker': 'Company'},
                color='Ticker',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            st.plotly_chart(fig_comp, use_container_width=True)

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

                # --- HISTORICAL FINANCIALS ---
        st.subheader("📊 Historical Performance (Last 5 Years)")
        st.markdown("A look at the company's financial trends helps confirm the durability of its business.")
        
        financials = get_historical_financials(ticker)

        if financials:
            # Create a combined dataframe for charting
            financials_df = pd.DataFrame({
                'Revenue': financials['revenue'],
                'Net Income': financials['net_income'],
                'Free Cash Flow': financials['fcf'],
                'ROE': financials['roe']
            }).sort_index()

            # Chart 1: Revenue & Net Income
            fig_inc = go.Figure()
            fig_inc.add_trace(go.Bar(x=financials_df.index, y=financials_df['Revenue'], name='Revenue', marker_color='#2563EB'))
            fig_inc.add_trace(go.Bar(x=financials_df.index, y=financials_df['Net Income'], name='Net Income', marker_color='#FBBF24'))
            fig_inc.update_layout(title=f'Revenue & Net Income Trend for {ticker.upper()}',
                                  barmode='group',
                                  xaxis_title='Year',
                                  yaxis_title='Amount ($)',
                                  legend_title_text='Metric')
            st.plotly_chart(fig_inc, use_container_width=True)

            # Chart 2: FCF & ROE
            fig_fcf = go.Figure()
            fig_fcf.add_trace(go.Scatter(x=financials_df.index, y=financials_df['Free Cash Flow'], mode='lines+markers', name='Free Cash Flow', line=dict(color='#047857')))
            fig_fcf.add_trace(go.Scatter(x=financials_df.index, y=financials_df['ROE']*100, mode='lines+markers', name='ROE (%)', line=dict(color='#B91C1C'), yaxis='y2'))
            fig_fcf.update_layout(title=f'Free Cash Flow & ROE Trend for {ticker.upper()}',
                                  xaxis_title='Year',
                                  yaxis_title='Free Cash Flow ($)',
                                  yaxis2=dict(title='ROE (%)', overlaying='y', side='right'))
            st.plotly_chart(fig_fcf, use_container_width=True)

        st.markdown("---")

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