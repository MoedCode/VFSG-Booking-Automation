# VFSG-Booking-Automation/vfs_app/gui.py

import os
import sys
from browser_manager import login_to_vfs, start_new_booking, fill_appointment_details

# هذه الوظيفة تجعل البرنامج يعرف مساره الحقيقي حتى بعد الضغط (EXE)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# أضف مجلد المشروع للمسارات لضمان رؤية الملفات الأخرى
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import customtkinter as ctk

import threading
import time
from browser_manager import open_browser, close_browser, handle_cookies
import __init__ as shared

# إعدادات الشكل العام
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VfsDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VFS Global - Control Center")
        self.geometry("500x600")  # زودنا الطول شوية عشان الفورم الجديدة

        # --- العنوان ---
        self.label = ctk.CTkLabel(
            self, text="VFS AUTOMATION", font=("Roboto", 24, "bold")
        )
        self.label.pack(pady=20)

        # --- 1. مدخل الرابط (باقي كما هو) ---
        self.url_var = ctk.StringVar(value=shared.DEFAULT_URL)
        self.url_entry = ctk.CTkEntry(self, width=420, textvariable=self.url_var)
        self.url_entry.pack(pady=5, padx=20)

        # --- 2. نموذج تسجيل الدخول (Login Form) ---
        self.email_label = ctk.CTkLabel(self, text="Email Address:")
        self.email_label.pack(pady=(10, 0))
        self.email_var = ctk.StringVar(value=shared.user["email"])
        self.email_entry = ctk.CTkEntry(self, width=420, textvariable=self.email_var)
        self.email_entry.pack(pady=5)

        self.pwd_label = ctk.CTkLabel(self, text="Password:")
        self.pwd_label.pack(pady=(10, 0))
        self.pwd_var = ctk.StringVar(value=shared.user["pwd"])
        self.pwd_entry = ctk.CTkEntry(
            self, width=420, textvariable=self.pwd_var, show="*"
        )
        self.pwd_entry.pack(pady=5)

        # --- حالة البوت ---
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", text_color="gray")
        self.status_label.pack(pady=10)

        # --- الأزرار ---

        # الزرار اللي طلبته: Launch With Chrome
        self.btn_launch = ctk.CTkButton(
            self,
            text="Launch With Chrome",
            fg_color="#2ECC71",
            hover_color="#27AE60",
            font=("Roboto", 14, "bold"),
            command=self.start_full_flow_thread,
        )
        self.btn_launch.pack(pady=15, padx=60, fill="x")

        # باقي الأزرار (إغلاق الكروم، إغلاق الـ GUI، إلخ)
        self.btn_close_chrome = ctk.CTkButton(
            self,
            text="Terminate Chrome Only",
            fg_color="#E67E22",
            hover_color="#D35400",
            command=close_browser,
        )
        self.btn_close_chrome.pack(pady=5, padx=60, fill="x")

        self.btn_exit_all = ctk.CTkButton(
            self,
            text="Close All & Exit",
            fg_color="#C0392B",
            hover_color="#A93226",
            command=self.full_exit,
        )
        self.btn_exit_all.pack(pady=10, padx=60, fill="x")

    # --- وظائف التشغيل ---

    def start_full_flow_thread(self):
        """تشغيل العملية بالكامل في Thread"""
        t = threading.Thread(target=self.run_full_automation)
        t.daemon = True
        t.start()

    def run_full_automation(self):
        # 1. تحديث البيانات من الـ UI لملف الـ shared
        shared.user["email"] = self.email_entry.get()
        shared.user["pwd"] = self.pwd_entry.get()
        url = self.url_entry.get()

        self.update_status("Launching Stealth Chrome...", "#3498DB")
        open_browser(url)

        self.update_status("Waiting for Cookies...", "#F1C40F")
        handle_cookies()

        self.update_status("Attempting Auto-Login...", "#9B59B6")
        if login_to_vfs():
            self.update_status("Login Successful! Check Browser.", "#2ECC71")
        else:
            self.update_status("Login Failed! Check Selectors.", "#E74C3C")


        if start_new_booking():
            self.update_status("Booking Started! Filling Form...", "#3498DB")
            
            # NEW: Call the form filler
            if fill_appointment_details():
                self.update_status("Form Submitted! Moving to next step.", "#2ECC71")
            else:
                self.update_status("Form Error! Check console.", "#E74C3C")
        else:
            self.update_status("Failed to start booking", "#E74C3C")

    def update_status(self, text, color):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def full_exit(self):
        close_browser()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = VfsDashboard()
    app.mainloop()
