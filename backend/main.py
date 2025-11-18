"""
Main FastAPI Application
Stock Technical Analysis AI Backend
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
#backend_dir = Path(__file__).parent
backend_dir = Path(__file__)
sys.path.insert(0, str(backend_dir))
#sys.path.append('/workspaces/Stock-Chart-Analysis-AI-Agent/backend')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import traceback

# Import serialization utilities
from src.utils.serialization import sanitize_response

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
    """API health check with import verification"""
    import_status = {}
    
    try:
        from src.services.data_fetcher import StockDataFetcher
        import_status['data_fetcher'] = 'ok'
    except Exception as e:
        import_status['data_fetcher'] = f'error: {str(e)}'
    
    try:
        from src.services.technical_indicators import TechnicalIndicators
        import_status['indicators'] = 'ok'
    except Exception as e:
        import_status['indicators'] = f'error: {str(e)}'
    
    try:
        from src.services.chart_generator import ChartGenerator
        import_status['chart_generator'] = 'ok'
    except Exception as e:
        import_status['chart_generator'] = f'error: {str(e)}'
    
    return {
        "status": "ok" if all('ok' in v for v in import_status.values()) else "degraded",
        "services": import_status,
        "python_path": sys.path[:3]
    }


# Debug Endpoint
@app.get("/api/debug/test")
async def debug_test():
    """Debug endpoint to test basic functionality"""
    try:
        from src.services.data_fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        
        # Try to fetch a small amount of data
        info = fetcher.get_stock_info('RELIANCE')
        
        return {
            "status": "ok",
            "message": "Imports and basic data fetch working",
            "stock_info": info
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )


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
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__
            }
        )


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
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )


# Technical Analysis Endpoint (Phase 1 - Basic)
@app.post("/api/analyze")
async def analyze_stock(request: AnalysisRequest):
    """
    Perform technical analysis on a stock (Phase 1)
    This is the basic version - returns calculated indicators
    Phase 2 endpoint (/api/analyze-ai) includes AI agent insights
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
        
        # Create response
        response = {
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
            "note": "Phase 1: Basic analysis. Use /api/analyze-ai for AI agent insights."
        }
        
        # Sanitize response for JSON serialization (convert NumPy types)
        return sanitize_response(response)
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "symbol": request.symbol,
                "timeframe": request.timeframe
            }
        )


# AI-Powered Analysis Endpoint (Phase 2 - with AI Agents)
@app.post("/api/analyze-ai")
async def analyze_stock_ai(request: AnalysisRequest):
    """
    Perform AI-powered technical analysis (Phase 2)
    Uses 5 AI agents for comprehensive analysis:
    - Agent 1: Data Orchestration
    - Agent 2: Technical Analysis
    - Agent 3: Vision Pattern Recognition (LLM)
    - Agent 4: Risk & Scenario Analysis (LLM)
    - Agent 5: Report Writing (LLM)
    
    Also generates downloadable DOCX report
    """
    try:
        from src.crew_orchestrator import AIAnalysisCrew
        from src.services.docx_generator import DOCXReportGenerator
        
        symbol = request.symbol.upper()
        timeframe = request.timeframe
        
        # Run AI analysis crew
        crew = AIAnalysisCrew()
        result = crew.run_analysis(symbol, timeframe)
        
        if result['status'] != 'success':
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'AI analysis failed')
            )
        
        # Generate DOCX report
        try:
            docx_gen = DOCXReportGenerator()
            docx_path = docx_gen.generate_report(result, include_chart=True)
            result['docx_path'] = docx_path
            result['docx_filename'] = os.path.basename(docx_path)
            result['docx_download_url'] = f"/api/download/docx/{os.path.basename(docx_path)}"
        except Exception as e:
            logger.warning(f"DOCX generation failed: {str(e)}")
            result['docx_path'] = None
            result['docx_error'] = str(e)
        
        # Sanitize response for JSON serialization
        return sanitize_response(result)
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "symbol": request.symbol,
                "timeframe": request.timeframe
            }
        )


# DOCX Download Endpoint (Phase 3)
@app.get("/api/download/docx/{filename}")
async def download_docx(filename: str):
    """Download generated DOCX report"""
    docx_dir = os.getenv("DOCX_OUTPUT_DIR", "/home/claude/stock-analysis-ai/backend/reports")
    filepath = os.path.join(docx_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )


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
    
    print("\n" + "="*80)
    print("🚀 Starting Stock Technical Analysis AI Backend")
    print("="*80)
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://localhost:{port}/docs")
    print(f"Health: http://localhost:{port}/api/health")
    print("="*80 + "\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )