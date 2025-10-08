# 🚀 IntrinsicAlpha AI: The New Standard for Value Investing

This isn't just another stock analysis app. It's an **AI co-pilot** designed for the modern value investor, someone who sees a stock not as a ticker symbol but as a piece of a business. If you believe the best way to invest is to buy a great company for less than it's worth, this is your platform. Think of it like buying high quality clothes at a deep sale; our app helps you find those same opportunities in the stock market.

---
## ✨ Core Features

* **Explainable AI & Transparent Reasoning:** We pull back the curtain on the AI's decision-making process. You don't just get a buy/sell signal; you see **exactly why**. Our dashboards visualize key factors and simplify the complex logic, so you can learn and build conviction with every analysis.
* **Grounded in Timeless Principles:** Our AI agents aren't chasing fleeting trends. They are embedded with the philosophies of **Benjamin Graham** and **Warren Buffett**. This app is built to find companies with a significant **margin of safety**, a durable **business moat**, and a proven track record of value.
* **Actionable, Portfolio-Aware Guidance:** We go beyond basic analysis to provide practical advice. Our platform helps answer the most critical questions: "Is this a good fit for my portfolio?" and "How much should I invest?" This is personalized, actionable guidance—not just a recommendation.
* **An Agentic AI Crew:** Powered by a modular, multi-agent system, our AI can handle a multi-step analysis just like a human investor. It can pull qualitative and quantitative signals, detect anomalies, and monitor its own performance, ensuring the insights you receive are robust and reliable.


## 3 Tabs:

* **Stock Insight Tab:** Analyze one stock per chat session. The AI provides a recommendation (buy/sell/hold) along with key explanations, including feature importance, the underlying model logic, and a risk profile. Dashboards dynamically update with each response.
* **AI System Monitor Tab:** A dedicated dashboard for monitoring the AI infrastructure itself. This provides transparency by displaying fake but realistic data on agent performance, such as response times, successful runs, and potential drift warnings.p
* **Intuitive Interface:** A modern, SaaS-style UI that mimics a chat application, featuring a navigation sidebar, dynamic dashboards, and a clean, responsive layout.

---
## 💻 Tech Stack

* **Frontend/UI:** [Streamlit](https://streamlit.io/)
* **AI Framework:** Will integrate a multi-agent system (like CrewAI) later.
* **LLMs:** [Groq Llama 3](https://groq.com/) & [Google Gemini](https://ai.google.dev/)
* **Charts:** Streamlit, [Plotly](https://plotly.com/), or [Matplotlib](https://matplotlib.org/)
* **Data:** Fake, simulated data for this prototype.

---
## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* **Python 3.11:** The application is built and tested with Python 3.11.
* **API Keys:** You will need API keys from both Google AI Studio and GroqCloud to enable the LLM functionality in the future.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/ai-stock-insight-app.git](https://github.com/your-username/ai-stock-insight-app.git)
    cd ai-stock-insight-app
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python3.11 -m venv .venv
    # On macOS/Linux
    source .venv/bin/activate
    # On Windows
    .\.venv\Scripts\activate
    ```
3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    * Create a file named `.env` in the root of your project directory.
    * Add your API keys to the `.env` file (these will be used later):
        ```env
        GEMINI_API_KEY="your_google_api_key_here"
        GROQ_API_KEY="your_groq_api_key_here"
        ```

---
## 📖 Usage

With your virtual environment active, run the following command in your terminal:

```sh
streamlit run Home.py
```

## Navigating the App
The application is structured into three main pages:

* **🏠 Home:** The landing page with a modern hero section and feature highlights.

* **📈 Stock Insight:** The main workspace where you can chat with the AI and view the interactive
dashboards.

* **🧠 AI System Monitor:** A separate page to monitor the performance of the AI's internal agents.