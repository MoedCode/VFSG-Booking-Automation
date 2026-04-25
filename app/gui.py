# VFSG-Booking-Automation/app/gui.py

import os
import sys
import threading
import time
import customtkinter as ctk

# Add project folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_manager import login_to_vfs, start_new_booking, fill_appointment_form, open_browser, close_browser, handle_cookies
import __init__ as shared

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VfsDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VFS Global - Control Center")
        self.geometry("550x780")  # Increased height for new controls
        
        # State control for the infinite loop
        self.is_running = False

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=730)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Title ---
        self.label = ctk.CTkLabel(
            self.scroll_frame, text="VFS AUTOMATION", font=("Roboto", 24, "bold")
        )
        self.label.pack(pady=(10, 20))

        # ==========================================
        # 1. Credentials
        # ==========================================
        self.email_label = ctk.CTkLabel(self.scroll_frame, text="Email Address:")
        self.email_label.pack(pady=(5, 0))
        self.email_var = ctk.StringVar(value=shared.user["email"])
        self.email_entry = ctk.CTkEntry(self.scroll_frame, width=420, textvariable=self.email_var)
        self.email_entry.pack(pady=5)

        self.pwd_label = ctk.CTkLabel(self.scroll_frame, text="Password:")
        self.pwd_label.pack(pady=(5, 0))
        self.pwd_var = ctk.StringVar(value=shared.user["pwd"])
        self.pwd_entry = ctk.CTkEntry(self.scroll_frame, width=420, textvariable=self.pwd_var, show="*")
        self.pwd_entry.pack(pady=5)

        # ==========================================
        # 2. Status
        # ==========================================
        self.status_label = ctk.CTkLabel(self.scroll_frame, text="Status: Ready", text_color="gray", font=("Roboto", 14))
        self.status_label.pack(pady=10)

        # ==========================================
        # 3. Control Buttons
        # ==========================================
        self.btn_launch = ctk.CTkButton(
            self.scroll_frame, text="Start Auto-Hunt", fg_color="#2ECC71", hover_color="#27AE60",
            font=("Roboto", 14, "bold"), command=self.start_automation_loop
        )
        self.btn_launch.pack(pady=5, padx=60, fill="x")

        self.btn_stop = ctk.CTkButton(
            self.scroll_frame, text="Stop Auto-Hunt", fg_color="#E74C3C", hover_color="#C0392B",
            font=("Roboto", 14, "bold"), command=self.stop_automation
        )
        self.btn_stop.pack(pady=5, padx=60, fill="x")

        self.btn_close_chrome = ctk.CTkButton(
            self.scroll_frame, text="Terminate Chrome Only", fg_color="#E67E22", hover_color="#D35400",
            command=close_browser
        )
        self.btn_close_chrome.pack(pady=5, padx=60, fill="x")

        ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray20").pack(fill="x", pady=10, padx=30)

        # ==========================================
        # 4. Relaunch & Loop Settings (NEW)
        # ==========================================
        self.relaunch_frame = ctk.CTkFrame(self.scroll_frame)
        self.relaunch_frame.pack(pady=5, padx=20, fill="x")

        # Max Relaunches
        ctk.CTkLabel(self.relaunch_frame, text="Max Relaunch Cycles (0 = Infinite):", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.max_cycles_var = ctk.StringVar(value="50")
        self.max_cycles_entry = ctk.CTkEntry(self.relaunch_frame, width=60, textvariable=self.max_cycles_var)
        self.max_cycles_entry.grid(row=0, column=1, padx=10, pady=10)

        # Delay between relaunches
        ctk.CTkLabel(self.relaunch_frame, text="Delay Between Launches (Seconds):", font=("Roboto", 12, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.delay_var = ctk.StringVar(value="60")
        self.delay_entry = ctk.CTkEntry(self.relaunch_frame, width=60, textvariable=self.delay_var)
        self.delay_entry.grid(row=1, column=1, padx=10, pady=10)

        # Max refresh switches per session
        ctk.CTkLabel(self.relaunch_frame, text="Category Refresh Switches per session:", font=("Roboto", 12, "bold")).grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.max_switch_var = ctk.StringVar(value="5")
        self.max_switch_entry = ctk.CTkEntry(self.relaunch_frame, width=60, textvariable=self.max_switch_var)
        self.max_switch_entry.grid(row=2, column=1, padx=10, pady=10)

        # ==========================================
        # 5. Target Category
        # ==========================================
        self.radio_frame = ctk.CTkFrame(self.scroll_frame)
        self.radio_frame.pack(pady=10, padx=20, fill="x")

        self.cat_label = ctk.CTkLabel(self.radio_frame, text="Target Category to Hunt:", font=("Roboto", 12, "bold"))
        self.cat_label.pack(pady=10, padx=15, anchor="w")

        self.target_cat_var = ctk.StringVar(value="Tourism")

        categories = [
            ("Tourism", "Tourism"),
            ("Business", "Business"),
            ("Family Visit", "Family/Friend Visit"),
            ("Other", "Other (Medical, Cultural and sports, Entry Visa)"),
        ]

        for text, value in categories:
            rb = ctk.CTkRadioButton(
                self.radio_frame, text=text, variable=self.target_cat_var, value=value, command=self.sync_category
            )
            rb.pack(side="top", anchor="w", padx=20, pady=5)
            
        ctk.CTkLabel(self.scroll_frame, text="").pack(pady=10)

    # --- Functions ---

    def sync_category(self):
        shared.tracking_config["main_target"] = self.target_cat_var.get()
        print(f"[GUI] New Hunting Target: {shared.tracking_config['main_target']}")

    def stop_automation(self):
        """Signals the loop to stop after the current action."""
        if self.is_running:
            self.is_running = False
            self.update_status("Stopping automation... Please wait.", "#E74C3C")
            print("[System] Stop signal received. Will halt after current sequence.")

    def start_automation_loop(self):
        """Starts the main continuous loop in a background thread."""
        if self.is_running:
            print("[System] Bot is already running!")
            return
            
        self.is_running = True
        t = threading.Thread(target=self.run_master_loop)
        t.daemon = True
        t.start()

    def run_master_loop(self):
        """The Master Loop that handles relaunching Chrome."""
        
        # Read parameters from UI
        try:
            max_cycles = int(self.max_cycles_var.get())
            delay_seconds = int(self.delay_var.get())
            shared.tracking_config["max_switches"] = int(self.max_switch_var.get())
        except ValueError:
            max_cycles = 50
            delay_seconds = 60
            shared.tracking_config["max_switches"] = 5
            print("[Warning] Invalid input in settings. Using defaults.")

        shared.user["email"] = self.email_entry.get()
        shared.user["pwd"] = self.pwd_entry.get()
        shared.tracking_config["main_target"] = self.target_cat_var.get()

        cycle_count = 0

        while self.is_running:
            cycle_count += 1
            cycle_text = f"Cycle {cycle_count}/{max_cycles}" if max_cycles > 0 else f"Cycle {cycle_count}/∞"
            print(f"\n{'='*40}\n[Master Loop] Starting {cycle_text}\n{'='*40}")

            # Run a single session
            slot_found = self.run_single_session(cycle_text)

            # If a slot is found, stop the loop entirely
            if slot_found:
                self.is_running = False
                self.update_status("SLOT FOUND! Automation halted.", "#2ECC71")
                break

            # If we reached the max cycles, stop
            if max_cycles > 0 and cycle_count >= max_cycles:
                self.is_running = False
                self.update_status("Max cycles reached. Automation stopped.", "#F1C40F")
                break

            # Wait before relaunching (if still running)
            if self.is_running:
                close_browser() # Ensure old browser is killed
                self.update_status(f"Waiting {delay_seconds}s before relaunch...", "#E67E22")
                
                # Check for stop signal every second during the delay
                for _ in range(delay_seconds):
                    if not self.is_running:
                        break
                    time.sleep(1)

        print("[Master Loop] Terminated.")

    def run_single_session(self, cycle_text):
        """Runs the login and hunt process once. Returns True if slot found, False otherwise."""
        from captcha import monitor_and_solve_captcha 
        
        try:
            self.update_status(f"{cycle_text}: Launching Browser...", "#3498DB")
            open_browser(shared.DEFAULT_URL)

            self.update_status(f"{cycle_text}: Handling Cookies...", "#F1C40F")
            handle_cookies()

            self.update_status(f"{cycle_text}: Attempting Login...", "#9B59B6")
            
            if login_to_vfs():
                monitor_and_solve_captcha(context="login", timeout=15)
                self.update_status(f"{cycle_text}: Login Successful!", "#2ECC71")
            else:
                self.update_status(f"{cycle_text}: Login Failed! Will retry...", "#E74C3C")
                return False # Exit this cycle

            if start_new_booking():
                self.update_status(f"{cycle_text}: Monitoring Form...", "#E67E22")
                
                # fill_appointment_form returns True if slot found, False if max switches reached
                if fill_appointment_form(shared.tracking_config["max_switches"]):
                    monitor_and_solve_captcha(context="application_form", timeout=30)
                    import winsound
                    winsound.Beep(2000, 1000)
                    return True # SLOT FOUND!
                else:
                    self.update_status(f"{cycle_text}: No Slots Found.", "#E74C3C")
                    return False
            else:
                self.update_status(f"{cycle_text}: Failed to Start Booking.", "#E74C3C")
                return False

        except Exception as e:
            self.update_status(f"Error: {str(e)[:30]}...", "#E74C3C")
            print(f"[Session Error] {e}")
            return False

    def update_status(self, text, color):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def full_exit(self):
        self.is_running = False
        close_browser()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = VfsDashboard()
    app.mainloop()