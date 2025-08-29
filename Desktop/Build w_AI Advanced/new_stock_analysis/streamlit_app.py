import streamlit as st
import sys
import os

st.set_page_config(
    page_title="Stock Analysis AI",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI-Powered Stock Analysis")
st.markdown("Get comprehensive stock analysis with buy/hold/sell recommendations powered by CrewAI")

# Sidebar for inputs
st.sidebar.header("API Configuration")

# API Key input
api_key = st.sidebar.text_input(
    "Google API Key", 
    type="password",
    help="Enter your Google Gemini API key",
    placeholder="Enter your Google API key here..."
)

st.sidebar.markdown("---")
st.sidebar.header("Stock Analysis Settings")

# Stock symbol input
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol", 
    value="NVDA",
    help="Enter stock symbol (e.g., AAPL, GOOGL, TCS for Indian stocks)"
).upper().strip()

# Analysis button
analyze_button = st.sidebar.button("🔍 Analyze Stock", type="primary")

# Main content area
if analyze_button and stock_symbol:
    if not api_key:
        st.error("⚠️ Please enter your Google API Key in the sidebar to proceed.")
        st.info("You can get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
    else:
        st.header(f"Analysis for {stock_symbol}")
        
        # Show loading spinner
        with st.spinner(f"Analyzing {stock_symbol}... This may take a few minutes."):
            try:
                # Set the API key as environment variable temporarily
                os.environ['GOOGLE_API_KEY'] = api_key
                
                # Import and run the simple stock analysis
                from simple_stock_analysis import analyze_stock_simple
                result = analyze_stock_simple(stock_symbol)
                
                # Display results
                st.success("Analysis Complete!")
                
                # Display the analysis result in an expandable section
                with st.expander("📊 Complete Analysis Report", expanded=True):
                    st.markdown(result)
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.info("Please check your API key, dependencies, and internet connection.")
                
                # Show more detailed error info
                with st.expander("Error Details"):
                    st.code(str(e))
            finally:
                # Clean up the environment variable
                if 'GOOGLE_API_KEY' in os.environ:
                    del os.environ['GOOGLE_API_KEY']

elif not stock_symbol and analyze_button:
    st.warning("Please enter a stock symbol to analyze.")

# Instructions
if not analyze_button:
    st.markdown("""
    ## How to Use
    
    1. **Enter a stock symbol** in the sidebar (e.g., AAPL, GOOGL, TCS)
    2. **Click "Analyze Stock"** to start the analysis
    3. **Wait for the AI crew** to complete the analysis (this may take a few minutes)
    4. **Review the comprehensive report** with buy/hold/sell recommendation
    
    ## Features
    
    - 📊 **Financial Data Analysis**: Current metrics, ratios, and historical performance
    - 📰 **News Intelligence**: Recent news and market sentiment analysis  
    - 🔍 **Fundamental Analysis**: Comprehensive financial health assessment
    - 💡 **Investment Recommendation**: Clear buy/hold/sell advice with reasoning
    
    ## Supported Markets
    
    - **US Stocks**: AAPL, GOOGL, MSFT, TSLA, etc.
    - **Indian Stocks**: TCS, RELIANCE, INFY (automatically adds .NS suffix)
    
    ## Requirements
    
    1. **Google API Key**: Enter your Google Gemini API key in the sidebar
       - Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
       - The API key is used only for this session and not stored
    
    ## Dependencies
    
    If you encounter errors, you may need to install or update:
    ```bash
    pip install crewai crewai-tools langchain-google-genai yfinance duckduckgo-search streamlit python-dotenv
    ```
    """)

# Footer
st.markdown("---")
st.markdown("*Powered by CrewAI and Google Gemini*")