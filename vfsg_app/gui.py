# VFSG-Booking-Automation/vfs_app/gui.py

import os
import sys
import threading
import time
import customtkinter as ctk

# أضف مجلد المشروع للمسارات لضمان رؤية الملفات الأخرى
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_manager import login_to_vfs, start_new_booking, fill_appointment_form, open_browser, close_browser, handle_cookies
import __init__ as shared

# هذه الوظيفة تجعل البرنامج يعرف مساره الحقيقي حتى بعد الضغط (EXE)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# إعدادات الشكل العام
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VfsDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VFS Global - Control Center")
        self.geometry("550x700")  # حجم النافذة

        # ==========================================
        # إنشاء إطار قابل للتمرير (Scrollable Frame)
        # ==========================================
        # كل العناصر سيتم وضعها داخل هذا الإطار ليظهر الـ Scrollbar
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=650)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- العنوان ---
        self.label = ctk.CTkLabel(
            self.scroll_frame, text="VFS AUTOMATION", font=("Roboto", 24, "bold")
        )
        self.label.pack(pady=(10, 20))

        # ==========================================
        # 1. إعدادات الدخول والروابط
        # ==========================================
        self.url_var = ctk.StringVar(value=shared.DEFAULT_URL)
        self.url_entry = ctk.CTkEntry(self.scroll_frame, width=420, textvariable=self.url_var)
        self.url_entry.pack(pady=5, padx=20)

        self.email_label = ctk.CTkLabel(self.scroll_frame, text="Email Address:")
        self.email_label.pack(pady=(10, 0))
        self.email_var = ctk.StringVar(value=shared.user["email"])
        self.email_entry = ctk.CTkEntry(self.scroll_frame, width=420, textvariable=self.email_var)
        self.email_entry.pack(pady=5)

        self.pwd_label = ctk.CTkLabel(self.scroll_frame, text="Password:")
        self.pwd_label.pack(pady=(10, 0))
        self.pwd_var = ctk.StringVar(value=shared.user["pwd"])
        self.pwd_entry = ctk.CTkEntry(self.scroll_frame, width=420, textvariable=self.pwd_var, show="*")
        self.pwd_entry.pack(pady=5)

        # ==========================================
        # 2. حالة البوت
        # ==========================================
        self.status_label = ctk.CTkLabel(self.scroll_frame, text="Status: Ready", text_color="gray", font=("Roboto", 14))
        self.status_label.pack(pady=15)

        # ==========================================
        # 3. أزرار التحكم
        # ==========================================
        self.btn_launch = ctk.CTkButton(
            self.scroll_frame, text="Launch With Chrome", fg_color="#2ECC71", hover_color="#27AE60",
            font=("Roboto", 14, "bold"), command=self.start_full_flow_thread
        )
        self.btn_launch.pack(pady=10, padx=60, fill="x")

        self.btn_close_chrome = ctk.CTkButton(
            self.scroll_frame, text="Terminate Chrome Only", fg_color="#E67E22", hover_color="#D35400",
            command=close_browser
        )
        self.btn_close_chrome.pack(pady=5, padx=60, fill="x")

        self.btn_exit_all = ctk.CTkButton(
            self.scroll_frame, text="Close All & Exit", fg_color="#C0392B", hover_color="#A93226",
            command=self.full_exit
        )
        self.btn_exit_all.pack(pady=10, padx=60, fill="x")

        # مسافة فاصلة
        ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray20").pack(fill="x", pady=15, padx=30)

        # ==========================================
        # 4. إعدادات الصيد (Hunting Settings)
        # ==========================================
        self.settings_frame = ctk.CTkFrame(self.scroll_frame)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # عدد التبديلات
        self.switch_label = ctk.CTkLabel(self.settings_frame, text="Max Refresh Switches:", font=("Roboto", 12, "bold"))
        self.switch_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.max_switch_var = ctk.StringVar(value="5") # الافتراضي 5
        self.max_switch_entry = ctk.CTkEntry(self.settings_frame, width=60, textvariable=self.max_switch_var)
        self.max_switch_entry.grid(row=0, column=1, padx=10, pady=10)

        # ==========================================
        # 5. اختيار الفئة المستهدفة
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
            
        # مسافة إضافية في النهاية للراحة البصرية أثناء الـ Scroll
        ctk.CTkLabel(self.scroll_frame, text="").pack(pady=10)

    # --- الوظائف ---

    def sync_category(self):
        """تحديث الهدف في الإعدادات المشتركة ليقرأه البوت فوراً"""
        shared.tracking_config["main_target"] = self.target_cat_var.get()
        print(f"[GUI] New Hunting Target: {shared.tracking_config['main_target']}")

    def start_full_flow_thread(self):
        """تشغيل العملية بالكامل في Thread لتجنب تجميد الواجهة"""
        t = threading.Thread(target=self.run_full_automation)
        t.daemon = True
        t.start()

    def run_full_automation(self):
        # 1. تحديث البيانات من الـ UI لملف الـ shared
        shared.user["email"] = self.email_entry.get()
        shared.user["pwd"] = self.pwd_entry.get()
        url = self.url_entry.get()

        # تحديث الفئة المستهدفة
        selected_cat = self.target_cat_var.get()
        shared.tracking_config["main_target"] = selected_cat
        
        # قراءة عدد المحاولات وتخزينها في shared ليقرأها ملف الـ browser_manager
        try:
            val = int(self.max_switch_var.get())
            shared.tracking_config["max_switches"] = val
        except ValueError:
            shared.tracking_config["max_switches"] = 5 # قيمة افتراضية لو أدخل المستخدم نص خاطئ

        print(f"\n[System] User Selected Category: {selected_cat}")
        print(f"[System] Max Switches Set To: {shared.tracking_config['max_switches']}")

        self.update_status("Launching Stealth Chrome...", "#3498DB")
        open_browser(url)

        self.update_status("Waiting for Cookies...", "#F1C40F")
        handle_cookies()

        self.update_status("Attempting Auto-Login...", "#9B59B6")
        if login_to_vfs():
            self.update_status("Login Successful! Check Browser.", "#2ECC71")
        else:
            self.update_status("Login Failed! Check Selectors.", "#E74C3C")
            return 

        if start_new_booking():
            self.update_status("Booking Started! Filling Form...", "#3498DB")

            # يتم استدعاء دالة التعبئة الآن (وهي ستقرأ max_switches من shared مباشرة)
            if fill_appointment_form():
                self.update_status("Base Form Filled. Starting Hunter...", "#2ECC71")

                # استدعاء ملف الصياد
                from trackiing_loging import run_vfs_monitor
                self.update_status(f"Hunting Slots in {selected_cat}...", "#E67E22")

                run_vfs_monitor()

                self.update_status("SLOT FOUND! Complete Payment.", "#2ECC71")

            else:
                self.update_status("Form Error / Max Attempts Reached.", "#E74C3C")
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