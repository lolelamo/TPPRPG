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
            print("\033[2J\033[H", end='')  # Clear screen
            print("This script is running with administrator privileges.")
            print("Press Enter to continue...")
            input()

        else:
            print("\033[2J\033[H", end='')  # Clear screen
            print("This script is NOT running with administrator privileges.")
            print("Some operations may not work properly.")
            print("")
            print("The 'keyboard' library requires root privileges on Linux.")
            print("")
            
            # Ask for admin with better formatting
            try:
                response = input("Do you want to restart this script with admin privileges? (y/n): ").strip().lower()
                print("\033[2J\033[H", end='')  # Clear screen after input
                
                if response in ['y', 'yes']:
                    print("Requesting administrator privileges...")
                    request_admin()
                else:
                    print("Continuing without admin privileges...")
                    Write(str(LOG_PATH), "", "Running without admin privileges, Linux")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                sys.exit(1)
            except EOFError:
                print("\nInput error. Continuing without admin privileges...")
                Write(str(LOG_PATH), "", "Running without admin privileges, Linux")
    else:
        print("\033[2J\033[H", end='')  # Clear screen
        print("Info: keyboard library doesn't require admin privileges on Windows. This is optional")
        try:
            response = input("Do you want to restart this script with admin privileges? (y/n): ").strip().lower()
            print("\033[2J\033[H", end='')  # Clear screen after input
            
            if response in ['y', 'yes']:
                print("Requesting administrator privileges...")
                request_admin()
            else:
                print("Continuing without admin privileges...")
                Write(str(LOG_PATH), "", "Running without admin privileges, Windows")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(1)
        except EOFError:
            print("\nInput error. Continuing without admin privileges...")
            Write(str(LOG_PATH), "", "Running without admin privileges, Windows")

if __name__ == "__main__":
    main_c()

