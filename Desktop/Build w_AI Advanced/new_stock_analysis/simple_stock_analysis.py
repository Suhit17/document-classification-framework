# Simple Stock Analysis Implementation
# Streamlined version without CrewAI compatibility issues

from langchain_google_genai import ChatGoogleGenerativeAI
import yfinance as yf
from duckduckgo_search import DDGS
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_stock_data(symbol: str) -> str:
    """
    Fetch comprehensive stock data using Yahoo Finance.
    Handles both regular stocks and Indian stocks (.NS suffix).
    
    Args:
        symbol: Stock symbol to analyze
    """
    def try_fetch_stock(ticker_symbol):
        try:
            stock = yf.Ticker(ticker_symbol)
            
            # Get basic info
            info = stock.info
            
            # Get historical data (3 years)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3*365)
            hist_data = stock.history(start=start_date, end=end_date)
            
            # Compile key metrics
            current_price = hist_data['Close'][-1] if not hist_data.empty else info.get('currentPrice', 'N/A')
            
            stock_data = {
                'symbol': ticker_symbol,
                'company_name': info.get('longName', 'N/A'),
                'current_price': current_price,
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('forwardPE', info.get('trailingPE', 'N/A')),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'roe': info.get('returnOnEquity', 'N/A'),
                'profit_margin': info.get('profitMargins', 'N/A'),
                'revenue_growth': info.get('revenueGrowth', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'volume': info.get('volume', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
            }
            
            # Add recent performance
            if not hist_data.empty:
                try:
                    stock_data['1_month_return'] = f"{((current_price - hist_data['Close'][-30]) / hist_data['Close'][-30] * 100):.2f}" if len(hist_data) >= 30 else 'N/A'
                    stock_data['3_month_return'] = f"{((current_price - hist_data['Close'][-90]) / hist_data['Close'][-90] * 100):.2f}" if len(hist_data) >= 90 else 'N/A'
                    stock_data['1_year_return'] = f"{((current_price - hist_data['Close'][-252]) / hist_data['Close'][-252] * 100):.2f}" if len(hist_data) >= 252 else 'N/A'
                except:
                    stock_data['1_month_return'] = 'N/A'
                    stock_data['3_month_return'] = 'N/A'
                    stock_data['1_year_return'] = 'N/A'
            
            return stock_data, True
            
        except Exception as e:
            return f"Error fetching {ticker_symbol}: {str(e)}", False
    
    # Try original symbol first
    result, success = try_fetch_stock(symbol)
    
    # If failed and symbol doesn't already have .NS, try with .NS
    if not success and not symbol.endswith('.NS'):
        print(f"Trying {symbol}.NS for Indian stock...")
        result, success = try_fetch_stock(f"{symbol}.NS")
        
    if success:
        # Format the data nicely
        data = result
        formatted_output = f"""
STOCK DATA FOR {data['symbol']}
===============================
Company: {data['company_name']}
Sector: {data['sector']} | Industry: {data['industry']}

CURRENT METRICS:
- Current Price: ${data['current_price']}
- Market Cap: {data['market_cap']}
- P/E Ratio: {data['pe_ratio']}
- Price to Book: {data['price_to_book']}
- Beta: {data['beta']}

FINANCIAL HEALTH:
- Debt to Equity: {data['debt_to_equity']}
- Return on Equity: {data['roe']}
- Profit Margin: {data['profit_margin']}
- Revenue Growth: {data['revenue_growth']}
- Dividend Yield: {data['dividend_yield']}

PERFORMANCE:
- 52 Week High: ${data['52_week_high']}
- 52 Week Low: ${data['52_week_low']}
- 1 Month Return: {data['1_month_return']}%
- 3 Month Return: {data['3_month_return']}%
- 1 Year Return: {data['1_year_return']}%

TRADING DATA:
- Volume: {data['volume']}
- Average Volume: {data['avg_volume']}
        """
        return formatted_output
    else:
        return result

def search_stock_news(company_name: str, symbol: str) -> str:
    """
    Search for recent news about the stock using DuckDuckGo.
    """
    try:
        queries = [
            f"{company_name} stock news",
            f"{symbol} earnings news", 
            f"{company_name} financial news"
        ]
        
        all_news = []
        
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = list(ddgs.text(query, max_results=3, region='us-en'))
                    
                    for result in results:
                        news_item = {
                            'title': result.get('title', ''),
                            'body': result.get('body', ''),
                            'url': result.get('href', ''),
                            'source': result.get('href', '').split('/')[2] if result.get('href') else 'Unknown'
                        }
                        all_news.append(news_item)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error with query '{query}': {e}")
                    continue
        
        if all_news:
            formatted_news = f"""
RECENT NEWS FOR {company_name} ({symbol})
==========================================
"""
            for i, news in enumerate(all_news[:8], 1):
                formatted_news += f"""
{i}. {news['title']}
   Source: {news['source']}
   Summary: {news['body'][:200]}...
   URL: {news['url']}
   
"""
            return formatted_news
        else:
            return f"No recent news found for {company_name} ({symbol})"
            
    except Exception as e:
        return f"Error searching for news: {str(e)}"

def analyze_stock_simple(stock_symbol: str) -> str:
    """
    Simple stock analysis without CrewAI - direct LLM analysis
    
    Args:
        stock_symbol (str): Stock symbol to analyze
    
    Returns:
        str: Complete analysis and recommendation
    """
    print(f"\nStarting Simple Stock Analysis for: {stock_symbol}")
    print("="*50)
    
    try:
        # Initialize Google Gemini LLM
        gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
        
        # Step 1: Get stock data
        print("Fetching stock data...")
        stock_data = get_stock_data(stock_symbol)
        
        # Step 2: Get news data
        print("Searching for recent news...")
        # Extract company name from stock data for news search
        company_name = stock_symbol
        if "Company:" in stock_data:
            try:
                company_name = stock_data.split("Company: ")[1].split("\n")[0]
            except:
                company_name = stock_symbol
        
        news_data = search_stock_news(company_name, stock_symbol)
        
        # Step 3: Create comprehensive analysis prompt
        analysis_prompt = f"""
You are a senior financial analyst. Please provide a comprehensive stock analysis for {stock_symbol} based on the following data:

STOCK DATA:
{stock_data}

NEWS DATA:
{news_data}

Please provide:

1. **EXECUTIVE SUMMARY** (2-3 sentences about the company and current situation)

2. **FINANCIAL HEALTH ASSESSMENT** 
   - Analyze key metrics (P/E, debt-to-equity, ROE, profit margins, etc.)
   - Compare to industry standards where possible
   - Rate financial health: Excellent/Good/Fair/Poor

3. **VALUATION ANALYSIS**
   - Is the stock overvalued, fairly valued, or undervalued?
   - Key valuation metrics analysis
   
4. **RECENT NEWS IMPACT**
   - How recent news affects the stock outlook
   - Market sentiment analysis

5. **INVESTMENT RECOMMENDATION**
   - Clear decision: **BUY** / **HOLD** / **SELL**
   - Confidence level: High/Medium/Low
   - 3-5 key reasons supporting your recommendation
   - Main risks to consider
   - Suggested time horizon (short/medium/long term)

6. **BOTTOM LINE** (1-2 sentences in plain English for beginner investors)

Make your analysis clear, actionable, and accessible to both beginners and experienced investors. Be honest about uncertainties and risks.
"""
        
        print("Generating AI analysis...")
        # Get LLM analysis
        response = gemini_llm.invoke(analysis_prompt)
        analysis_result = response.content if hasattr(response, 'content') else str(response)
        
        print(f"\nAnalysis Complete for {stock_symbol}")
        print("="*50)
        
        return analysis_result
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        print(error_msg)
        return error_msg

# Example usage
if __name__ == "__main__":
    stock_symbol = "NVDA"
    analysis_result = analyze_stock_simple(stock_symbol)
    
    print("\n" + "="*80)
    print("FINAL ANALYSIS RESULT")
    print("="*80)
    print(analysis_result)