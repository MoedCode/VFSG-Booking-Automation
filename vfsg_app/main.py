# VFSG-Booking-Automation/vfs_app/main.py

from __init__ import *
from browser_manager import *
from gui import VfsDashboard
import threading
import sys

# ريموت كنترول للـ GUI
gui_app = None


def main():
    global gui_app, driver
    print("--- VFS Browser Controller ---")

    def run_gui():
        global gui_app
        gui_app = VfsDashboard()
        gui_app.mainloop()

    # تشغيل الـ GUI في الخلفية
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.daemon = True  # مهم جداً عشان يقفل مع الـ terminal
    gui_thread.start()

    while True:
        try:
            raw_input = input("\nAction >> ").strip().lower()
            if not raw_input:
                continue

            # الخروج النهائي
            if raw_input in ["\\e", "exit"]:
                close_browser()
                if gui_app:
                    gui_app.after(0, gui_app.full_exit)  # اؤمر الـ GUI يقفل نفسه بأمان
                print("Goodbye!")
                break

            # إغلاق الـ GUI فقط
            elif raw_input in ["\\eg", "exit gui"]:
                if gui_app:
                    # بنستخدم after(0) عشان نبعت الأمر للـ Thread بتاع الـ GUI
                    gui_app.after(0, gui_app.destroy)
                    print("GUI closed.")
                else:
                    print("GUI is not running.")

            # فتح الكروم
            elif raw_input.startswith(("\\oc", "open chrome")):
                # كود الفتح بتاعك زي ما هو...
                open_browser(DEFAULT_URL)
                handle_cookies()

        except KeyboardInterrupt:
            close_browser()
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
