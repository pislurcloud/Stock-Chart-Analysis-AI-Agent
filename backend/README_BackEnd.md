# 🚀 Stock Analysis AI - Backend

Comprehensive AI-powered stock technical analysis system for Indian NSE stocks with 5 AI agents, 50+ indicators, and professional report generation.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [AI Agents](#ai-agents)
- [Technical Indicators](#technical-indicators)
- [Usage Examples](#usage-examples)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

A production-ready backend API that performs comprehensive technical analysis on Indian stock market (NSE) stocks using:

- **50+ Technical Indicators** (RSI, MACD, Bollinger Bands, etc.)
- **5 AI Agents** (sequential workflow with LLMs)
- **Pattern Recognition** (AI-powered visual analysis)
- **Scenario Generation** (trading strategies with R:R ratios)
- **Professional Reports** (Markdown + DOCX formats)
- **Real-time Data** (via yfinance)

**Built with**: Python 3.8+, FastAPI, pandas, ta-lib, LLMs (GPT-4o-mini, Claude Sonnet 4)

---

## ✨ Features

### Phase 1: Technical Analysis System
- ✅ 50+ technical indicators
- ✅ Real-time NSE stock data
- ✅ Professional chart generation
- ✅ Support/resistance detection
- ✅ Trend analysis
- ✅ Volume analysis
- ✅ Volatility metrics

### Phase 2: AI Agent System
- ✅ 5 specialized AI agents
- ✅ Sequential workflow orchestration
- ✅ Pattern recognition (visual)
- ✅ Risk analysis & scenarios
- ✅ AI-powered report synthesis
- ✅ Flexible LLM configuration

### Phase 3: Report Generation
- ✅ Professional DOCX reports
- ✅ Markdown reports
- ✅ Embedded charts
- ✅ Scenario playbook tables
- ✅ One-click download

---

## 🏗️ Architecture

```
Backend API (FastAPI)
    ↓
CrewAI Orchestrator → 5 Sequential Agents
    ↓
Agent 1: Data Orchestration (Python)
    ↓
Agent 2: Technical Analysis (Rule-based)
    ↓
Agent 3: Pattern Recognition (LLM Vision)
    ↓
Agent 4: Risk & Scenario Analysis (LLM)
    ↓
Agent 5: Report Writing (LLM)
    ↓
JSON Response + DOCX File
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Configure API Keys
```bash
# Edit .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx
```

### 3. Start Server
```bash
python3 main.py
```

Server runs on: **http://localhost:8000**

### 4. Test API
```bash
curl -X POST http://localhost:8000/api/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "timeframe": "1d"}'
```

---

## 📦 Installation

### System Requirements
- **Python**: 3.8, 3.9, 3.10, 3.11
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for dependencies

### Install Steps

```bash
cd backend

# Option 1: Direct install
pip install -r requirements.txt --break-system-packages

# Option 2: Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 3: Conda
conda create -n stock-analysis python=3.10
conda activate stock-analysis
pip install -r requirements.txt
```

### Required Packages
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
yfinance==0.2.32
ta==0.11.0
plotly==5.18.0
matplotlib==3.8.2
python-docx==1.1.0
openai==1.3.7
anthropic==0.7.7
langchain==0.1.0
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Output Directories
CHART_OUTPUT_DIR=/path/to/charts
DOCX_OUTPUT_DIR=/path/to/reports

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,https://*.app.github.dev

# AI/LLM API Keys
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Optional

# Model Configuration
VISION_MODEL=meta-llama/llama-4-maverick:free
VISION_PROVIDER=openrouter

RISK_MODEL=gpt-4o-mini
RISK_PROVIDER=openai

REPORT_MODEL=moonshotai/kimi-vl-a3b-thinking
REPORT_PROVIDER=openrouter
```

### Model Presets

**Cost-Effective (Default)** - ~$0.01 per analysis:
```bash
VISION_MODEL=meta-llama/llama-4-maverick:free  # FREE
RISK_MODEL=gpt-4o-mini
REPORT_MODEL=moonshotai/kimi-vl-a3b-thinking
```

**Premium (All Claude)** - ~$0.05 per analysis:
```bash
VISION_MODEL=anthropic/claude-sonnet-4
RISK_MODEL=anthropic/claude-sonnet-4
REPORT_MODEL=anthropic/claude-sonnet-4
VISION_PROVIDER=anthropic
RISK_PROVIDER=anthropic
REPORT_PROVIDER=anthropic
```

---

## 🔌 API Endpoints

### Base URL
- **Local**: `http://localhost:8000`
- **Codespaces**: `https://<codespace-name>-8000.app.github.dev`

---

### GET /api/health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T10:30:00Z"
}
```

---

### POST /api/analyze

Basic technical analysis (Phase 1 - no AI).

**Request**:
```json
{
  "symbol": "RELIANCE",
  "timeframe": "1d"
}
```

**Response**:
```json
{
  "symbol": "RELIANCE",
  "timeframe": "1d",
  "stock_info": {...},
  "latest_candle": {...},
  "indicators": {
    "moving_averages": {...},
    "rsi": {...},
    "macd": {...},
    "bollinger_bands": {...}
  },
  "chart_path": "/path/to/chart.png"
}
```

---

### POST /api/analyze-ai ⭐

AI-powered comprehensive analysis (Phase 2).

**Request**:
```json
{
  "symbol": "RELIANCE",
  "timeframe": "1d"
}
```

**Response**:
```json
{
  "status": "success",
  "symbol": "RELIANCE",
  "execution_time": 45.2,
  
  "technical_analysis": {
    "overall_bias": "BULLISH",
    "strength_score": 75.5,
    "trend": "STRONG BULLISH",
    "key_levels": {
      "resistance_1": 1580.00,
      "support_1": 1485.00
    }
  },
  
  "pattern_analysis": {
    "market_structure": "BULLISH",
    "patterns": [...],
    "confidence": "HIGH"
  },
  
  "risk_analysis": {
    "scenarios": [
      {
        "scenario": "Bullish (Aggressive)",
        "entry": 1520.50,
        "stop": 1485.00,
        "target": 1580.00,
        "rr_ratio": 1.68,
        "confidence": "High",
        "warreni_take": "Enter near current levels"
      }
    ],
    "backtest": {...},
    "risk_metrics": {...}
  },
  
  "report": {
    "markdown": "# RELIANCE Analysis...",
    "summary": "Strong bullish setup...",
    "recommendation": "BUY - Bullish (Aggressive)"
  },
  
  "docx_download_url": "/api/download/docx/RELIANCE_1d_analysis_xxxxx.docx"
}
```

---

### GET /api/download/docx/{filename}

Download generated DOCX report.

**Example**:
```bash
curl http://localhost:8000/api/download/docx/RELIANCE_1d_analysis_xxxxx.docx \
  --output report.docx
```

---

### Supported Parameters

**Symbols**: Any NSE stock (RELIANCE, TCS, INFY, HDFCBANK, etc.)

**Timeframes**:
- `15m` - 15 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day (default)
- `1wk` - 1 week

---

## 🤖 AI Agents

### Agent 1: Data Orchestrator
- **Type**: Python (no LLM)
- **Responsibilities**: 
  - Fetch stock data from Yahoo Finance
  - Calculate 50+ technical indicators
  - Generate professional charts
  - Quality check data

---

### Agent 2: Technical Analyst
- **Type**: Rule-based (no LLM)
- **Responsibilities**:
  - Interpret indicators
  - Identify signals
  - Detect confluences
  - Calculate trend strength

---

### Agent 3: Vision Pattern Recognition
- **Type**: LLM Vision
- **Default Model**: llama-4-maverick:free (FREE)
- **Alternative**: Claude Sonnet 4
- **Responsibilities**:
  - Analyze chart images
  - Identify patterns (triangles, H&S, flags)
  - Recognize candlestick patterns
  - Assess market structure

---

### Agent 4: Risk & Scenario Analyst
- **Type**: LLM Text
- **Default Model**: GPT-4o-mini
- **Alternative**: Claude Sonnet 4
- **Responsibilities**:
  - Generate trading scenarios
  - Calculate entry/stop/target levels
  - Compute risk:reward ratios
  - Recommend position sizing

---

### Agent 5: Report Writer
- **Type**: LLM Text
- **Default Model**: Kimi (moonshotai)
- **Alternative**: Claude Sonnet 4
- **Responsibilities**:
  - Synthesize all insights
  - Generate markdown report
  - Create DOCX document
  - Provide key takeaways

---

## 📊 Technical Indicators

### Trend Indicators (12)
- Moving Averages (SMA 20, 50, 200)
- EMA (9, 21, 50)
- ADX (Average Directional Index)
- SuperTrend
- Ichimoku Cloud

### Momentum Indicators (10)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
- CCI (Commodity Channel Index)
- Williams %R
- ROC (Rate of Change)

### Volatility Indicators (8)
- Bollinger Bands
- ATR (Average True Range)
- Keltner Channels
- Donchian Channels
- Standard Deviation

### Volume Indicators (6)
- Volume MA
- OBV (On-Balance Volume)
- CMF (Chaikin Money Flow)
- Volume Rate of Change
- VWAP (Volume Weighted Average Price)

### Support/Resistance (14)
- Pivot Points (Standard, Fibonacci, Camarilla)
- Fibonacci Retracements
- Dynamic S/R (Swing highs/lows)

**Total: 50+ indicators**

---

## 💡 Usage Examples

### Example 1: Python Client
```python
import requests

response = requests.post(
    'http://localhost:8000/api/analyze-ai',
    json={
        'symbol': 'RELIANCE',
        'timeframe': '1d'
    }
)

data = response.json()
print(f"Recommendation: {data['report']['recommendation']}")
print(f"Bias: {data['technical_analysis']['overall_bias']}")

# Download DOCX
docx_url = f"http://localhost:8000{data['docx_download_url']}"
```

### Example 2: Batch Analysis
```python
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

for symbol in stocks:
    response = requests.post(
        'http://localhost:8000/api/analyze-ai',
        json={'symbol': symbol, 'timeframe': '1d'}
    )
    data = response.json()
    print(f"{symbol}: {data['report']['recommendation']}")
```

### Example 3: cURL
```bash
# Analyze stock
curl -X POST http://localhost:8000/api/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TCS", "timeframe": "1d"}' \
  | jq -r '.report.recommendation'

# Download report
curl http://localhost:8000/api/download/docx/TCS_1d_analysis_xxxxx.docx \
  --output TCS_report.docx
```

---

## 🚢 Deployment

### Docker

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python3", "main.py"]
```

**Build & Run**:
```bash
docker build -t stock-analysis-backend .
docker run -p 8000:8000 --env-file .env stock-analysis-backend
```

---

### Railway

1. Connect GitHub repo
2. Set environment variables
3. Auto-deploy

**railway.json**:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 main.py"
  }
}
```

---

### Render

1. Create Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `python3 main.py`
4. Add environment variables

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
python3 main.py
```

### API Key Errors
```bash
# Check .env file
cat .env | grep API_KEY
```

### CORS Errors
```bash
# Update .env
CORS_ORIGINS=http://localhost:3000,https://*.app.github.dev
```

### Chart Generation Fails
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

### DOCX Generation Fails
```bash
pip install python-docx --break-system-packages
```

---

## 💰 Cost Analysis

### Per Analysis Cost

**Default Configuration**:
- Agent 1-2: $0.000 (Python)
- Agent 3: $0.000 (llama-4-maverick:free)
- Agent 4: $0.003 (GPT-4o-mini)
- Agent 5: $0.007 (Kimi)
- **Total: ~$0.01**

**With Claude Sonnet 4**:
- Agent 1-2: $0.000
- Agent 3: $0.015 (Claude vision)
- Agent 4: $0.015 (Claude)
- Agent 5: $0.020 (Claude)
- **Total: ~$0.05**

### Monthly Estimates

| Usage | Default | Claude |
|-------|---------|--------|
| 10/day | $3 | $15 |
| 50/day | $15 | $75 |
| 100/day | $30 | $150 |

---

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)
- **ReDoc**: http://localhost:8000/redoc
- **Frontend README**: See `frontend/README.md`

---

## 🎯 Roadmap

- [ ] WebSocket for real-time updates
- [ ] Database integration
- [ ] Batch processing API
- [ ] Custom indicators
- [ ] Alert system
- [ ] PDF reports
- [ ] Multi-stock comparison

---

**Version**: 3.0  
**Last Updated**: November 2025  
**Built with**: Python, FastAPI, pandas, AI/LLMs

---

**🎉 Backend Complete - Ready for Production!**