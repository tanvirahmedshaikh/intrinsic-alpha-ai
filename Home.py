import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IntrinsicAlpha AI",
    page_icon="📈",
    layout="wide"
)

# --- Custom CSS for a modern SaaS feel ---
st.markdown("""
<style>
    .hero-section {
        padding: 6rem 2rem;
        text-align: center;
        background: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .hero-section h1 {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.2;
        color: #1a1a1a;
    }
    .hero-section p {
        font-size: 1.5rem;
        color: #4a5568;
        max-width: 700px;
        margin: 1rem auto;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    .feature-card {
        background: #fff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
with st.container():
    st.markdown("""
    <div class="hero-section">
        <h1>IntrinsicAlpha AI: The New Standard for Value Investing</h1>
        <p>Stop overpaying for stocks! This isn't just another finance app; it's your personal AI co-pilot, designed to help you find undervalued gems. We combine the wisdom of Graham and Buffett with the power of modern AI, and our mission is to make you a more confident, data-driven investor.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Start Analyzing", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Stock_Insight.py")

st.divider()

# --- CORE FEATURES SECTION ---
with st.container():
    st.header("Why IntrinsicAlpha AI Stands Out?")
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
    
    # Feature 1: Explainable AI
    st.markdown("""
    <div class="feature-card">
        <h3>Explainable AI & Transparent Reasoning</h3>
        <p>You don't just get a buy/sell signal; you see exactly why. Our dashboards visualize key factors and simplify the complex logic, so you can learn and build conviction with every analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature 2: Grounded in Timeless Principles
    st.markdown("""
    <div class="feature-card">
        <h3>Grounded in Timeless Principles</h3>
        <p>Our AI agents are embedded with the philosophies of Benjamin Graham and Warren Buffett to find companies with a significant margin of safety and a durable business moat.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature 3: Actionable, Portfolio-Aware Guidance
    st.markdown("""
    <div class="feature-card">
        <h3>Actionable, Portfolio-Aware Guidance</h3>
        <p>We go beyond basic analysis to provide practical advice, helping you answer the most critical questions: "Is this a good fit for my portfolio?" and "How much should I invest?"</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature 4: An Agentic AI Crew
    st.markdown("""
    <div class="feature-card">
        <h3>An Agentic AI Crew</h3>
        <p>Powered by a modular, multi-agent system, our AI can handle a multi-step analysis just like a human investor. It can pull qualitative and quantitative signals and monitor its own performance.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- FINAL CTA SECTION ---
with st.container():
    st.markdown("""
    <div class="hero-section">
        <h2>Ready to Invest with Conviction?</h2>
        <p>Stop overpaying for stocks. Let our AI help you find great companies at wonderful prices.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Get Started Now", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Stock_Insight.py")

# --- FOOTER ---
st.markdown("""
<br>
<div style="text-align: center; color: #718096;">
    <p>Disclaimer: This is a prototype and not financial advice. All data is for illustrative purposes only.</p>
    <p>
        <a href="https://github.com/your-username/your-repo" target="_blank">
            <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge" />
        </a>
    </p>
</div>
""", unsafe_allow_html=True)