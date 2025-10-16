# 🚀 Cross-Platform Automation System

This project now includes a powerful, cross-platform automation system that works on **Windows**, **macOS**, and **Linux**.

## 🎯 Quick Start (Any Operating System)

### First Time Setup
```bash
# Clone the repository
git clone https://github.com/Smuthiki/presales_assistant.git
cd presales_assistant

# One-command setup (installs everything)
python setup.py

# Add your API keys to .env file
# Edit .env and replace placeholder values

# Start the application
python run.py start
```

### Daily Usage
```bash
# Start application
python run.py start

# Stop application
python run.py stop

# Check status
python run.py status
```

## 📋 Available Commands

### Python Scripts (Cross-Platform)
```bash
# Setup & Installation
python setup.py              # Complete setup (Python + Node.js + .env)

# Application Control  
python run.py start          # Start both backend and frontend
python run.py stop           # Stop all servers
python run.py restart        # Restart application
python run.py status         # Check application status
python run.py diagnose       # Run system diagnostics
python run.py repair         # Repair frontend dependencies
```

### NPM Scripts (Alternative)
```bash
# Setup
npm run setup               # Same as: python setup.py

# Application Control
npm start                   # Same as: python run.py start
npm run dev                 # Same as: python run.py start
npm stop                    # Same as: python run.py stop
npm run restart             # Same as: python run.py restart
npm run status              # Same as: python run.py status
npm run diagnose            # Same as: python run.py diagnose
npm run repair              # Same as: python run.py repair

# Development
npm run backend             # Start only backend server
npm run frontend            # Start only frontend server
npm run update              # Update all dependencies
npm run clean               # Clean install (removes node_modules)
```

## 🔧 What the Automation Does

### `python setup.py` - Complete Setup
- ✅ Checks Python and Node.js installation
- ✅ Installs all Python packages (FastAPI, OpenAI, pandas, etc.)
- ✅ Installs all Node.js packages (React, Material-UI, etc.)
- ✅ Ensures critical dependencies (@csstools/normalize.css, postcss-normalize)
- ✅ Installs MUI components and icons automatically
- ✅ Sets up PDF generation tools (jspdf, html2canvas)
- ✅ Configures HTTP client (axios) and markdown rendering
- ✅ Creates `.env` file from template
- ✅ Verifies all installations
- ✅ Cross-platform colored output
- ✅ Intelligent error handling and recovery

### `python run.py start` - Application Launcher
- ✅ Starts FastAPI backend server (port 8000)
- ✅ Starts React frontend server (port 3000)
- ✅ Intelligently detects already-running servers
- ✅ Opens browser automatically
- ✅ Creates separate terminal windows on Windows
- ✅ Background processes on Linux/macOS
- ✅ Port conflict detection
- ✅ Process management
- ✅ Graceful handling of partial startups

### `python run.py stop` - Clean Shutdown
- ✅ Terminates all related processes
- ✅ Frees up ports (8000, 3000)
- ✅ Works across all operating systems
- ✅ Safe process termination

### `python run.py repair` - Frontend Repair Tool
- ✅ Fixes missing CSS dependencies (@csstools/normalize.css, postcss-normalize)
- ✅ Repairs Material-UI components (@mui/material, @mui/icons-material)
- ✅ Ensures essential utilities (axios, react-markdown)
- ✅ Installs PDF generation tools (jspdf, html2canvas)
- ✅ Verifies development dependencies (concurrently, web-vitals)
- ✅ Runs security audit and applies fixes
- ✅ Resolves common frontend compilation errors
- ✅ Safe to run multiple times
- ✅ Comprehensive dependency verification

### `python run.py diagnose` - System Health Check
- ✅ Checks Python/Node.js versions
- ✅ Verifies all project files exist
- ✅ Tests package installations
- ✅ Checks port availability
- ✅ Validates .env configuration
- ✅ Comprehensive system report

## 🌟 Key Advantages Over Batch Files

| Feature | Batch Files (.bat) | Python Scripts |
|---------|-------------------|----------------|
| **Cross-Platform** | ❌ Windows only | ✅ Windows, macOS, Linux |
| **Version Control** | ❌ Can't commit | ✅ Committed to git |
| **Error Handling** | ⚠️ Basic | ✅ Advanced with recovery |
| **Process Management** | ⚠️ Limited | ✅ Full control |
| **Colored Output** | ❌ Windows limitation | ✅ All platforms |
| **Port Detection** | ❌ Manual | ✅ Automatic |
| **Dependency Checks** | ⚠️ Basic | ✅ Comprehensive |
| **Team Collaboration** | ❌ Not shareable | ✅ Same commands for everyone |

## 💡 Platform-Specific Features

### Windows
- Creates new console windows for each server
- Handles Windows-specific process management
- Fallback for ANSI colors

### macOS/Linux  
- Background process management
- Full ANSI color support
- Unix-style signal handling

## 🛠️ Extending the Automation

### Adding New Commands
Add new commands to `run.py`:

```python
def my_custom_command():
    """Your custom automation"""
    print_colored("Running custom command...", Colors.OKCYAN)
    # Your code here

# In main():
parser.add_argument("command", choices=["start", "stop", "my-command"])
```

### Adding New NPM Scripts
Add to `package.json`:

```json
{
  "scripts": {
    "my-command": "python run.py my-command"
  }
}
```

## 🔒 Security & Best Practices

- ✅ `.env` files are gitignored by default
- ✅ No hardcoded API keys in scripts
- ✅ Safe process termination
- ✅ Prerequisite validation before execution
- ✅ Error handling prevents crashes

## 🐛 Troubleshooting

### Common Issues & Solutions

**Frontend CSS/PostCSS Errors**
```bash
python run.py repair      # Fix missing CSS dependencies
# Resolves: "Cannot find module '@csstools/normalize.css'"
#          "Loading PostCSS 'postcss-normalize' plugin failed"
```

**Server Already Running**
```bash
python run.py start   # Will detect and use existing servers
# Shows: "✓ Backend already running on port 8000"
#        "✓ Frontend already running on port 3000"
```

**Port Already in Use**
```bash
python run.py stop    # Stop all servers first
python run.py start   # Then restart
```

**Python/Node.js Not Found**
```bash
python run.py diagnose    # Check system status
# Install missing prerequisites
```

**Package Installation Fails**
```bash
# Try alternative installation
pip install --upgrade pip
python setup.py    # Re-run setup
```

**Environment Variables Not Loading**
```bash
# Check .env file exists and has correct format
python run.py diagnose    # Verify configuration
```

## 📦 Dependencies

### Python Requirements
- Python 3.11+
- All packages listed in `requirements.txt`
- `psutil` for process management

### Node.js Requirements  
- Node.js 16+
- npm packages in `presales-assistant-ui/package.json`

### Critical Frontend Dependencies
The system automatically ensures these key dependencies are installed:

**CSS & Styling:**
- `@csstools/normalize.css` - CSS normalization
- `postcss-normalize` - PostCSS plugin for normalize.css

**UI Framework:**
- `@mui/material` - Material-UI components
- `@mui/icons-material` - Material-UI icons
- `@emotion/react` + `@emotion/styled` - CSS-in-JS styling

**Core Utilities:**
- `axios` - HTTP client for API calls
- `react-markdown` - Markdown rendering
- `jspdf` + `html2canvas` - PDF generation

**Development Tools:**
- `concurrently` - Run multiple commands
- `web-vitals` - Performance monitoring

### Dependency Files
- `requirements.txt` - Python backend dependencies
- `presales-assistant-ui/package.json` - Frontend dependencies
- `presales-assistant-ui/package-requirements.txt` - Reference list

## 🚀 Deployment Ready

This automation system is designed for:
- ✅ **Development** - Quick local setup
- ✅ **CI/CD** - Automated testing and deployment
- ✅ **Production** - Environment-based configuration
- ✅ **Team Collaboration** - Consistent setup across team members

## 🌈 Cross-Platform Compatibility

Tested and working on:
- ✅ Windows 10/11
- ✅ macOS (Intel & Apple Silicon)
- ✅ Ubuntu Linux
- ✅ Other Linux distributions

---

**🎉 Enjoy seamless, cross-platform automation!**

*No more platform-specific scripts - one automation system that works everywhere!*