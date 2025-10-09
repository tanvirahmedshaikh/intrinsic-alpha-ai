import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
        st.subheader("Intrinsic Value & Margin of Safety")

        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 8px;">
            <p><strong><font size='+1'>Investment Conclusion:</font></strong> Our analysis concludes that AAPL is a **"Wonderful Business at a Non-Sensible Price."** The company is high-quality, but its current market price is only justified by highly aggressive growth forecasts, leaving no Margin of Safety for the investor.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### DCF Intrinsic Value Analysis")
        # Creating a table to show different valuation scenarios
        valuation_data = {
            "Valuation Case": ["Conservative Case", "Base Case", "Aggressive Case (LLM Premium)"],
            "Key Assumptions": [
                "High WACC, conservative FCF margin",
                "WACC 8.0%, consensus FCF projections",
                "Low WACC, high FCF ramp-up (AI demand)"
            ],
            "Intrinsic Value": [142.00, 193.00, 287.00],
            "Current Price (≈$256)": [256.00, 256.00, 256.00],
            "Margin of Safety (%)": [-44.4, -24.6, 12.1]
        }
        
        valuation_df = pd.DataFrame(valuation_data)
        st.dataframe(valuation_df, use_container_width=True)
        
        st.info("The table above shows that AAPL is significantly overvalued under a conservative or base-case analysis. A positive Margin of Safety only exists in the most aggressive, speculative scenario.")
        
        st.markdown("---")
        
        st.markdown("### Target Buy Price")
        st.markdown("To purchase this stock with a protective Margin of Safety, an investor must wait for the price to drop to a level supported by a conservative valuation.")
        
        # Mock calculation for target buy price
        base_case_intrinsic_value = 193.00
        desired_margin_of_safety = 0.15 # 15%
        target_buy_price = base_case_intrinsic_value * (1 - desired_margin_of_safety)
        
        val_col1, val_col2, val_col3 = st.columns(3)
        with val_col1:
            st.metric("Base Case Intrinsic Value", f"${base_case_intrinsic_value:.2f}")
        with val_col2:
            st.metric("Desired Margin of Safety", f"{desired_margin_of_safety:.0%}")
        with val_col3:
            st.metric("Target Buy Price", f"${target_buy_price:.2f}")

        st.markdown("---")

        # --- EXPLAINABILITY & REASONING ---
        st.subheader("Explainable AI: The Reasoning Behind the Analysis")
        st.markdown("Our AI breaks down its recommendation based on timeless value investing principles.")
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 8px;">
            <p><strong><font size='+1'>AI Summary:</font></strong> Our analysis concludes that AAPL is a **"Wonderful Business at a Non-Sensible Price."** The company is high-quality, but its current market price is only justified by highly aggressive growth forecasts, leaving no Margin of Safety for the investor.</p>
        </div>
        """, unsafe_allow_html=True)
        
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.markdown("#### Feature Importance")
            importance_df = generate_feature_importance_data()
            
            fig_importance = px.bar(
                importance_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title="What Drives the Decision?",
                labels={'Importance': 'Relative Importance (%)', 'Feature': 'Feature'},
                color_discrete_sequence=['#4299E1']
            )
            st.plotly_chart(fig_importance, use_container_width=True)

        with exp_col2:
            st.markdown("#### The Story Behind the Data")
            with st.container(border=True):
                st.markdown("""
                - **The Graham Number:** Under strict Graham screening, AAPL's high P/E of 38.82 and P/B of 58.21 lead to a quantitative failure. This is due to the structural obsolescence of P/B for tech companies with high intangible assets.
                - **Buffett's Mandate:** However, the company passes the Buffett quality screen with a "Wide Economic Moat" built on its ecosystem and brand, as well as an exceptional Return on Equity (ROE) of 154.9%.
                - **Moat Resilience & AI:** The AI recognizes that Apple’s high market valuation is a premium based on investor optimism around future AI/LLM integration.
                - **DCF Analysis:** Our discounted cash flow (DCF) models show that the current price is only justified under highly aggressive growth scenarios, which eliminates any protective buffer for the investor.
                """)
        
        st.markdown("---")

        # --- DECISION-MAKING FLOW ---
        st.subheader("AI Decision-Making Flow")
        st.markdown("The AI uses a four-layered value framework to make a final determination.")
        with st.container(border=True):
            st.markdown("""
            1.  **Quality Screen (Buffett):** The AI first checks for a durable **Economic Moat** and high **Capital Efficiency** (ROE/ROIC). **Result:** Pass.
            2.  **Growth-Adjusted Value (Adapted Graham):** It then calculates the **PEG Ratio** to ensure the valuation is not overextended relative to growth. **Result:** Fail (PEG is too high).
            3.  **Final Safety Margin (Buffett/Graham):** The AI performs a **DCF Analysis** to confirm a tangible Margin of Safety. **Result:** Fail (MOS is negative under conservative and base-case assumptions).
            4.  **Final Determination:** Based on these results, the AI provides a definitive **NO-BUY** recommendation at the current price, as it lacks a protective safety buffer.
            """)
            
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