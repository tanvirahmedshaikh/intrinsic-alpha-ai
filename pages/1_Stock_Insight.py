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

# The updated function now also clears the ticker input value.
def new_chat_session():
    """Creates a new chat session and clears the ticker input."""
    session_id = str(uuid.uuid4())
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {"title": "New Chat"}
    st.session_state.editing_session_id = None
    # Crucial line: Reset the ticker input widget value in session state
    st.session_state.stock_ticker_input = ""

# --- SIDEBAR: CHAT HISTORY ---
with st.sidebar:
    st.header("IntrinsicAlpha AI")
    # Call the new function directly when the button is clicked
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
    """Fetches all available historical financials."""
    ticker_obj = yf.Ticker(ticker)

    try:
        # Get all available annual financials
        income_statement = ticker_obj.income_stmt
        balance_sheet = ticker_obj.balance_sheet
        cash_flow = ticker_obj.cash_flow

        # Pull key metrics from the fetched data
        # No slicing here, so we get all available data
        revenue = income_statement.loc['Total Revenue']
        net_income = income_statement.loc['Net Income']
        operating_cash_flow = cash_flow.loc['Cash Flow From Continuing Operating Activities']

        # Use the correct singular name from your API data
        capital_expenditures = cash_flow.loc['Capital Expenditure']

        # Calculate Free Cash Flow (FCF)
        fcf = operating_cash_flow.values - np.abs(capital_expenditures.values)
        fcf = pd.Series(fcf, index=operating_cash_flow.index)

        # Metrics
        total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest']
        total_equity = balance_sheet.loc['Stockholders Equity']
        debt_to_equity = total_liabilities.values / total_equity.values
        debt_to_equity = pd.Series(debt_to_equity, index=total_equity.index)

        # Calculate ROE
        roe = net_income.values / total_equity.values
        roe = pd.Series(roe, index=total_equity.index)

        # Sort all series by date to ensure they are in the correct order for plotting
        return {
            'revenue': revenue.sort_index(),
            'net_income': net_income.sort_index(),
            'fcf': fcf.sort_index(),
            'debt_to_equity': debt_to_equity.sort_index(),
            'roe': roe.sort_index()
        }
    except Exception as e:
        print(f"Could not fetch detailed financial data for {ticker.upper()}. Error: {e}")
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

# --- DCF Calculation Helper Functions ---
@st.cache_data
def get_dcf_base_data(ticker):
    """Fetches the last reported Free Cash Flow and Shares Outstanding."""
    ticker_obj = yf.Ticker(ticker)
    try:
        # Use income statement and balance sheet to find latest values
        # Note: This is a simplified fetch, and a real app might need more robust error handling
        fcf = ticker_obj.cash_flow.loc['Free Cash Flow'].iloc[0]
        shares = ticker_obj.get_shares_full().iloc[-1]
        return fcf, shares
    except Exception:
        st.error("Could not fetch FCF or Shares Outstanding. Using placeholder data.")
        return 100_000, 16_000_000 # Return large placeholder values

@st.cache_data
def calculate_dcf(fcf_growth, wacc, terminal_growth, base_fcf, years, shares_outstanding):
    """
    Simplified DCF model:
    - fcf_growth: annual growth rate in FCF
    - wacc: discount rate
    - terminal_growth: long-term growth rate after forecast
    - base_fcf: starting free cash flow
    - shares_outstanding: number of shares
    """
    # Project future FCFs
    fcfs = [base_fcf * ((1 + fcf_growth) ** t) for t in range(1, years + 1)]

    # Discount each FCF to present value
    discounted_fcfs = [fcf / ((1 + wacc) ** t) for t, fcf in enumerate(fcfs, start=1)]

    # Terminal value
    terminal_value = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    discounted_terminal = terminal_value / ((1 + wacc) ** years)

    # Enterprise value
    total_value = sum(discounted_fcfs) + discounted_terminal

    # Per-share value
    intrinsic_value = total_value / shares_outstanding
    return intrinsic_value

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
            {"label": "P/E Historical Avg (5Y)", "value": hist_metrics.get('Historical PE Avg (5Y)'), "help": "This compares the current P/E to its 5-year historical average (~29). A P/E of ~38.89 is significantly higher, indicating the stock is valued above its own recent history and suggests strong market optimism about future growth.", "format": ".2f"},
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

        # Get dynamic data for base case intrinsic value
        base_fcf, shares_outstanding = get_dcf_base_data(ticker)
        
        # Calculate the base case intrinsic value using dynamic data
        base_case_intrinsic_value = calculate_dcf(
            fcf_growth=0.10,
            wacc=0.085,
            terminal_growth=0.025,
            base_fcf=base_fcf,
            years=10,
            shares_outstanding=shares_outstanding,
        )

        # Get the current market price dynamically
        current_price = metrics_data.get('Previous Close', 0)

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
        # Define the reusable Markdown text
        dcf_explanation = """
        💡 **Why these numbers?**

        - **Free Cash Flow (FCF) Growth** → How fast the company’s cash generation grows. Think of it as the **engine power** of the business. A range of 5–15% is typical for stable firms, while 15–25%+ is for high-growth companies.

        - **Discount Rate (WACC)** → This is your required rate of return, adjusted for the risk of the investment. It acts as a **risk premium**—the more uncertain a company, the higher the WACC you demand.
            - **A good rule of thumb for WACC:**
                * **7-9%:** For large, stable companies with a proven track record.
                * **9-12%:** For companies with a higher risk profile or more volatile earnings.
                * **15%+:** For startups and high-growth firms that carry significant risk.

        - **Terminal Growth Rate** → The company’s long-term, steady-state growth rate after your forecast period. This is typically set close to the long-term inflation rate (2–3%), as no company can realistically outgrow the overall economy forever.
        """

        st.subheader("📊 Valuation Scenarios")

        st.markdown("""
        Before playing with the sliders, here’s how small changes in assumptions can shift a stock’s value dramatically.  
        """)

        # --- Example Scenario Table ---
        base_fcf, shares_outstanding = get_dcf_base_data(ticker)

        # Define scenario parameters
        scenario_parameters = {
            "Conservative": {"fcf_growth": 0.05, "wacc": 0.095, "terminal_growth": 0.02},
            "Base": {"fcf_growth": 0.10, "wacc": 0.085, "terminal_growth": 0.025},
            "Aggressive": {"fcf_growth": 0.18, "wacc": 0.075, "terminal_growth": 0.03},
        }

        # Dynamically calculate intrinsic values for each scenario
        intrinsic_values = []
        for case, params in scenario_parameters.items():
            value = calculate_dcf(
                fcf_growth=params["fcf_growth"],
                wacc=params["wacc"],
                terminal_growth=params["terminal_growth"],
                base_fcf=base_fcf,
                years=10,
                shares_outstanding=shares_outstanding,
            )
            intrinsic_values.append(value)

        # Create the dataframe with dynamic values
        valuation_data = {
            "Valuation Case": list(scenario_parameters.keys()),
            "FCF Growth (5Y)": [f"{p['fcf_growth']:.0%}" for p in scenario_parameters.values()],
            "WACC": [f"{p['wacc']:.1%}" for p in scenario_parameters.values()],
            "Terminal Growth Rate": [f"{p['terminal_growth']:.1%}" for p in scenario_parameters.values()],
            "Intrinsic Value ($)": [f"{v:.2f}" for v in intrinsic_values],
        }

        valuation_df = pd.DataFrame(valuation_data)
        st.dataframe(valuation_df, use_container_width=True, hide_index=True)

        st.markdown(dcf_explanation)

        st.markdown("---")

        st.markdown("""
        ### 🧠 The DCF Formula (Simplified)

        > **Intrinsic Value = Σ (FCFₜ / (1 + WACC)ᵗ) + (Terminal Value / (1 + WACC)ⁿ)**  
        > where **Terminal Value = FCFₙ × (1 + g) / (WACC - g)**

        In plain English:
        - Project **future cash flows** (like forecasting your salary growth).
        - **Discount** them back to today (since money today is worth more than tomorrow).
        - Add the **terminal value** for all years beyond your forecast.
        """)

        st.markdown("""---""")

        st.markdown("""
        ### 🎛️ Your DCF Playground
        Now, adjust the assumptions below — see how small changes in growth or risk completely shift the company’s intrinsic value.
        """)

        # --- User Inputs (Sliders) ---
        col_fcf, col_wacc, col_term = st.columns(3)

        with col_fcf:
            st.markdown("#### FCF Growth Rate")
            st.markdown("*Think of it as the engine power of the business. Higher = faster-growing cash flow*")
            fcf_growth_pct = st.slider("Projected FCF Growth (5–10 years)", 5, 30, 10, step=1, format="%d%%", label_visibility="collapsed")
            fcf_growth = fcf_growth_pct / 100  # convert to decimal for calculations
            st.caption("Typically 5–15% for mature firms, 15–25%+ for fast growers.")

        with col_wacc:
            st.markdown("#### Discount Rate (WACC)")
            st.markdown("*Think of this as your ‘risk hurdle.’ Higher WACC = higher required return.*")
            wacc_pct = st.slider("Discount Rate (WACC)", 5.0, 20.0, 8.5, step=0.5, format="%.1f%%", label_visibility="collapsed")
            wacc = wacc_pct / 100
            st.caption("Usually 7–9% for stable firms, 9–12% for risky ones.")

        with col_term:
            st.markdown("#### Terminal Growth Rate")
            st.markdown("*The company’s long-term steady growth after 10 years.*")
            terminal_growth_pct = st.slider("Terminal Growth Rate (%)", 2.0, 4.0, 2.5, step=0.1, format="%.1f%%", label_visibility="collapsed")
            terminal_growth = terminal_growth_pct / 100
            st.caption("Typically near inflation (~2–3%).")

        # --- Live DCF Calculation ---
        # Get dynamic data
        base_fcf, shares_outstanding = get_dcf_base_data(ticker)
        
        # Calculate intrinsic value using fetched data and user inputs
        intrinsic_value = calculate_dcf(fcf_growth, wacc, terminal_growth, base_fcf, 10, shares_outstanding)
        
        # Get the current market price dynamically
        current_price = get_key_metrics(ticker).get('Previous Close', 0)

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
        
        # Calculate Margin of Safety and determine color
        if intrinsic_value > 0:
            mos_percent = ((intrinsic_value - current_price) / intrinsic_value) * 100
        else:
            mos_percent = 0
            
        mos_color = "green" if mos_percent > 0 else "red"
        
        # Add a text annotation for Margin of Safety
        fig.add_annotation(
            x=0.5,  # Centered horizontally
            y=1.1,  # Positioned at a higher point on the chart, above the title
            xref="paper",
            yref="paper",
            text=f"Margin of Safety: {mos_percent:.1f}%",
            showarrow=False,
            font=dict(
                size=16,
                color=mos_color
            )
        )
        
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


        # --- QUALITATIVE INSIGHTS & STOCK COMPARISON ---
        st.subheader("💡 Qualitative Insights")
        st.markdown("We analyze the non-quantifiable strengths of the business, such as its competitive advantages and the quality of its leadership. These are the **bedrock of long-term value investing**.")

        qual_col1, qual_col2 = st.columns([0.45, 0.55])
                
        ratings = get_moat_and_management_rating(ticker)
        key_metrics = get_key_metrics(ticker) # Fetching metrics again for ROIC

        # Example of a new function to get more detailed moat and management info
        def get_detailed_qualitative_insights(ticker):
            if ticker.upper() == 'AAPL':
                return {
                    "moat": {
                        "rating": "Very Wide Moat",
                        "types": [
                            {"name": "Network Effects", "icon": "🌐"},
                            {"name": "High Switching Costs", "icon": "🔗"},
                            {"name": "Intangible Assets (Brand)", "icon": "👑"}
                        ],
                        "explanation": "Powered by a deeply integrated ecosystem of hardware, software, and services. The **Network Effect** is at play as more users on the platform attract more developers and services. This creates **High Switching Costs**, as users are reluctant to leave the familiar ecosystem and abandon their app purchases, media library, and data. The **Intangible Asset** of its powerful brand allows it to command premium pricing."
                    },
                    "management": {
                        "rating": "Exceptional",
                        "explanation": "Management has a proven track record of efficient **capital allocation**, evidenced by consistent, disciplined share buybacks that have reduced the share count over time. Their focus on **innovation and margin control** has allowed the company to generate strong, predictable earnings and free cash flow."
                    }
                }
            else:
                # Placeholder for other tickers
                return {
                    "moat": {
                        "rating": "No Moat",
                        "types": [],
                        "explanation": "Moat analysis is not available for this ticker yet. The AI is constantly learning and adding more detailed insights."
                    },
                    "management": {
                        "rating": "N/A",
                        "explanation": "Management analysis is not yet available for this ticker."
                    }
                }

        # --- LEFT COLUMN: MOAT & MANAGEMENT ---
        with qual_col1:
            detailed_insights = get_detailed_qualitative_insights(ticker)

            st.markdown("#### The Moat: Competitive Advantage")
            st.info(
                f"**Rating:** {detailed_insights['moat']['rating']} "
                f"{' '.join([t['icon'] for t in detailed_insights['moat']['types']])}"
            )
            st.markdown(detailed_insights['moat']['explanation'])

            st.markdown("#### Management & Capital Allocation")
            st.info(f"**Rating:** {detailed_insights['management']['rating']}")
            st.markdown(detailed_insights['management']['explanation'])

        # --- RIGHT COLUMN: COMPARISONS ---
        with qual_col2:
            st.markdown("#### 🔄 Peers & Comparison")
            
            # Hardcoded comparison data, including ROIC
            compare_data = {
                'Ticker': ['AAPL', 'MSFT', 'GOOG', 'NVDA'],
                'P/E Ratio': [38.89, 37.3, 24.95, 51.74],
                'P/B Ratio': [58.2, 11.06, 7.91, 44.63],
                'ROE': [154.9, 32.4, 34.3, 105.2],
                'ROIC': [31.2, 25.5, 21.8, 34.1]
            }
            
            compare_df = pd.DataFrame(compare_data)

            # Add the "Why" column logic
            compare_df['Reason for Comparison'] = [
                "Primary subject of analysis.",
                "A direct competitor in software and enterprise solutions with a strong cloud and AI focus.",
                "A dominant player in digital advertising and a key competitor in AI and cloud computing.",
                "A high-growth leader in the semiconductor industry, crucial for AI advancements."
            ]

            st.markdown(f"""
            Our AI identifies peers with similar business models or valuation characteristics to **{ticker.upper()}**. 
            Comparing them helps us see if the market is valuing your stock fairly relative to its peers.
            """)
            
            st.dataframe(compare_df, use_container_width=True, hide_index=True)

            # --- Consolidated Comparison Charts ---
            st.markdown("##### Visualizing Key Differences")

            chart1, chart2 = st.columns(2)
            
            with chart1:
                # P/E Ratio Comparison
                fig_pe = px.bar(
                    compare_df.melt(id_vars=['Ticker', 'Reason for Comparison'], value_vars=['P/E Ratio']),
                    x='Ticker',
                    y='value',
                    title='P/E Ratio Comparison',
                    labels={'value': 'P/E Ratio'},
                    color='Ticker',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_pe.update_layout(showlegend=False) 
                st.plotly_chart(fig_pe, use_container_width=True)

            with chart2:
                # ROIC Comparison
                fig_roic = px.bar(
                    compare_df.melt(id_vars=['Ticker', 'Reason for Comparison'], value_vars=['ROIC']),
                    x='Ticker',
                    y='value',
                    title='ROIC Comparison',
                    labels={'value': 'ROIC (%)'},
                    color='Ticker',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_roic.update_layout(showlegend=False)
                st.plotly_chart(fig_roic, use_container_width=True)

            st.info("The P/E Ratio reflects market expectations, while ROIC (Return on Invested Capital) measures how efficiently a company uses both debt and equity to generate profits. Comparing them reveals if a high price is justified by high capital efficiency.")

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
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
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

        # --- FINAL VERDICT: CONSOLIDATED FRAMEWORK ---
        st.subheader("🧠 Final Verdict: A Layered AI Framework")
        st.markdown("Our AI applies a step-by-step reasoning chain, blending classic value investing principles with modern quantitative analysis to reach a final verdict.")

        with st.container(border=True):
            st.markdown("""
            1.  ✅ **The Quality Screen (Inspired by Buffett)**
                * **Analogy:** Is this a fortress? We check for a **durable economic moat** and exceptional **capital efficiency (ROE/ROIC)**.
                * **Result:** **PASS**. Apple’s wide moat, sticky ecosystem, and remarkable ROE of 154.9% confirm it is a world-class business. A company can't be a good investment if it's not a good business.

            2.  ❌ **The Value Filter (Inspired by Graham)**
                * **Analogy:** What is the price tag? We evaluate traditional metrics like the **P/E Ratio** and **P/B Ratio** to see if the stock is trading at a "cheap" price.
                * **Result:** **FAIL**. With a P/E of 38.8 and P/B of 58.2, the stock fails the classic Graham deep value test. This isn't a sign of weakness, but of how the market values intangible assets like brand and customer loyalty.

            3.  ❌ **The Safety Margin Test (DCF Analysis)**
                * **Analogy:** Is the price tag a bargain? We run a **Discounted Cash Flow (DCF)** analysis to find the company's true **intrinsic value** and compare it to the current price, seeking a **positive margin of safety**.
                * **Result:** **FAIL**. The stock’s current price is justified only under highly optimistic growth assumptions, leaving **no meaningful margin of safety** for a value investor.

            4.  🧾 **Final Determination:**
                * **Conclusion:** Based on this layered analysis, the AI issues a **NO-BUY** recommendation at current levels. The stock is a **"wonderful business at a non-sensible price."**
            """)

        # --- REFLECTIVE QUOTE ---
        st.markdown("""
        > *“Price is what you pay. Value is what you get.”*  
        > — Warren Buffett
        """)

        # --- HISTORICAL FINANCIALS (IMPROVED) ---
        st.subheader("📊 Historical Performance")
        st.markdown("""
        A look at the company's financial trends is like a **business's medical chart**. It helps us confirm if the business is healthy and if its competitive advantage is holding up over time.
        """)
                
        financials = get_historical_financials(ticker)

        if financials:
            # Create a combined dataframe for charting
            financials_df = pd.DataFrame({
                'Revenue': financials['revenue'],
                'Net Income': financials['net_income'],
                'Free Cash Flow': financials['fcf'],
                'ROE': financials['roe']
            }).sort_index()

            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Combined Chart: Revenue, Net Income, and Free Cash Flow
                fig_inc_fcf = go.Figure()

                # Revenue as a bar chart (light color)
                fig_inc_fcf.add_trace(go.Bar(
                    x=financials_df.index, 
                    y=financials_df['Revenue'], 
                    name='Revenue', 
                    marker_color='#4E84C4',
                    opacity=0.6,
                ))

                # Net Income as a bar chart (darker color)
                fig_inc_fcf.add_trace(go.Bar(
                    x=financials_df.index, 
                    y=financials_df['Net Income'], 
                    name='Net Income', 
                    marker_color='#FFC34D',
                    opacity=0.8,
                ))

                # FCF as a line chart with a different y-axis
                fig_inc_fcf.add_trace(go.Scatter(
                    x=financials_df.index, 
                    y=financials_df['Free Cash Flow'], 
                    mode='lines+markers', 
                    name='Free Cash Flow', 
                    line=dict(color='#047857', width=3), 
                    yaxis='y2'
                ))

                fig_inc_fcf.update_layout(
                    title=f'Revenue, Net Income, and FCF Trend for {ticker.upper()}',
                    barmode='group',
                    xaxis_title='Year',
                    yaxis_title='Amount ($)',
                    yaxis2=dict(
                        title='Free Cash Flow ($)',
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend_title_text='Metric',
                    height=550
                )
                st.plotly_chart(fig_inc_fcf, use_container_width=True)
            
            with col_chart2:
                # Chart: ROE & Debt-to-Equity
                fig_roe = go.Figure()

                # ROE as a line chart
                fig_roe.add_trace(go.Scatter(
                    x=financials_df.index,
                    y=financials_df['ROE'] * 100,
                    mode='lines+markers',
                    name='ROE (%)',
                    line=dict(color='#B91C1C', width=3)
                ))
                
                # Debt-to-Equity as a bar chart (on a different axis)
                fig_roe.add_trace(go.Bar(
                    x=financials_df.index,
                    y=financials['debt_to_equity'],
                    name='Debt-to-Equity',
                    marker_color='#5A5A5A',
                    opacity=0.5,
                    yaxis='y2'
                ))

                fig_roe.update_layout(
                    title=f'Profitability & Financial Health for {ticker.upper()}',
                    xaxis_title='Year',
                    yaxis_title='ROE (%)',
                    yaxis2=dict(
                        title='Debt-to-Equity',
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend_title_text='Metric',
                    height=550
                )
                st.plotly_chart(fig_roe, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📖 Key Observations")
            st.markdown(f"""
            - **Revenue & FCF:** A healthy business should show consistent revenue growth. For a value investor, it's critical that this revenue translates into **Free Cash Flow**—the true "earning power" of a business. Look for a steady, upward trend.
            - **ROE:** This measures how much profit the company generates with shareholder money. A **consistently high ROE** (typically >15-20%) is a hallmark of a high-quality business with a durable competitive advantage.
            - **Financial Health:** We also look at the **Debt-to-Equity** ratio. A low and stable ratio is a sign of financial stability and disciplined management.
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