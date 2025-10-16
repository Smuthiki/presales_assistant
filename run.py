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
        print_colored("Backend server already running on port 8000", Colors.WARNING)
        return None
    
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
        print_colored("Frontend server already running on port 3000", Colors.WARNING)
        return None
    
    # Check if frontend directory exists
    ui_dir = Path("presales-assistant-ui")
    if not ui_dir.exists():
        print_colored("Error: Frontend directory not found!", Colors.FAIL)
        return None
    
    # Start frontend server
    try:
        original_dir = os.getcwd()
        os.chdir(ui_dir)
        
        if platform.system() == "Windows":
            # On Windows, create new window
            frontend_process = subprocess.Popen(
                ["npm", "start"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=True
            )
        else:
            # On Unix-like systems
            frontend_process = subprocess.Popen(
                ["npm", "start"],
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
    try:
        node_version = subprocess.run(["node", "--version"], 
                                    capture_output=True, text=True)
        print_colored(f"✓ Node.js: {node_version.stdout.strip()}", Colors.OKGREEN)
    except:
        print_colored("✗ Node.js not found", Colors.FAIL)
    
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
    backend_process = start_backend()
    if backend_process is None:
        print_colored("Failed to start backend", Colors.FAIL)
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if frontend_process is None:
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
    print_colored("✓ Backend running on: http://localhost:8000", Colors.OKGREEN)
    print_colored("✓ Frontend running on: http://localhost:3000", Colors.OKGREEN)
    print_colored("✓ Browser opened automatically", Colors.OKGREEN)
    
    if platform.system() != "Windows":
        print("\nTo stop the application, run: python run.py stop")
        print("Or press Ctrl+C in the terminal windows")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="AI-Powered Presales Assistant Runner")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "diagnose"], 
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

if __name__ == "__main__":
    main()