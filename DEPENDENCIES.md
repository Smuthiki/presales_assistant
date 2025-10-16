# 📦 Complete Dependency Management Guide

## Overview
This document lists all dependencies for the AI-Powered Presales Assistant, organized by backend (Python) and frontend (Node.js).

## 🐍 Python Backend Dependencies

### Core Framework & Server
- `fastapi==0.104.1` - Modern web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `python-multipart==0.0.6` - File upload support

### AI & Machine Learning  
- `openai==1.3.8` - OpenAI API client
- `pandas==2.1.3` - Data manipulation
- `numpy==1.25.2` - Numerical computations
- `scikit-learn==1.3.2` - Machine learning
- `sentence-transformers==2.2.2` - Text embeddings

### Web Scraping & Data Processing
- `beautifulsoup4==4.12.2` - HTML parsing
- `requests==2.31.0` - HTTP requests
- `duckduckgo-search==3.9.6` - Search API
- `lxml==4.9.3` - XML/HTML parser

### Document Processing
- `reportlab==4.0.7` - PDF generation
- `openpyxl==3.1.2` - Excel file handling

### System & Configuration
- `python-dotenv==1.0.0` - Environment variables
- `httpx==0.25.2` - Async HTTP client
- `anyio==4.0.0` - Async compatibility
- `psutil==5.9.6` - System process management

## ⚛️ Node.js Frontend Dependencies

### Core React
- `react@^19.1.1` - React library
- `react-dom@^19.1.1` - React DOM renderer
- `react-scripts@5.0.1` - Create React App scripts

### UI Framework (Material-UI)
- `@mui/material@^7.3.2` - Material-UI components
- `@mui/icons-material@^7.3.2` - Material-UI icons
- `@emotion/react@^11.14.0` - CSS-in-JS styling
- `@emotion/styled@^11.14.1` - Styled components

### HTTP & API Communication
- `axios@^1.12.2` - HTTP client for API calls

### Content Rendering
- `react-markdown@^10.1.0` - Markdown rendering

### Document Generation
- `jspdf@^3.0.3` - PDF generation
- `html2canvas@^1.4.1` - Canvas screenshot utility

### CSS & Styling
- `@csstools/normalize.css@^12.1.1` - CSS normalization
- `postcss-normalize@^13.0.1` - PostCSS normalize plugin

### Testing
- `@testing-library/jest-dom@^6.8.0` - Jest DOM matchers
- `@testing-library/react@^16.3.0` - React testing utilities
- `@testing-library/user-event@^13.5.0` - User interaction testing
- `@testing-library/dom@^10.4.1` - DOM testing utilities

### Development & Utilities
- `concurrently@^9.2.1` - Run multiple commands
- `web-vitals@^2.1.4` - Performance monitoring

## 🔧 Installation Commands

### Automatic (Recommended)
```bash
# Complete setup (installs everything)
python setup.py

# Repair frontend dependencies
python run.py repair
```

### Manual Installation

#### Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd presales-assistant-ui
npm install

# Critical dependencies (auto-installed by setup/repair)
npm install @csstools/normalize.css postcss-normalize
npm install @mui/material @mui/icons-material
npm install @emotion/react @emotion/styled
npm install axios react-markdown
npm install jspdf html2canvas
npm install concurrently web-vitals
```

## 🚨 Common Issues & Solutions

### CSS/PostCSS Errors
```bash
# Error: "Cannot find module '@csstools/normalize.css'"
python run.py repair
```

### Missing Material-UI Components
```bash
# Error: "Module not found: Can't resolve '@mui/material'"
python run.py repair
```

### PDF Generation Issues
```bash
# Error: "jspdf is not defined" or "html2canvas not found"
cd presales-assistant-ui
npm install jspdf html2canvas
```

### HTTP Request Errors
```bash
# Error: "axios is not defined"
cd presales-assistant-ui
npm install axios
```

## 📁 Dependency Files

- `requirements.txt` - Python backend dependencies
- `presales-assistant-ui/package.json` - Frontend dependencies manifest
- `presales-assistant-ui/package-requirements.txt` - Reference dependency list
- This file (`DEPENDENCIES.md`) - Complete documentation

## 🔄 Updating Dependencies

### Backend Updates
```bash
pip install --upgrade -r requirements.txt
```

### Frontend Updates
```bash
cd presales-assistant-ui
npm update
```

### Automated Updates
```bash
npm run update  # Updates both backend and frontend
```

## ✅ Verification

After installation, verify dependencies with:
```bash
python run.py diagnose  # System health check
python run.py status    # Current status
```

---

*This guide is automatically maintained by the setup and repair scripts.*