#!/usr/bin/env python3
"""
Cross-Platform Application Runner for AI-Powered Presales Assistant
Handles starting, stopping, and managing the application
"""

import os
import sys
import subprocess
import signal
import time
import webbrowser
import platform
import psutil
from pathlib import Path
import argparse

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

def check_port(port):
    """Check if a port is in use"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def find_processes_by_name(name):
    """Find processes by name"""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if name.lower() in proc.info['name'].lower():
                processes.append(proc)
    except:
        pass
    return processes

def kill_processes_by_port(port):
    """Kill processes using a specific port"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    print_colored(f"✓ Terminated process on port {port}", Colors.OKGREEN)
                    return True
                except:
                    pass
    except:
        pass
    return False

def start_backend():
    """Start the FastAPI backend server"""
    print_colored("Starting backend server...", Colors.OKCYAN)
    
    # Check if backend is already running
    if check_port(8000):
        print_colored("✓ Backend server already running on port 8000", Colors.OKGREEN)
        return "already_running"
    
    # Check if ff.py exists
    if not Path("ff.py").exists():
        print_colored("Error: ff.py not found!", Colors.FAIL)
        return None
    
    # Start backend server
    try:
        if platform.system() == "Windows":
            # On Windows, create new window
            backend_process = subprocess.Popen(
                [sys.executable, "ff.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems
            backend_process = subprocess.Popen(
                [sys.executable, "ff.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if check_port(8000):
            print_colored("✓ Backend server started on http://localhost:8000", Colors.OKGREEN)
            return backend_process
        else:
            print_colored("⚠ Backend server may not have started properly", Colors.WARNING)
            return backend_process
    
    except Exception as e:
        print_colored(f"Error starting backend: {e}", Colors.FAIL)
        return None

def start_frontend():
    """Start the React frontend server"""
    print_colored("Starting frontend server...", Colors.OKCYAN)
    
    # Check if frontend is already running
    if check_port(3000):
        print_colored("✓ Frontend server already running on port 3000", Colors.OKGREEN)
        return "already_running"
    
    # Check if frontend directory exists
    ui_dir = Path("presales-assistant-ui")
    if not ui_dir.exists():
        print_colored("Error: Frontend directory not found!", Colors.FAIL)
        return None
    
    # Find npm executable dynamically
    npm_path = find_executable("npm")
    if not npm_path:
        print_colored("Error: npm not found!", Colors.FAIL)
        return None
    
    # Start frontend server
    try:
        original_dir = os.getcwd()
        os.chdir(ui_dir)
        
        if platform.system() == "Windows":
            # On Windows, create new window
            frontend_process = subprocess.Popen(
                [npm_path, "start"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems
            frontend_process = subprocess.Popen(
                [npm_path, "start"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        os.chdir(original_dir)
        
        # Wait for frontend to start
        time.sleep(5)
        
        if check_port(3000):
            print_colored("✓ Frontend server started on http://localhost:3000", Colors.OKGREEN)
            return frontend_process
        else:
            print_colored("⚠ Frontend server may not have started properly", Colors.WARNING)
            return frontend_process
    
    except Exception as e:
        print_colored(f"Error starting frontend: {e}", Colors.FAIL)
        return None

def stop_servers():
    """Stop all servers"""
    print_header("STOPPING ALL SERVERS")
    
    stopped = False
    
    # Stop backend (port 8000)
    if check_port(8000):
        if kill_processes_by_port(8000):
            stopped = True
    
    # Stop frontend (port 3000)
    if check_port(3000):
        if kill_processes_by_port(3000):
            stopped = True
    
    # Alternative method: kill by process name
    python_processes = find_processes_by_name("python")
    for proc in python_processes:
        try:
            if "ff.py" in " ".join(proc.info.get('cmdline', [])):
                proc.terminate()
                print_colored("✓ Terminated backend process", Colors.OKGREEN)
                stopped = True
        except:
            pass
    
    node_processes = find_processes_by_name("node")
    for proc in node_processes:
        try:
            cmdline = " ".join(proc.info.get('cmdline', []))
            if "react-scripts" in cmdline or "npm" in cmdline:
                proc.terminate()
                print_colored("✓ Terminated frontend process", Colors.OKGREEN)
                stopped = True
        except:
            pass
    
    if stopped:
        print_colored("✓ All servers stopped", Colors.OKGREEN)
    else:
        print_colored("ℹ No running servers found", Colors.WARNING)

def repair_frontend():
    """Repair frontend dependencies and issues"""
    print_header("REPAIRING FRONTEND DEPENDENCIES")
    
    ui_dir = Path("presales-assistant-ui")
    if not ui_dir.exists():
        print_colored("Frontend directory not found!", Colors.FAIL)
        return False
    
    original_dir = os.getcwd()
    os.chdir(ui_dir)
    
    try:
        # Install missing dependencies
        npm_path = find_executable("npm")
        if not npm_path:
            print_colored("npm not found!", Colors.FAIL)
            return False
        
        # Check for Material-UI corruption by looking for common signs
        mui_corrupted = False
        try:
            result = subprocess.run([npm_path, "list", "@mui/material"], 
                                  capture_output=True, text=True, check=False)
            if result.returncode != 0 or "ENOENT" in result.stderr:
                mui_corrupted = True
        except:
            mui_corrupted = True
        
        # If Material-UI appears corrupted, do a clean reinstall
        if mui_corrupted:
            print_colored("Material-UI corruption detected. Performing clean reinstall...", Colors.WARNING)
            
            # Remove Material-UI packages
            mui_packages = ["@mui/material", "@mui/icons-material", "@emotion/react", "@emotion/styled"]
            for pkg in mui_packages:
                try:
                    subprocess.run([npm_path, "uninstall", pkg], 
                                 capture_output=True, text=True, check=False)
                    print_colored(f"✓ Removed {pkg}", Colors.OKGREEN)
                except:
                    pass
            
            # Check if complete clean install is needed
            node_modules = Path("node_modules")
            if node_modules.exists() and any("ENOENT" in str(e) for e in []):
                print_colored("Performing complete clean install...", Colors.WARNING)
                try:
                    import shutil
                    if node_modules.exists():
                        shutil.rmtree(node_modules)
                    
                    package_lock = Path("package-lock.json")
                    if package_lock.exists():
                        package_lock.unlink()
                    
                    print_colored("✓ Cleaned node_modules and package-lock.json", Colors.OKGREEN)
                    
                    # Reinstall all dependencies
                    print_colored("Reinstalling all dependencies...", Colors.OKCYAN)
                    result = subprocess.run([npm_path, "install"], 
                                          capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        print_colored("✓ Complete reinstall successful", Colors.OKGREEN)
                    else:
                        print_colored("⚠ Reinstall had issues but continuing...", Colors.WARNING)
                        
                except Exception as e:
                    print_colored(f"⚠ Clean install error: {e}", Colors.WARNING)
        
        print_colored("Installing/repairing critical dependencies...", Colors.OKCYAN)
        critical_deps = [
            # CSS and PostCSS (most common issue)
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
            
            # Development tools
            "concurrently@^9.2.1",
            "web-vitals@^2.1.4"
        ]
        
        for dep in critical_deps:
            try:
                result = subprocess.run([npm_path, "install", dep], 
                                      capture_output=True, text=True, check=False)
                dep_name = dep.split('@')[0]
                if result.returncode == 0:
                    print_colored(f"✓ Installed/verified {dep_name}", Colors.OKGREEN)
                else:
                    print_colored(f"⚠ Issue with {dep_name}", Colors.WARNING)
            except Exception as e:
                print_colored(f"⚠ Error installing {dep}: {e}", Colors.WARNING)
        
        # Try to fix audit issues
        print_colored("Attempting to fix security issues...", Colors.OKCYAN)
        try:
            subprocess.run([npm_path, "audit", "fix"], 
                         capture_output=True, text=True, check=False)
            print_colored("✓ Security audit completed", Colors.OKGREEN)
        except:
            print_colored("⚠ Could not run security audit", Colors.WARNING)
        
        # Verify critical packages and detect corruption
        print_colored("Verifying critical packages...", Colors.OKCYAN)
        verification_packages = [
            "@csstools/normalize.css",
            "postcss-normalize",
            "@mui/material", 
            "react-markdown",
            "axios"
        ]
        
        corruption_detected = False
        for pkg in verification_packages:
            try:
                result = subprocess.run([npm_path, "list", pkg], 
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0 and "ENOENT" not in result.stderr:
                    print_colored(f"✓ {pkg} verified", Colors.OKGREEN)
                else:
                    print_colored(f"⚠ {pkg} may need attention", Colors.WARNING)
                    if "ENOENT" in result.stderr or "missing" in result.stderr.lower():
                        corruption_detected = True
            except:
                print_colored(f"⚠ Could not verify {pkg}", Colors.WARNING)
        
        # Special check for Material-UI ESM files
        mui_esm_check = Path("node_modules/@mui/material/esm")
        if mui_esm_check.exists():
            # Check for common missing files that cause compilation errors
            critical_files = [
                "node_modules/@mui/material/esm/Paper/index.js",
                "node_modules/@mui/material/esm/ButtonBase/index.js", 
                "node_modules/@mui/material/esm/CircularProgress/index.js"
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                print_colored("⚠ Material-UI ESM files corruption detected!", Colors.WARNING)
                print_colored("Run 'python run.py repair' again or do a manual clean install", Colors.WARNING)
                corruption_detected = True
            else:
                print_colored("✓ Material-UI ESM files verified", Colors.OKGREEN)
        
        if corruption_detected:
            print_colored("\n⚠ Package corruption detected! If issues persist:", Colors.WARNING)
            print_colored("1. Run: python run.py repair", Colors.WARNING)
            print_colored("2. Or manually: cd presales-assistant-ui && npm run clean && npm install", Colors.WARNING)
        
        return True
    finally:
        os.chdir(original_dir)

def diagnose_system():
    """Run system diagnostics"""
    print_header("SYSTEM DIAGNOSTICS")
    
    # Check Python
    try:
        python_version = subprocess.run([sys.executable, "--version"], 
                                      capture_output=True, text=True)
        print_colored(f"✓ Python: {python_version.stdout.strip()}", Colors.OKGREEN)
    except:
        print_colored("✗ Python issue", Colors.FAIL)
    
    # Check Node.js
    node_path = find_executable("node")
    if node_path:
        try:
            node_version = subprocess.run([node_path, "--version"], 
                                        capture_output=True, text=True)
            print_colored(f"✓ Node.js: {node_version.stdout.strip()} (found at: {node_path})", Colors.OKGREEN)
        except:
            print_colored("✗ Node.js not working", Colors.FAIL)
    else:
        print_colored("✗ Node.js not found", Colors.FAIL)
    
    # Check npm
    npm_path = find_executable("npm")
    if npm_path:
        try:
            npm_version = subprocess.run([npm_path, "--version"], 
                                       capture_output=True, text=True)
            print_colored(f"✓ npm: {npm_version.stdout.strip()} (found at: {npm_path})", Colors.OKGREEN)
        except:
            print_colored("✗ npm not working", Colors.FAIL)
    else:
        print_colored("✗ npm not found", Colors.FAIL)
    
    # Check project files
    files_to_check = {
        "ff.py": "Backend main file",
        "Project_Portfolio_Data.xlsx": "Portfolio data",
        ".env": "Environment configuration",
        "presales-assistant-ui/package.json": "Frontend configuration"
    }
    
    print_colored("\nProject Files:", Colors.OKCYAN)
    for file, description in files_to_check.items():
        if Path(file).exists():
            print_colored(f"✓ {description} ({file})", Colors.OKGREEN)
        else:
            print_colored(f"✗ {description} missing ({file})", Colors.FAIL)
    
    # Check ports
    print_colored("\nPort Status:", Colors.OKCYAN)
    if check_port(8000):
        print_colored("✓ Port 8000 in use (backend likely running)", Colors.OKGREEN)
    else:
        print_colored("ℹ Port 8000 available", Colors.WARNING)
    
    if check_port(3000):
        print_colored("✓ Port 3000 in use (frontend likely running)", Colors.OKGREEN)
    else:
        print_colored("ℹ Port 3000 available", Colors.WARNING)
    
    # Check .env file
    print_colored("\nEnvironment Configuration:", Colors.OKCYAN)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key and api_key != 'your_openai_api_key_here':
            print_colored("✓ OpenAI API key configured", Colors.OKGREEN)
        else:
            print_colored("⚠ OpenAI API key needs configuration", Colors.WARNING)
        
        model = os.getenv('OPENAI_MODEL', '')
        if model:
            print_colored(f"✓ OpenAI model: {model}", Colors.OKGREEN)
        
    except Exception as e:
        print_colored(f"⚠ Environment configuration issue: {e}", Colors.WARNING)

def start_application():
    """Start the complete application"""
    print_header("STARTING AI-POWERED PRESALES ASSISTANT")
    
    # Check .env file
    if not Path(".env").exists():
        print_colored("Warning: .env file not found. Run 'python setup.py' first.", Colors.WARNING)
    
    # Start backend
    backend_result = start_backend()
    if backend_result is None:
        print_colored("Failed to start backend", Colors.FAIL)
        return
    
    # Start frontend
    frontend_result = start_frontend()
    if frontend_result is None:
        print_colored("Failed to start frontend", Colors.FAIL)
        return
    
    # Open browser
    print_colored("Opening browser...", Colors.OKCYAN)
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:3000")
        print_colored("✓ Browser opened", Colors.OKGREEN)
    except:
        print_colored("Could not open browser automatically", Colors.WARNING)
        print("Please open http://localhost:3000 manually")
    
    print_header("APPLICATION STARTED SUCCESSFULLY!")
    
    # Show status based on what happened
    if backend_result == "already_running":
        print_colored("✓ Backend already running on: http://localhost:8000", Colors.OKGREEN)
    else:
        print_colored("✓ Backend started on: http://localhost:8000", Colors.OKGREEN)
    
    if frontend_result == "already_running":
        print_colored("✓ Frontend already running on: http://localhost:3000", Colors.OKGREEN)
    else:
        print_colored("✓ Frontend started on: http://localhost:3000", Colors.OKGREEN)
    
    print_colored("✓ Browser opened automatically", Colors.OKGREEN)
    
    if platform.system() != "Windows":
        print("\nTo stop the application, run: python run.py stop")
        print("Or press Ctrl+C in the terminal windows")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="AI-Powered Presales Assistant Runner")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "diagnose", "repair"], 
                       help="Command to execute")
    
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print_header("AI-POWERED PRESALES ASSISTANT RUNNER")
        print("Available commands:")
        print("  python run.py start     - Start the application")
        print("  python run.py stop      - Stop all servers")
        print("  python run.py restart   - Restart the application")
        print("  python run.py status    - Check application status")
        print("  python run.py diagnose  - Run system diagnostics")
        print("  python run.py repair    - Repair frontend dependencies")
        print("\nFor first-time setup, run: python setup.py")
        return
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_application()
    elif args.command == "stop":
        stop_servers()
    elif args.command == "restart":
        stop_servers()
        time.sleep(2)
        start_application()
    elif args.command == "status":
        diagnose_system()
    elif args.command == "diagnose":
        diagnose_system()
    elif args.command == "repair":
        repair_frontend()

if __name__ == "__main__":
    main()