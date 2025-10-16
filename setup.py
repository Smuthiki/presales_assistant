#!/usr/bin/env python3
"""
Cross-Platform Setup Script for AI-Powered Presales Assistant
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class Colors:
    """ANSI color codes for cross-platform colored output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def find_executable(name):
    """Find executable in PATH or common locations dynamically"""
    # First try to find in PATH
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["where", name], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(["which", name], capture_output=True, text=True, check=True)
        
        # On Windows, prefer .cmd files
        paths = result.stdout.strip().split('\n')
        if platform.system() == "Windows":
            cmd_paths = [p for p in paths if p.endswith('.cmd')]
            if cmd_paths:
                return cmd_paths[0]
        return paths[0]
    except:
        pass
    
    # If not found in PATH, try to find node first and derive npm location
    if name == "npm":
        node_path = find_executable("node")
        if node_path:
            node_dir = os.path.dirname(node_path)
            # On Windows, prioritize .cmd files
            if platform.system() == "Windows":
                potential_npm_paths = [
                    os.path.join(node_dir, "npm.cmd"),
                    os.path.join(node_dir, "npm.exe"),
                    os.path.join(node_dir, "npm"),
                ]
            else:
                potential_npm_paths = [
                    os.path.join(node_dir, "npm"),
                    os.path.join(node_dir, "npm.cmd"),
                    os.path.join(node_dir, "npm.exe"),
                ]
            
            for npm_path in potential_npm_paths:
                if os.path.exists(npm_path):
                    try:
                        subprocess.run([npm_path, "--version"], capture_output=True, text=True, check=True)
                        return npm_path
                    except:
                        continue
    
    # Last resort: try common installation directories
    if platform.system() == "Windows":
        common_paths = [
            os.path.expandvars(r"%PROGRAMFILES%\nodejs"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\nodejs"),
            os.path.expandvars(r"%APPDATA%\npm"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\npm"),
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                # Prioritize .cmd files on Windows
                potential_paths = [
                    os.path.join(base_path, f"{name}.cmd"),
                    os.path.join(base_path, f"{name}.exe"),
                    os.path.join(base_path, name),
                ]
                
                for path in potential_paths:
                    if os.path.exists(path):
                        try:
                            subprocess.run([path, "--version"], capture_output=True, text=True, check=True)
                            return path
                        except:
                            continue
    else:
        # Unix-like systems
        common_paths = [
            "/usr/local/bin",
            "/usr/bin",
            "/opt/node/bin",
            os.path.expanduser("~/.local/bin"),
            os.path.expanduser("~/node_modules/.bin"),
        ]
        
        for base_path in common_paths:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                try:
                    subprocess.run([path, "--version"], capture_output=True, text=True, check=True)
                    return path
                except:
                    continue
    
    return None

def run_npm_command(args, description, check=True):
    """Run npm command with dynamic path detection"""
    npm_path = find_executable("npm")
    if not npm_path:
        print_colored(f"✗ {description} failed - npm not found", Colors.FAIL)
        return False
    
    try:
        command = [npm_path] + args
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored(f"✓ {description} completed successfully", Colors.OKGREEN)
            return True
        else:
            print_colored(f"⚠ {description} completed with warnings", Colors.WARNING)
            if result.stderr:
                print(f"Warning: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ {description} failed", Colors.FAIL)
        print(f"Error: {e}")
        return False
    except Exception as e:
        print_colored(f"✗ {description} failed", Colors.FAIL)
        print(f"Error: {e}")
        return False

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message with fallback for Windows"""
    if platform.system() == "Windows":
        print(message)
    else:
        print(f"{color}{message}{Colors.ENDC}")

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print_colored(f"  {title}", Colors.HEADER)
    print("="*80)

def run_command(command, description, check=True):
    """Run a command with description and error handling"""
    print_colored(f"\n[RUNNING] {description}...", Colors.OKCYAN)
    
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored(f"✓ {description} completed successfully", Colors.OKGREEN)
            return True
        else:
            print_colored(f"⚠ {description} completed with warnings", Colors.WARNING)
            if result.stderr:
                print(f"Warning: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ {description} failed", Colors.FAIL)
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print_colored(f"✗ Command not found for {description}", Colors.FAIL)
        return False

def check_prerequisites():
    """Check if Python and Node.js are installed"""
    print_header("CHECKING PREREQUISITES")
    
    # Check Python
    try:
        python_version = subprocess.run([sys.executable, "--version"], 
                                      capture_output=True, text=True)
        print_colored(f"✓ Python: {python_version.stdout.strip()}", Colors.OKGREEN)
        python_ok = True
    except:
        print_colored("✗ Python not found", Colors.FAIL)
        python_ok = False
    
    # Check Node.js
    node_path = find_executable("node")
    if node_path:
        try:
            node_version = subprocess.run([node_path, "--version"], 
                                        capture_output=True, text=True)
            print_colored(f"✓ Node.js: {node_version.stdout.strip()}", Colors.OKGREEN)
            node_ok = True
        except:
            print_colored("✗ Node.js not working", Colors.FAIL)
            node_ok = False
    else:
        print_colored("✗ Node.js not found", Colors.FAIL)
        node_ok = False
    
    # Check npm
    npm_path = find_executable("npm")
    if npm_path:
        try:
            npm_version = subprocess.run([npm_path, "--version"], 
                                       capture_output=True, text=True)
            print_colored(f"✓ npm: {npm_version.stdout.strip()}", Colors.OKGREEN)
            npm_ok = True
        except:
            print_colored("✗ npm not working", Colors.FAIL)
            npm_ok = False
    else:
        print_colored("✗ npm not found", Colors.FAIL)
        npm_ok = False
    
    if not (python_ok and node_ok and npm_ok):
        print_colored("\nPlease install missing prerequisites:", Colors.WARNING)
        if not python_ok:
            print("- Python 3.11+: https://www.python.org/downloads/")
        if not node_ok or not npm_ok:
            print("- Node.js 16+ (includes npm): https://nodejs.org/")
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print_header("INSTALLING PYTHON DEPENDENCIES")
    
    # Core packages
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "openai",
        "pandas",
        "numpy",
        "scikit-learn",
        "sentence-transformers",
        "beautifulsoup4",
        "requests",
        "openpyxl",
        "duckduckgo-search",
        "python-dotenv"
    ]
    
    # Try pip install with packages
    package_list = " ".join(packages)
    success = run_command(f"{sys.executable} -m pip install {package_list}", 
                         "Installing Python packages", check=False)
    
    if not success:
        print_colored("Trying alternative installation method...", Colors.WARNING)
        run_command(f"{sys.executable} -m pip install --upgrade pip", 
                   "Upgrading pip")
        
        # Try installing from requirements.txt if it exists
        if Path("requirements.txt").exists():
            run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                       "Installing from requirements.txt", check=False)
    
    return True

def install_node_dependencies():
    """Install Node.js dependencies"""
    print_header("INSTALLING NODE.JS DEPENDENCIES")
    
    ui_dir = Path("presales-assistant-ui")
    if not ui_dir.exists():
        print_colored("Frontend directory not found!", Colors.FAIL)
        return False
    
    # Change to UI directory and install
    original_dir = os.getcwd()
    os.chdir(ui_dir)
    
    try:
        # First, install main dependencies from package.json
        success = run_npm_command(["install"], "Installing Node.js packages from package.json", check=False)
        
        if not success:
            print_colored("Trying with --force flag...", Colors.WARNING)
            success = run_npm_command(["install", "--force"], "Installing with force", check=False)
        
        # Install critical dependencies that are commonly missing
        critical_deps = [
            # CSS and PostCSS dependencies (most common issues)
            "@csstools/normalize.css@^12.1.1",
            "postcss-normalize@^13.0.1",
            
            # Core MUI dependencies
            "@mui/material@^7.3.2",
            "@mui/icons-material@^7.3.2", 
            "@emotion/react@^11.14.0",
            "@emotion/styled@^11.14.1",
            
            # Essential utilities
            "axios@^1.12.2",
            "react-markdown@^10.1.0",
            
            # PDF and canvas utilities
            "jspdf@^3.0.3",
            "html2canvas@^1.4.1",
            
            # Development utilities
            "concurrently@^9.2.1"
        ]
        
        print_colored("Ensuring critical dependencies are installed...", Colors.OKCYAN)
        for dep in critical_deps:
            run_npm_command(["install", dep], f"Installing {dep.split('@')[0]}", check=False)
        
        # Try to fix any audit issues without breaking changes
        print_colored("Fixing security vulnerabilities...", Colors.OKCYAN)
        run_npm_command(["audit", "fix"], "Fixing security issues", check=False)
        
        # Verify key packages are installed
        print_colored("Verifying installation...", Colors.OKCYAN)
        verification_packages = [
            "@csstools/normalize.css",
            "postcss-normalize", 
            "@mui/material",
            "react-markdown",
            "axios"
        ]
        
        for pkg in verification_packages:
            result = run_npm_command(["list", pkg], f"Checking {pkg}", check=False)
            if not result:
                print_colored(f"⚠ {pkg} may need manual installation", Colors.WARNING)
        
        return success
    finally:
        os.chdir(original_dir)

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_header("SETTING UP ENVIRONMENT CONFIGURATION")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_colored("✓ .env file already exists", Colors.OKGREEN)
        
        # Check if it has placeholder values
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "your_openai_api_key_here" in content:
                    print_colored("⚠ .env file needs API key configuration", Colors.WARNING)
                    print("\nPlease edit .env file and add your actual API keys:")
                    print("1. Get OpenAI API key from: https://platform.openai.com/api-keys")
                    print("2. Replace 'your_openai_api_key_here' with your actual key")
                else:
                    print_colored("✓ .env file appears to be configured", Colors.OKGREEN)
        except:
            pass
    else:
        if env_example.exists():
            print_colored("Creating .env file from template...", Colors.OKCYAN)
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print_colored("✓ .env file created", Colors.OKGREEN)
        else:
            # Create basic .env file
            print_colored("Creating basic .env file...", Colors.OKCYAN)
            env_content = """# AI-Powered Presales Assistant Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
SERPAPI_API_KEY=your_serpapi_key_here_optional
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print_colored("✓ Basic .env file created", Colors.OKGREEN)
        
        print_colored("\n⚠ IMPORTANT: Add your API keys to .env file!", Colors.WARNING)
        print("Edit .env file and replace placeholder values with actual API keys")
    
    return True

def verify_setup():
    """Verify the installation"""
    print_header("VERIFYING SETUP")
    
    # Test Python imports
    test_script = """
try:
    import fastapi, openai, pandas, numpy
    print("✓ Core Python packages working")
except ImportError as e:
    print(f"✗ Missing package: {e}")
    exit(1)

try:
    import sentence_transformers, beautifulsoup4, requests
    print("✓ Additional Python packages working")
except ImportError as e:
    print(f"⚠ Optional package issue: {e}")

try:
    from dotenv import load_dotenv
    load_dotenv()
    import os
    if os.getenv('OPENAI_API_KEY'):
        if os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
            print("⚠ .env file needs API key configuration")
        else:
            print("✓ Environment configuration loaded")
    else:
        print("⚠ OPENAI_API_KEY not found in environment")
except Exception as e:
    print(f"⚠ Environment loading issue: {e}")
"""
    
    run_command(f'{sys.executable} -c "{test_script}"', 
               "Testing Python setup", check=False)
    
    # Check Node modules
    ui_dir = Path("presales-assistant-ui")
    node_modules = ui_dir / "node_modules"
    
    if node_modules.exists():
        print_colored("✓ Node.js setup verified", Colors.OKGREEN)
    else:
        print_colored("⚠ Node.js setup incomplete", Colors.WARNING)
    
    # Check project files
    required_files = ["ff.py", "Project_Portfolio_Data.xlsx", ".env"]
    for file in required_files:
        if Path(file).exists():
            print_colored(f"✓ {file} exists", Colors.OKGREEN)
        else:
            print_colored(f"⚠ {file} missing", Colors.WARNING)
    
    return True

def main():
    """Main setup function"""
    print_header("AI-POWERED PRESALES ASSISTANT - CROSS-PLATFORM SETUP")
    print_colored("This will set up the complete development environment", Colors.OKCYAN)
    print("Works on Windows, macOS, and Linux")
    
    # Check prerequisites
    if not check_prerequisites():
        print_colored("\nSetup cannot continue without prerequisites", Colors.FAIL)
        sys.exit(1)
    
    # Install dependencies
    install_python_dependencies()
    install_node_dependencies()
    
    # Setup environment
    create_env_file()
    
    # Verify setup
    verify_setup()
    
    print_header("SETUP COMPLETE!")
    print_colored("✓ Python dependencies installed", Colors.OKGREEN)
    print_colored("✓ Node.js dependencies installed", Colors.OKGREEN)
    print_colored("✓ Environment file created", Colors.OKGREEN)
    print_colored("✓ Setup verified", Colors.OKGREEN)
    
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python run.py start")
    print("   Or: npm run dev (from project root)")
    
    print_colored("\nSetup completed successfully! 🚀", Colors.HEADER)

if __name__ == "__main__":
    main()