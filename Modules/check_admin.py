#!/usr/bin/env python3
import os
import platform
import sys
from pathlib import Path

# Get the absolute path to the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Define log path using pathlib for better path handling
LOG_PATH = PROJECT_ROOT / "logs" / "logs.txt"

def is_admin():
    """Checks if the script is running with administrator privileges."""
    if platform.system() == 'Windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:  # Linux, Unix, etc.
        return os.geteuid() == 0  # Root has UID 0

def request_admin():
    """Attempt to restart the script with admin privileges."""
    if platform.system() == 'Windows':
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Requesting administrator privileges...")
                # Get the script path
                script = sys.executable
                params = sys.argv
                # Join all parameters as strings
                params_string = ' '.join(f'"{param}"' for param in params)
                # Use ShellExecute to launch the script with elevated privileges
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", script, params_string, None, 1
                )
                # Exit the current instance
                sys.exit()
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            return False
    else:  # Linux, Unix, etc.
        if os.geteuid() != 0:
            print("Requesting root privileges...")
            try:
                # Use sudo to elevate privileges
                args = ['sudo', sys.executable] + sys.argv
                os.execvp('sudo', args)
            except Exception as e:
                print(f"Failed to request root privileges: {e}")
                return False
    return True

def main_c():
    """ Check if running as admin """
    from Modules.Loader import Write  # Local import to avoid circular dependency
    admin = is_admin()
    if platform.system() != "Windows":
        if admin:
            print("This script is running with administrator privileges.")

        else:
            print("This script is NOT running with administrator privileges.")
            print("Some operations may not work properly.\n")
            
            # Ask for admin
            response = input("Do you want to restart this script with admin privileges? (y/n): ")
            if response.lower() in ['y', 'yes']:
                request_admin()
            else:
                Write(str(LOG_PATH), "", "Running without admin privileges, Linux")
    else:
        print("Info: keyboard library doesn't require admin privileges on Windows")
        response = input("Do you want to restart this script with admin privileges? (y/n): ")

        if response.lower() in ['y', 'yes']:
            request_admin()
        else:
            Write(str(LOG_PATH), "", "Running without admin privileges, Windows")

if __name__ == "__main__":
    main_c()

