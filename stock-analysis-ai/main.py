"""
Main FastAPI Application
Stock Technical Analysis AI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Stock Technical Analysis AI",
    description="AI-powered technical analysis for Indian NSE stocks",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    
class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


# Health Check Endpoint
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Stock Technical Analysis AI Backend is running"
    }


@app.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "status": "ok",
        "services": {
            "data_fetcher": "operational",
            "indicators": "operational",
            "chart_generator": "operational"
        }
    }


# Stock Info Endpoint
@app.get("/api/stock/{symbol}")
async def get_stock_info(symbol: str):
    """Get basic stock information"""
    try:
        from src.services.data_fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        info = fetcher.get_stock_info(symbol.upper())
        
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Quick Data Fetch Endpoint
@app.get("/api/data/{symbol}/{timeframe}")
async def get_stock_data(symbol: str, timeframe: str = "1d"):
    """Fetch stock OHLCV data"""
    try:
        from src.services.data_fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        df = fetcher.fetch_live_data(symbol.upper(), timeframe=timeframe)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Convert to JSON-serializable format
        data = df.tail(100).reset_index().to_dict(orient='records')
        
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "candles": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Technical Analysis Endpoint (Phase 1 - Basic)
@app.post("/api/analyze")
async def analyze_stock(request: AnalysisRequest):
    """
    Perform technical analysis on a stock
    This is the Phase 1 version - returns calculated indicators
    Phase 2 will integrate CrewAI agents
    """
    try:
        from src.services.data_fetcher import StockDataFetcher
        from src.services.technical_indicators import TechnicalIndicators
        from src.services.chart_generator import ChartGenerator
        
        symbol = request.symbol.upper()
        timeframe = request.timeframe
        
        # Fetch data
        fetcher = StockDataFetcher()
        df = fetcher.fetch_live_data(symbol, timeframe=timeframe)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate indicators
        calc = TechnicalIndicators(df)
        indicators = calc.calculate_all()
        df_enriched = calc.get_enriched_dataframe()
        
        # Generate chart
        stock_info = fetcher.get_stock_info(symbol)
        chart_gen = ChartGenerator()
        chart_path = chart_gen.generate_comprehensive_chart(
            df_enriched,
            indicators,
            symbol,
            timeframe,
            stock_info
        )
        
        # Get latest values
        latest_data = calc.get_latest_values()
        
        # Return analysis
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "stock_info": stock_info,
            "latest_candle": {
                "timestamp": latest_data['timestamp'],
                "open": latest_data['open'],
                "high": latest_data['high'],
                "low": latest_data['low'],
                "close": latest_data['close'],
                "volume": latest_data['volume'],
            },
            "indicators": indicators,
            "chart_path": chart_path,
            "status": "completed",
            "note": "Phase 1: Basic analysis. Phase 2 will add AI agent insights."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chart Image Endpoint
@app.get("/api/chart/{filename}")
async def get_chart(filename: str):
    """Serve generated chart images"""
    chart_dir = os.getenv("CHART_OUTPUT_DIR", "/home/claude/stock-analysis-ai/backend/charts")
    filepath = os.path.join(chart_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Chart not found")
    
    return FileResponse(filepath, media_type="image/png")


# Supported Stocks Endpoint
@app.get("/api/stocks/nifty50")
async def get_nifty50_symbols():
    """Get list of Nifty 50 stock symbols"""
    nifty50 = [
        "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE",
        "BAJAJFINSV", "BHARTIARTL", "BPCL", "BRITANNIA", "CIPLA",
        "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "GRASIM",
        "HCLTECH", "HDFC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
        "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY",
        "ITC", "JSWSTEEL", "KOTAKBANK", "LT", "M&M",
        "MARUTI", "NESTLEIND", "NTPC", "ONGC", "POWERGRID",
        "RELIANCE", "SBILIFE", "SBIN", "SHREECEM", "SUNPHARMA",
        "TATAMOTORS", "TATASTEEL", "TCS", "TECHM", "TITAN",
        "ULTRACEMCO", "UPL", "WIPRO"
    ]
    
    return {
        "index": "Nifty 50",
        "count": len(nifty50),
        "symbols": nifty50
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
