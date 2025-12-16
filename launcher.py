"""
MAC Dashboard Launcher - THREAD-BASED VERSION
Runs Streamlit in a background thread instead of subprocess
This works better with single-file EXE builds
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser
import threading
import time

# Import authentication from main.py
from main import app as msal_app, SCOPES, BASE_DIR


class AuthLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("MAC Quality Dashboard - Launcher")
        self.geometry("500x400")
        self.configure(bg="#F0F0F0")
        
        # Center window
        self.eval('tk::PlaceWindow . center')
        
        self.streamlit_thread = None
        self.streamlit_running = False
        
        self.create_widgets()
        self.check_auth_status()
    
    def create_widgets(self):
        """Create the launcher UI"""
        # Header
        header_frame = tk.Frame(self, bg="#1E3A8A", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="MAC QUALITY DASHBOARD",
            bg="#1E3A8A",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(expand=True)
        
        # Main content
        content = tk.Frame(self, bg="#F0F0F0")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Status label
        self.status_label = tk.Label(
            content,
            text="Checking authentication...",
            bg="#F0F0F0",
            font=("Segoe UI", 12),
            wraplength=400
        )
        self.status_label.pack(pady=20)
        
        # Auth button
        self.auth_button = tk.Button(
            content,
            text="Authenticate with Microsoft",
            command=self.authenticate,
            font=("Segoe UI", 12, "bold"),
            bg="#1E40AF",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        self.auth_button.pack(pady=10)
        self.auth_button.pack_forget()
        
        # Launch button
        self.launch_button = tk.Button(
            content,
            text="Launch Dashboard",
            command=self.launch_streamlit,
            font=("Segoe UI", 12, "bold"),
            bg="#059669",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        self.launch_button.pack(pady=10)
        self.launch_button.pack_forget()
        
        # Info text
        self.info_label = tk.Label(
            content,
            text="",
            bg="#F0F0F0",
            font=("Segoe UI", 9),
            wraplength=400,
            fg="#666666"
        )
        self.info_label.pack(pady=20)
    
    def check_auth_status(self):
        """Check if user is already authenticated"""
        try:
            accounts = msal_app.get_accounts()
            if accounts:
                result = msal_app.acquire_token_silent(SCOPES, account=accounts[0])
                if result and "access_token" in result:
                    self.status_label.config(text="Already authenticated!", fg="#059669")
                    self.info_label.config(text="You're signed in and ready to go.\nClick below to launch the dashboard.")
                    self.launch_button.pack(pady=10)
                    return
            
            self.status_label.config(text="Authentication Required", fg="#D97706")
            self.info_label.config(text="You need to sign in with Microsoft before using the dashboard.\nClick below to authenticate.")
            self.auth_button.pack(pady=10)
            
        except:
            self.status_label.config(text="Authentication Required", fg="#D97706")
            self.info_label.config(text="You need to sign in with Microsoft before using the dashboard.\nClick below to authenticate.")
            self.auth_button.pack(pady=10)
    
    def authenticate(self):
        """Start authentication flow"""
        self.status_label.config(text="Starting authentication...", fg="#1E40AF")
        self.auth_button.config(state="disabled")
        self.update()
        
        try:
            flow = msal_app.initiate_device_flow(scopes=SCOPES)
            
            if "user_code" not in flow:
                messagebox.showerror("Error", f"Failed to start authentication: {flow.get('error_description', 'Unknown error')}")
                self.auth_button.config(state="normal")
                return
            
            self.show_auth_dialog(flow)
            
        except Exception as e:
            messagebox.showerror("Error", f"Authentication error: {str(e)}")
            self.auth_button.config(state="normal")
            self.status_label.config(text="Authentication failed", fg="#DC2626")
    
    def show_auth_dialog(self, flow):
        """Show device code authentication dialog"""
        popup = tk.Toplevel(self)
        popup.title("Microsoft Authentication")
        popup.geometry("500x300")
        popup.transient(self)
        popup.grab_set()
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (500 // 2)
        y = (popup.winfo_screenheight() // 2) - (300 // 2)
        popup.geometry(f"500x300+{x}+{y}")
        
        tk.Label(popup, text="Sign in with Microsoft", font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(popup, text="Follow these steps to authenticate:", font=("Segoe UI", 10)).pack(pady=5)
        tk.Label(popup, text="1. Click 'Open Login Page' below", font=("Segoe UI", 9)).pack(anchor="w", padx=40)
        tk.Label(popup, text="2. Enter the code shown below", font=("Segoe UI", 9)).pack(anchor="w", padx=40)
        tk.Label(popup, text="3. Sign in with your Microsoft work account", font=("Segoe UI", 9)).pack(anchor="w", padx=40)
        
        code_frame = tk.Frame(popup, bg="#1E3A8A", relief="ridge", bd=2)
        code_frame.pack(pady=15)
        tk.Label(code_frame, text=flow["user_code"], font=("Courier New", 18, "bold"), bg="#1E3A8A", fg="white", padx=20, pady=10).pack()
        
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        def copy_code():
            popup.clipboard_clear()
            popup.clipboard_append(flow["user_code"])
            messagebox.showinfo("Copied", "Code copied to clipboard!")
        
        def open_browser():
            webbrowser.open("https://microsoft.com/devicelogin")
        
        tk.Button(button_frame, text="Copy Code", command=copy_code, font=("Segoe UI", 10), padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(button_frame, text="Open Login Page", command=open_browser, font=("Segoe UI", 10, "bold"), bg="#0078D4", fg="white", padx=15, pady=5).pack(side="left", padx=5)
        
        tk.Label(popup, text="Waiting for you to complete sign-in...", font=("Segoe UI", 9), fg="#666666").pack(pady=10)
        
        def complete_auth():
            try:
                result = msal_app.acquire_token_by_device_flow(flow)
                
                if "access_token" in result:
                    popup.destroy()
                    self.status_label.config(text="Authentication successful!", fg="#059669")
                    self.info_label.config(text="You're now signed in.\nClick below to launch the dashboard.")
                    self.auth_button.pack_forget()
                    self.launch_button.pack(pady=10)
                    messagebox.showinfo("Success", "Authentication successful!\n\nYou can now launch the dashboard.")
                else:
                    popup.destroy()
                    messagebox.showerror("Authentication Failed", result.get("error_description", "Unknown error"))
                    self.auth_button.config(state="normal")
                    self.status_label.config(text="Authentication failed", fg="#DC2626")
            except Exception as e:
                popup.destroy()
                messagebox.showerror("Error", f"Authentication error: {str(e)}")
                self.auth_button.config(state="normal")
                self.status_label.config(text="Authentication failed", fg="#DC2626")
        
        auth_thread = threading.Thread(target=complete_auth, daemon=True)
        auth_thread.start()
    
    def launch_streamlit(self):
        """Launch Streamlit - THREAD-BASED VERSION"""
        if self.streamlit_running:
            messagebox.showinfo("Already Running", "Dashboard is already running!\nCheck your browser at http://localhost:8501")
            return
        
        self.status_label.config(text="Launching dashboard...", fg="#1E40AF")
        self.launch_button.config(state="disabled")
        self.update()
        
        def run_streamlit():
            """Run Streamlit in a thread"""
            try:
                # Add paths to sys.path so imports work
                if getattr(sys, 'frozen', False):
                    bundle_dir = sys._MEIPASS
                    exe_dir = os.path.dirname(sys.executable)
                else:
                    bundle_dir = os.path.dirname(os.path.abspath(__file__))
                    exe_dir = bundle_dir
                
                # Add to path if not already there
                for path in [bundle_dir, exe_dir]:
                    if path not in sys.path:
                        sys.path.insert(0, path)
                
                # Change working directory so DB/Excel files are created next to EXE
                os.chdir(exe_dir)
                
                # Import Streamlit CLI
                from streamlit.web import cli as stcli
                
                # Set up arguments for Streamlit
                streamlit_app_path = os.path.join(bundle_dir, "streamlit_app.py")
                
                sys.argv = [
                    "streamlit",
                    "run",
                    streamlit_app_path,
                    "--server.port=8501",
                    "--server.headless=true",
                    "--browser.gatherUsageStats=false",
                    "--server.fileWatcherType=none"
                ]
                
                self.streamlit_running = True
                
                # Run Streamlit (this blocks until Streamlit stops)
                stcli.main()
                
            except Exception as e:
                import traceback
                error_msg = f"Streamlit failed to start:\n\n{str(e)}\n\n{traceback.format_exc()[:500]}"
                self.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.after(0, lambda: self.launch_button.config(state="normal"))
                self.after(0, lambda: self.status_label.config(text="Launch failed", fg="#DC2626"))
            finally:
                self.streamlit_running = False
        
        # Start Streamlit in a background thread
        self.streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
        self.streamlit_thread.start()
        
        # Wait a bit, then open browser
        self.after(5000, self.open_dashboard)
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('localhost', 8501))
                if result == 0:
                    # Streamlit is running
                    webbrowser.open("http://localhost:8501")
                    
                    messagebox.showinfo(
                        "Dashboard Launched",
                        "The dashboard has been opened in your browser!\n\n"
                        "You can minimize this launcher window.\n"
                        "The dashboard will continue running."
                    )
                    
                    # Re-enable button
                    self.launch_button.config(state="normal")
                    self.status_label.config(text="Dashboard is running!", fg="#059669")
                    self.info_label.config(text="Browser opened at http://localhost:8501\nYou can minimize this window.")
                else:
                    # Not running yet - wait and retry
                    self.after(3000, self.retry_open)
        except:
            self.after(3000, self.retry_open)
    
    def retry_open(self):
        """Retry opening dashboard"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('localhost', 8501))
                if result == 0:
                    webbrowser.open("http://localhost:8501")
                    messagebox.showinfo("Dashboard Launched", "Dashboard opened in your browser!")
                    self.launch_button.config(state="normal")
                    self.status_label.config(text="Dashboard is running!", fg="#059669")
                else:
                    messagebox.showerror(
                        "Streamlit Not Started",
                        "Streamlit failed to start.\n\n"
                        "This may be a build issue.\n"
                        "Try rebuilding with: pyinstaller --clean MAC_Dashboard_SingleFile.spec"
                    )
                    self.launch_button.config(state="normal")
                    self.status_label.config(text="Launch failed", fg="#DC2626")
        except:
            messagebox.showerror("Error", "Could not verify Streamlit status.")
            self.launch_button.config(state="normal")


def main():
    """Main entry point"""
    print("=" * 60)
    print("MAC Quality Dashboard Launcher (Thread-Based)")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Running as EXE: {getattr(sys, 'frozen', False)}")
    if getattr(sys, 'frozen', False):
        print(f"EXE location: {sys.executable}")
        print(f"Bundle dir: {sys._MEIPASS}")
    print("=" * 60)
    
    app = AuthLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()























