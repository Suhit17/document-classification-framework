# Stock Analysis CrewAI Implementation
# Simple and clean implementation for stock analysis with buy/hold/sell recommendations

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
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

# Initialize Google Gemini LLM
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    verbose=True
)

# ========================================================================================
# TOOLS DEFINITION
# ========================================================================================

class GetStockDataInput(BaseModel):
    """Input schema for GetStockData."""
    symbol: str = Field(..., description="Stock symbol to analyze")

class GetStockDataTool(BaseTool):
    name: str = "get_stock_data"
    description: str = "Fetch comprehensive stock data using Yahoo Finance. Handles both regular stocks and Indian stocks (.NS suffix)."
    args_schema: Type[BaseModel] = GetStockDataInput

    def _run(self, symbol: str) -> str:
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
            
            # Get financial statements
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
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
                stock_data['1_month_return'] = ((current_price - hist_data['Close'][-30]) / hist_data['Close'][-30] * 100) if len(hist_data) >= 30 else 'N/A'
                stock_data['3_month_return'] = ((current_price - hist_data['Close'][-90]) / hist_data['Close'][-90] * 100) if len(hist_data) >= 90 else 'N/A'
                stock_data['1_year_return'] = ((current_price - hist_data['Close'][-252]) / hist_data['Close'][-252] * 100) if len(hist_data) >= 252 else 'N/A'
            
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

@tool
def search_stock_news(company_name: str, symbol: str, config=None) -> str:
    """
    Search for recent news about the stock using DuckDuckGo.
    Focuses on the past week of news.
    
    Args:
        company_name: Company name to search news for
        symbol: Stock symbol
    """
    try:
        # Create search queries
        queries = [
            f"{company_name} stock news",
            f"{symbol} earnings news",
            f"{company_name} financial news"
        ]
        
        all_news = []
        
        with DDGS() as ddgs:
            for query in queries:
                try:
                    # Search for recent news
                    results = list(ddgs.text(query, max_results=5, region='us-en'))
                    
                    for result in results:
                        news_item = {
                            'title': result.get('title', ''),
                            'body': result.get('body', ''),
                            'url': result.get('href', ''),
                            'source': result.get('href', '').split('/')[2] if result.get('href') else 'Unknown'
                        }
                        all_news.append(news_item)
                    
                    # Small delay between searches
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error with query '{query}': {e}")
                    continue
        
        # Format news output
        if all_news:
            formatted_news = f"""
RECENT NEWS FOR {company_name} ({symbol})
==========================================
"""
            for i, news in enumerate(all_news[:10], 1):  # Limit to top 10 results
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

# ========================================================================================
# AGENTS DEFINITION
# ========================================================================================

# Agent 1: Stock Data Collector
stock_data_collector = Agent(
    role="Financial Data Specialist",
    goal="Gather comprehensive financial data including current stock metrics, historical performance (1-3 years), and detailed financial statements with proper symbol handling for both regular and Indian (.NS) stocks",
    backstory="""You are an experienced financial data analyst who specializes in extracting and organizing 
    stock market data. You have expertise in handling various stock exchanges and ensuring data accuracy 
    across different markets. You're meticulous about data quality and always double-check your sources.""",
    tools=[get_stock_data],
    llm=gemini_llm,
    verbose=True
)

# Agent 2: News Research Analyst
news_research_analyst = Agent(
    role="Market News Intelligence Specialist", 
    goal="Collect and analyze the most relevant news from the past week related to the company, including corporate announcements, industry trends, and market sentiment that could impact stock performance",
    backstory="""You are a seasoned financial journalist with deep expertise in identifying market-moving news. 
    You excel at filtering noise from signal and understanding how news events translate to stock performance. 
    You have a keen eye for spotting trends and understanding market sentiment.""",
    tools=[search_stock_news],
    llm=gemini_llm,
    verbose=True
)

# Agent 3: Fundamental Analysis Expert
fundamental_analyst = Agent(
    role="Comprehensive Financial Analyst",
    goal="Synthesize all collected data into a detailed fundamental analysis covering key metrics like P/E ratios, debt-to-equity, revenue growth, profit margins, ROE, cash flow, and competitive positioning using industry-standard benchmarks",
    backstory="""You are a CFA charterholder with 15+ years of experience in equity research. You specialize 
    in breaking down complex financial data into clear, actionable insights that both professionals and 
    beginners can understand. You're known for your thorough analysis and ability to spot both opportunities and risks.""",
    llm=gemini_llm,
    verbose=True
)

# Agent 4: Investment Decision Advisor
investment_advisor = Agent(
    role="Investment Recommendation Specialist",
    goal="Review the comprehensive analysis and provide a clear BUY/HOLD/SELL recommendation with detailed reasoning, confidence level, and risk assessment in language that's accessible to non-experts",
    backstory="""You are a senior portfolio manager with a track record of successful investment decisions. 
    You excel at translating complex analysis into clear investment guidance and explaining the rationale 
    behind each recommendation. You always consider risk-reward ratios and investment time horizons.""",
    llm=gemini_llm,
    verbose=True
)

# ========================================================================================
# TASKS DEFINITION
# ========================================================================================

def create_stock_analysis_tasks(stock_symbol: str):
    """Create tasks for the stock analysis crew"""
    
    # Task 1: Financial Data Collection
    data_collection_task = Task(
        description=f"""
        Collect comprehensive financial data for stock symbol: {stock_symbol}
        
        Your tasks:
        1. Use the get_stock_data tool to fetch all relevant financial metrics
        2. If the initial symbol fails, the tool will automatically try with .NS suffix for Indian stocks
        3. Gather current stock price, market metrics, financial ratios, and historical performance
        4. Ensure all data is accurate and complete
        5. Format the data clearly for the next agent
        
        Focus on: Current valuation metrics, financial health indicators, growth metrics, and market performance data.
        """,
        agent=stock_data_collector,
        expected_output="A comprehensive dataset with all relevant financial metrics, ratios, and historical performance data formatted clearly for analysis"
    )
    
    # Task 2: News Intelligence Gathering  
    news_collection_task = Task(
        description=f"""
        Gather recent news and market intelligence for the stock: {stock_symbol}
        
        Your tasks:
        1. Use the company name from the previous task to search for relevant news
        2. Focus on news from the past 7 days that could impact stock performance
        3. Look for earnings reports, corporate announcements, analyst opinions, industry trends
        4. Assess overall market sentiment around the company
        5. Identify any potential catalysts or risk factors mentioned in the news
        
        Focus on: Market-moving news, sentiment analysis, and potential impact on stock performance.
        """,
        agent=news_research_analyst,
        expected_output="A comprehensive news summary with key headlines, market sentiment analysis, and assessment of potential impact on stock performance",
        context=[data_collection_task]
    )
    
    # Task 3: Comprehensive Fundamental Analysis
    analysis_task = Task(
        description=f"""
        Create a detailed fundamental analysis for {stock_symbol} using all collected data and news.
        
        Your tasks:
        1. Analyze all financial metrics and ratios from the collected data
        2. Compare key metrics against industry benchmarks and standards
        3. Assess the company's financial health, growth prospects, and valuation
        4. Incorporate recent news and market sentiment into your analysis
        5. Identify key strengths, weaknesses, opportunities, and threats
        6. Write your analysis in clear, accessible language for non-experts
        
        Structure your analysis with these sections:
        - Executive Summary
        - Financial Health Assessment  
        - Valuation Analysis
        - Growth Prospects
        - Recent News Impact
        - Risk Factors
        - Industry Comparison
        
        Make it comprehensive but easy to understand.
        """,
        agent=fundamental_analyst,
        expected_output="A detailed fundamental analysis report with clear sections covering financial health, valuation, growth prospects, news impact, and risk assessment, written in accessible language",
        context=[data_collection_task, news_collection_task]
    )
    
    # Task 4: Investment Recommendation
    recommendation_task = Task(
        description=f"""
        Provide a clear investment recommendation for {stock_symbol} based on the comprehensive analysis.
        
        Your tasks:
        1. Review all previous analysis and data
        2. Synthesize findings into a clear BUY/HOLD/SELL recommendation
        3. Provide your confidence level (High/Medium/Low) and reasoning
        4. Explain the key factors supporting your decision
        5. Identify main risks and potential catalysts
        6. Suggest an appropriate investment time horizon
        7. Write everything in simple terms that a beginner investor can understand
        
        Your final recommendation should include:
        - Clear Decision: BUY/HOLD/SELL
        - Confidence Level: High/Medium/Low  
        - Key Supporting Reasons (3-5 bullet points)
        - Main Risks to Consider
        - Suggested Time Horizon
        - Bottom Line Summary in plain English
        
        Be decisive but honest about uncertainties and risks.
        """,
        agent=investment_advisor,
        expected_output="A clear investment recommendation with decision, confidence level, supporting reasons, risk assessment, and plain-English summary suitable for beginner investors",
        context=[data_collection_task, news_collection_task, analysis_task]
    )
    
    return [data_collection_task, news_collection_task, analysis_task, recommendation_task]

# ========================================================================================
# CREW DEFINITION
# ========================================================================================

def create_stock_analysis_crew(stock_symbol: str):
    """Create and return the stock analysis crew"""
    
    tasks = create_stock_analysis_tasks(stock_symbol)
    
    crew = Crew(
        agents=[stock_data_collector, news_research_analyst, fundamental_analyst, investment_advisor],
        tasks=tasks,
        process=Process.sequential,
        manager_llm=gemini_llm,
        verbose=True
    )
    
    return crew

# ========================================================================================
# MAIN EXECUTION FUNCTION
# ========================================================================================

def analyze_stock(stock_symbol: str):
    """
    Main function to run the stock analysis crew
    
    Args:
        stock_symbol (str): Stock symbol to analyze (e.g., 'AAPL', 'RELIANCE', 'TCS')
    
    Returns:
        str: Complete analysis and recommendation
    """
    
    print(f"\nStarting Stock Analysis for: {stock_symbol}")
    print("="*50)
    
    try:
        # Create the crew
        crew = create_stock_analysis_crew(stock_symbol)
        
        # Execute the analysis
        result = crew.kickoff()
        
        print(f"\nAnalysis Complete for {stock_symbol}")
        print("="*50)
        
        return result
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        print(error_msg)
        return error_msg

# ========================================================================================
# EXAMPLE USAGE
# ========================================================================================

if __name__ == "__main__":
    # Example usage - replace with your desired stock symbol
    stock_symbol = "NVDA"  # Try "TCS" for Indian stock, "GOOGL" for US stock
    
    # Run the analysis
    analysis_result = analyze_stock(stock_symbol)
    
    print("\n" + "="*80)
    print("FINAL ANALYSIS RESULT")
    print("="*80)
    print(analysis_result)