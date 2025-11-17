# 🎨 Stock Analysis AI - Frontend Dashboard

Beautiful Next.js 14 dashboard for displaying AI-powered stock analysis.

## ✨ Features

- **Modern UI**: Built with Next.js 14 + TypeScript
- **Beautiful Design**: Tailwind CSS with dark mode support
- **Responsive**: Works on desktop, tablet, and mobile
- **Real-time Analysis**: Connect to backend API for live analysis
- **Scenario Display**: Interactive table showing trading scenarios
- **Report Viewing**: Beautiful markdown rendering
- **DOCX Download**: One-click download of professional reports
- **Dark Mode**: Toggle between light and dark themes

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles + Tailwind
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main page (home)
├── components/
│   ├── Header.tsx            # Header with dark mode toggle
│   ├── AnalysisForm.tsx      # Stock analysis form
│   ├── AnalysisResults.tsx   # Results display with tabs
│   ├── ScenarioTable.tsx     # Trading scenarios table
│   └── MetricsCard.tsx       # Metric display cards
├── public/                   # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

---

## 🎨 UI Components

### Header
- Logo and branding
- Dark mode toggle
- Sticky navigation

### AnalysisForm
- Stock symbol input with autocomplete
- Timeframe selector
- Quick stock buttons
- Loading states

### AnalysisResults
- Executive summary
- Key metrics cards
- Tabbed interface:
  - Overview
  - Scenarios
  - Full Report
- DOCX download button

### ScenarioTable
- Trading scenarios with color coding
- Entry, Stop, Target prices
- R:R ratios
- Confidence levels
- WarrenAI insights

---

## 🔧 Configuration

### Backend API URL

The frontend proxies API requests to the backend. Update `next.config.js` if your backend runs on a different port:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*', // Change port if needed
    },
  ]
}
```

---

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: "hsl(221.2 83.2% 53.3%)", // Change primary color
      // ... other colors
    }
  }
}
```

### Branding

Update the logo and title in `components/Header.tsx`:

```tsx
<span className="text-xl font-bold">
  Your Company Name
</span>
```

---

## 📱 Responsive Design

The dashboard is fully responsive:

- **Desktop**: Full layout with side-by-side elements
- **Tablet**: Adaptive grid layouts
- **Mobile**: Stacked layouts with optimized spacing

---

## 🌙 Dark Mode

Dark mode is automatically detected from system preferences and can be toggled manually. Preferences are saved in localStorage.

---

## 🚢 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Deploy

```bash
npm run build
```

### Other Platforms

```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## 📊 API Integration

The frontend expects these API endpoints:

### POST `/api/analyze-ai`
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
  "stock_info": {...},
  "technical_analysis": {...},
  "pattern_analysis": {...},
  "risk_analysis": {
    "scenarios": [...],
    "backtest": {...}
  },
  "report": {
    "markdown": "...",
    "summary": "...",
    "recommendation": "..."
  },
  "docx_download_url": "/api/download/docx/..."
}
```

### GET `/api/download/docx/{filename}`
Downloads the DOCX report.

---

## 🐛 Troubleshooting

### Backend Connection Issues

If you see connection errors:

1. **Check backend is running**: `http://localhost:8000/api/health`
2. **Check CORS**: Backend should allow `localhost:3000`
3. **Check proxy**: Verify `next.config.js` rewrites

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

---

## 📦 Dependencies

### Core
- `next` - React framework
- `react` - UI library
- `typescript` - Type safety

### Styling
- `tailwindcss` - Utility-first CSS
- `lucide-react` - Icon library

### Functionality
- `axios` - HTTP client
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub Flavored Markdown

---

## 🎯 Performance

### Optimization Tips

1. **Image Optimization**: Use Next.js `<Image>` component
2. **Code Splitting**: Components are lazy-loaded automatically
3. **Caching**: API responses can be cached with SWR
4. **Build Optimization**: Production builds are optimized automatically

---

## 🔐 Security

- No sensitive data stored in frontend
- API keys handled by backend
- HTTPS recommended for production
- CORS properly configured

---

## 📝 License

This project is part of the Stock Analysis AI system.

---

## 🆘 Support

For issues or questions:
1. Check the backend is running
2. Verify API endpoints are accessible
3. Check browser console for errors
4. Review Next.js documentation

---

**Built with ❤️ using Next.js 14 + TypeScript + Tailwind CSS**