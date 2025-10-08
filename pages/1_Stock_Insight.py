import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
import time
import datetime
import plotly.graph_objects as go
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IntrinsicAlpha AI",
    page_icon="📈",
    layout="wide"
)

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

        # Custom CSS for smaller font size and a more compact layout
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
            {"label": "Volume", "value": format_large_number(metrics_data.get('Volume')), "help": "The total number of shares of a security that have been traded during a given period."},
            {"label": "Market Cap", "value": format_large_number(metrics_data.get('Market Cap')), "help": "The total value of a company’s outstanding shares. Used to determine a company's size."},
            {"label": "P/B Ratio", "value": metrics_data.get('P/B Ratio'), "help": "The Price-to-Book (P/B) ratio compares a stock's price to the company's net asset value...", "format": ".2f"},
            {"label": "Debt-to-Equity Ratio", "value": metrics_data.get('Debt-to-Equity Ratio'), "help": "A low Debt-to-Equity ratio (ideally below 1) is a sign of a financially strong company, which is crucial for stability.", "format": ".2f"},
            {"label": "P/E Ratio (TTM)", "value": metrics_data.get('PE Ratio (TTM)'), "help": "The P/E Ratio (Price-to-Earnings) is a key valuation metric that compares a company's current stock price to its earnings.", "format": ".2f"},
            {"label": "P/E vs. Historical Avg (5Y)", "value": hist_metrics.get('Historical PE Avg (5Y)'), "help": "This compares the current P/E to its 5-year historical average. A P/E below its historical average can indicate the stock is undervalued.", "format": ".2f"},
            {"label": "EPS (TTM)", "value": metrics_data.get('EPS (TTM)'), "help": "Earnings Per Share (TTM) is the company's profit allocated to each outstanding share over the last 12 months.", "format": ".2f"},
            {"label": "Avg. Volume", "value": format_large_number(metrics_data.get('Avg. Volume')), "help": "The average daily trading volume over a specified period. High volume can indicate strong investor interest."},
            {"label": "Current ROA", "value": hist_metrics.get('Current ROA'), "help": "Return on Assets (ROA) measures how efficiently a company uses its assets to generate earnings. A higher ROA is generally better.", "format": ".1f", "suffix": "%"},
            {"label": "Historical ROA Avg (5Y)", "value": hist_metrics.get('Historical ROA Avg (5Y)'), "help": "Historical Return on Assets shows how a company's efficiency has changed over time.", "format": ".1f", "suffix": "%"},
            {"label": "Current Div Yield", "value": metrics_data.get('Current Dividend Yield'), "help": "The dividend yield shows the return on your investment from dividends alone.", "format": ".2f", "suffix": "%"},
            {"label": "Historical Div Yield Avg (5Y)", "value": hist_metrics.get('Historical Dividend Yield Avg (5Y)'), "help": "The average dividend yield over the last 5 years. A current yield above the historical average may indicate an opportunity.", "format": ".2f", "suffix": "%"}
        ]

        total_metrics = len(all_metrics)
        # Calculate the number of metrics per column
        metrics_per_col = total_metrics // 3
        remainder = total_metrics % 3

        # Distribute metrics evenly
        col1_metrics = all_metrics[:metrics_per_col + (1 if remainder > 0 else 0)]
        col2_metrics = all_metrics[len(col1_metrics):len(col1_metrics) + metrics_per_col + (1 if remainder > 1 else 0)]
        col3_metrics = all_metrics[len(col1_metrics) + len(col2_metrics):]

        # Create columns for metrics and the summary
        col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.2, 0.4])

        # Display metrics in each column
        with col1:
            for m in col1_metrics:
                value_to_display = m.get('value')
                if m.get('format'):
                    try:
                        if value_to_display is not None:
                            value_to_display = f"{value_to_display:{m['format']}}"
                    except (ValueError, TypeError):
                        value_to_display = 'N/A'
                
                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']
                    
                st.metric(label=m['label'], value=value_to_display, help=m['help'])

        with col2:
            for m in col2_metrics:
                value_to_display = m.get('value')
                if m.get('format'):
                    try:
                        if value_to_display is not None:
                            value_to_display = f"{value_to_display:{m['format']}}"
                    except (ValueError, TypeError):
                        value_to_display = 'N/A'
                
                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']

                st.metric(label=m['label'], value=value_to_display, help=m['help'])

        with col3:
            for m in col3_metrics:
                value_to_display = m.get('value')
                if m.get('format'):
                    try:
                        if value_to_display is not None:
                            value_to_display = f"{value_to_display:{m['format']}}"
                    except (ValueError, TypeError):
                        value_to_display = 'N/A'
                
                if 'suffix' in m and value_to_display != 'N/A':
                    value_to_display += m['suffix']

                st.metric(label=m['label'], value=value_to_display, help=m['help'])
        
        with col4:
            st.markdown(
                """
                <h3 style="margin-top: -5px; margin-bottom: 10px;">The Big Picture</h3>
                """,
                unsafe_allow_html=True
            )

            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 8px; height: 100%;">
                <p>Our analysis on Apple (AAPL) indicates a mixed picture. While it is a high-quality business with a strong competitive advantage (moat), its current valuation metrics—like a P/E ratio of {metrics_data.get('PE Ratio (TTM)', 'N/A'):.2f} and a P/B ratio of {metrics_data.get('P/B Ratio', 'N/A'):.2f}—are significantly higher than what a traditional value investor would look for. However, the company's strong historical performance and high ROA suggest a very efficient business. This means the market is placing a high value on future growth and brand, rather than just the balance sheet. For an investor focused on a significant margin of safety, this stock may not present a compelling opportunity at its current price.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")

        # --- VALUATION DASHBOARD ---
        st.subheader("Intrinsic Value & Margin of Safety")
        val_data = generate_valuation_data()
        
        val_col1, val_col2, val_col3 = st.columns(3)
        with val_col1:
            last_price = stock_data_tf['Close'].iloc[-1]
            st.metric("Current Price", f"${last_price:.2f}")
        with val_col2:
            st.metric("Intrinsic Value", f"${val_data['Intrinsic Value']:.2f}")
        with val_col3:
            st.metric("Margin of Safety", f"{val_data['Margin of Safety (%)']:.2f}%")

        st.info("The margin of safety is your cushion against risk. It is the difference between a stock’s current price and our conservative estimate of its intrinsic value. A larger margin of safety means a more secure investment.")

        st.markdown("---")

        # --- EXPLAINABILITY & REASONING ---
        st.subheader("Explainable AI: The Reasoning Behind the Analysis")
        st.markdown("Our AI breaks down its recommendation based on timeless value investing principles.")
        
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 8px;">
            <p><strong><font size='+1'>AI Summary:</font></strong> Our analysis on Apple (AAPL) indicates that while the stock is a high-quality business with a strong competitive advantage, its current valuation metrics—like a P/E ratio of 38.89—are significantly higher than the benchmarks favored by value investors. This suggests the market is pricing in substantial future growth. For an investor focused on a significant margin of safety, this stock may not present a compelling opportunity at its current price.</p>
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
                - **Durable Business Moat:** Apple's powerful brand, closed ecosystem, and loyal customer base give it a significant moat, which is a key reason its value is high despite a high P/E ratio.
                - **Earnings Power & Stability:** The company's consistent, growing earnings show a healthy and expanding business, aligning with Ben Graham's search for a proven track record.
                - **Management Quality:** Tim Cook's management has successfully grown the company's services segment, demonstrating a key qualitative factor that contributes to its long-term value.
                - **P/E Ratio:** While the P/E ratio of 38.89 is high for a typical value stock, our analysis takes into account the company's growth and moat, which justifies a higher multiple.
                - **Debt-to-Equity Ratio:** We'd also consider the company's balance sheet to ensure it has a low debt-to-equity ratio, which is crucial for financial stability and fits with the principles of security analysis.
                """)
        
        st.markdown("---")

        # --- DECISION-MAKING FLOW ---
        st.subheader("AI Decision-Making Flow")
        with st.container(border=True):
            st.markdown("""
            1.  **Quantitative Foundation:** The AI first analyzes key financial metrics like **earnings, debt, and assets** to establish a baseline of the company's financial health.
            2.  **Qualitative Moat Assessment:** It then assesses the company's **business moat** by looking at factors like its brand, management quality, and competitive landscape.
            3.  **Intrinsic Value Calculation:** Using a blended model that accounts for both quantitative financials and qualitative moats, the AI calculates a conservative estimate of the company's **intrinsic value**.
            4.  **Margin of Safety Check:** Finally, it compares the calculated intrinsic value to the current market price to determine the **margin of safety**, which is the core driver of the final recommendation.
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