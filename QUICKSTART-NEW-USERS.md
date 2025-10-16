# 🚀 Quick Start for New Users

## ⚡ One-Click Setup (Recommended)

### For Complete Beginners:
1. **Double-click** `⚡ ONE-CLICK SETUP.bat`
2. **Add your OpenAI API key** to the `.env` file that gets created
3. **Double-click** `🚀 Launch Presales Assistant.bat`
4. **Open** http://localhost:3000 in your browser

That's it! 🎉

## 📋 Prerequisites (Auto-checked by setup)
- **Python 3.11+** - [Download here](https://www.python.org/downloads/) (check "Add to PATH")
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)

## 🛠 What the One-Click Setup Does
✅ Checks if Python and Node.js are installed  
✅ Installs all Python dependencies globally  
✅ Installs all React/Node.js dependencies  
✅ Creates environment configuration file  
✅ Sets up launch shortcuts  
✅ Offers to start the application immediately  

## 🔑 After Setup - Add Your API Key
Edit the `.env` file and replace:
```env
OPENAI_API_KEY=your_openai_api_key_here
```
With your actual OpenAI API key.

## 🚀 Launch Options After Setup

### Option 1: Double-Click Launch (Easiest)
- Double-click `🚀 Launch Presales Assistant.bat`

### Option 2: Command Line
```bash
cd presales-assistant-ui
npm run start-all
```

### Option 3: Individual Services
```bash
# Backend only
python ff.py

# Frontend only (in new terminal)
cd presales-assistant-ui
npm start
```

## 🌐 Access Your Application
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 🆘 Troubleshooting

### "Python is not recognized"
- Install Python from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation
- Restart your command prompt

### "Node is not recognized"  
- Install Node.js from https://nodejs.org/
- Restart your command prompt

### "Permission denied" errors
- Run Command Prompt as Administrator
- Or use: `pip install --user` for Python packages

### OpenAI API Errors
- Make sure your API key is correct in `.env`
- Check your OpenAI account has credits
- Verify the key has the right permissions

## 🎯 Quick Test
1. Enter "Microsoft" in the company field
2. Click "Fetch Matching Rows"
3. Select some portfolio entries
4. Click "Build Pitch"
5. Watch the AI generate a comprehensive pitch!

---

**New to coding?** Just use the one-click setup files - they handle everything automatically! 🎊