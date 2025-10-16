# 🚀 How to Run AI-Powered Presales Assistant from Start

## Quick Start (TL;DR)
```powershell
# 1. Setup everything
python setup.py

# 2. Start the application  
python run.py start

# 3. Open browser to http://localhost:3000 (opens automatically)
```

---

## 📋 **Prerequisites Check**

Before starting, verify you have these installed:

### Required Software
- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/) (includes npm)
- **Git** (optional) - Only if cloning from repository

### Quick Verification
```powershell
python --version    # Should show 3.11+
node --version      # Should show 16+
npm --version       # Should show a version number
```

---

## 🎯 **Complete Step-by-Step Guide**

### **Step 1: Navigate to Project Directory**
```powershell
# If you already have the project folder
cd C:\Users\smuthiki\Downloads\presales_assistant

# OR if cloning from GitHub
git clone https://github.com/Smuthiki/presales_assistant.git
cd presales_assistant
```

### **Step 2: One-Command Complete Setup**
This installs **everything** automatically:
```powershell
python setup.py
```

**What it does:**
- ✅ Checks all prerequisites (Python, Node.js, npm)
- ✅ Installs Python backend dependencies (FastAPI, OpenAI, etc.)
- ✅ Installs React frontend dependencies (Material-UI, React, etc.)  
- ✅ Ensures CSS dependencies (@csstools/normalize.css, postcss-normalize)
- ✅ Sets up API communication tools (axios)
- ✅ Configures PDF generation (jspdf, html2canvas)
- ✅ Creates/verifies .env configuration file
- ✅ Runs security vulnerability fixes
- ✅ Verifies all installations work correctly

**Expected Output:**
```
================================================================================
  AI-POWERED PRESALES ASSISTANT - CROSS-PLATFORM SETUP
================================================================================
✓ Python: Python 3.13.7
✓ Node.js: v22.20.0
✓ npm: 10.9.3
✓ Python dependencies installed
✓ Node.js dependencies installed
✓ Environment file created
✓ Setup verified
Setup completed successfully! 🚀
```

### **Step 3: Verify Environment Configuration**
Check your API keys (should already be configured):
```powershell
# View .env file
notepad .env

# OR check with command
type .env
```

Should contain:
```
OPENAI_API_KEY=sk-proj-[your-key-here]
OPENAI_MODEL=gpt-4o
SERPAPI_API_KEY=[your-serpapi-key]
```

### **Step 4: Start the Application**
```powershell
python run.py start
```

**What happens:**
- 🚀 Starts FastAPI backend server on port 8000
- 🚀 Starts React frontend server on port 3000  
- 🌐 Opens browser automatically to http://localhost:3000
- ✅ Shows success confirmation

**Expected Output:**
```
================================================================================
  STARTING AI-POWERED PRESALES ASSISTANT
================================================================================
Starting backend server...
✓ Backend server started on http://localhost:8000
Starting frontend server...  
✓ Frontend server started on http://localhost:3000
Opening browser...
✓ Browser opened

================================================================================
  APPLICATION STARTED SUCCESSFULLY!
================================================================================
✓ Backend running on: http://localhost:8000
✓ Frontend running on: http://localhost:3000
✓ Browser opened automatically
```

### **Step 5: Use the Application**
The application opens in your browser with three main sections:
- 📊 **Portfolio Summary** - AI-powered portfolio analysis
- 📋 **Case Studies** - Relevant case study generation  
- 💬 **Chat** - Interactive AI assistance

---

## 🔄 **Daily Usage Commands**

Once set up, these are the commands you'll use regularly:

```powershell
# Start the application
python run.py start

# Stop the application  
python run.py stop

# Restart everything
python run.py restart

# Check what's running
python run.py status

# System health check
python run.py diagnose

# Fix frontend issues
python run.py repair
```

---

## 🛠️ **Troubleshooting**

### **If Setup Fails**
```powershell
# Check system status
python run.py diagnose

# Try setup again
python setup.py
```

### **If Frontend Has CSS Errors**
```powershell
# Fix missing CSS dependencies
python run.py repair
```

### **If Servers Don't Start**
```powershell
# Stop any existing processes
python run.py stop

# Start fresh
python run.py start
```

### **If Ports Are Busy**
```powershell
# Check what's using ports 8000 and 3000
python run.py diagnose

# Force stop and restart
python run.py stop
python run.py start
```

### **Complete Reset**
```powershell
# Nuclear option - complete reset
python run.py stop
python setup.py
python run.py start
```

---

## 📱 **Alternative Commands (NPM Shortcuts)**

You can also use npm commands:
```powershell
npm run dev         # Same as: python run.py start
npm start           # Same as: python run.py start
npm stop            # Same as: python run.py stop  
npm run repair      # Same as: python run.py repair
npm run diagnose    # Same as: python run.py diagnose
```

---

## ✅ **Verification Checklist**

After starting, verify everything works:

1. **Backend API**: Visit http://localhost:8000/docs (FastAPI docs)
2. **Frontend**: Visit http://localhost:3000 (Main application)
3. **System Status**: Run `python run.py diagnose`

Should show all green checkmarks ✅

---

## 🚨 **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| `npm not found` | Reinstall Node.js from nodejs.org |
| `Python not found` | Install Python 3.11+ from python.org |
| `Port already in use` | Run `python run.py stop` first |
| `CSS compilation errors` | Run `python run.py repair` |
| `API key errors` | Check .env file has valid keys |
| `Module not found` | Run `python setup.py` again |

---

## 🎯 **For Impatient Users**

**Super Quick Start (One Command):**
```powershell
python setup.py && python run.py start
```

**Just Want to Start (Already Set Up):**
```powershell
python run.py start
```

**Something's Broken, Fix Everything:**
```powershell
python run.py repair && python run.py start
```

---

## 📞 **Getting Help**

If you encounter issues:
1. Run `python run.py diagnose` to see system status
2. Check this guide's troubleshooting section
3. Review `AUTOMATION_README.md` for detailed automation info
4. Check `DEPENDENCIES.md` for dependency information

---

## 🎉 **Success!**

When everything is working, you should see:
- Backend API running on http://localhost:8000
- Frontend app running on http://localhost:3000  
- Browser opens automatically
- No error messages in terminal

**You're ready to use the AI-Powered Presales Assistant!** 🚀

---

*This guide is maintained automatically by the setup scripts. Last updated: October 2025*