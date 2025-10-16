# 🚀 Quick Start Guide

This guide will help you get the AI-Powered Presales Assistant up and running quickly.

## ⚡ Fast Setup (Automated)

### 1. Run Setup Script
```bash
# Double-click or run in Command Prompt:
setup_project.bat
```
This will automatically:
- Create Python virtual environment
- Install all backend dependencies  
- Install all frontend dependencies
- Create `.env` file from template

### 2. Configure API Key
Edit the `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Start the Application

**Terminal 1 (Backend):**
```bash
venv\Scripts\activate
python ff.py
```

**Terminal 2 (Frontend):**
```bash
cd presales-assistant-ui
npm start
```

### 4. Access the Application
Open your browser to: `http://localhost:3000`

## 🔧 Manual Setup (If Scripts Don't Work)

### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API Key

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
# Edit .env and add your OpenAI API key
```

### Frontend Setup
```bash
cd presales-assistant-ui
npm install
```

### Start Services
```bash
# Terminal 1 - Backend
venv\Scripts\activate
python ff.py

# Terminal 2 - Frontend  
cd presales-assistant-ui
npm start
```

## 📋 Git Repository Setup

### 1. Initialize Git (if not cloned)
```bash
# Run the Git setup script:
setup_git.bat

# Or manually:
git init
git add .
git commit -m "Initial commit: AI-Powered Presales Assistant"
```

### 2. Connect to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/presales_assistant.git
git branch -M main
git push -u origin main
```

## 🧪 Test the Application

1. **Open** `http://localhost:3000`
2. **Enter** a company name (e.g., "Microsoft")
3. **Click** "Fetch Matching Rows"
4. **Select** some portfolio entries
5. **Click** "Build Pitch"
6. **Review** the generated pitch with AI Intelligence Dashboard

## 🔍 Troubleshooting

### Common Issues

**"Git not recognized"**
- Install Git from: https://git-scm.com/download/win
- Restart command prompt after installation

**"Python not recognized"** 
- Install Python 3.11+ from: https://www.python.org/downloads/
- Make sure to check "Add to PATH" during installation

**"Node not recognized"**
- Install Node.js 16+ from: https://nodejs.org/
- Restart command prompt after installation

**"OpenAI API Error"**
- Check your API key in `.env` file
- Ensure you have credits in your OpenAI account
- Verify the key has the correct permissions

**"Port already in use"**
- Backend (8000): Kill any running Python processes
- Frontend (3000): Kill any running Node.js processes

### Getting Help

1. Check the main [README.md](README.md) for detailed documentation
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines  
3. Create an issue on GitHub for bugs or questions

## 🎯 Next Steps

Once running successfully:

1. **Explore Features**: Try different companies and see the AI intelligence gathering
2. **Customize Portfolio**: Update `Project_Portfolio_Data.xlsx` with your data
3. **Configure Search**: Modify search engine preferences in `ff.py`
4. **Enhance UI**: Customize the React frontend in `presales-assistant-ui/src/`

---

**Happy presales automation! 🎉**