# VFSG-Booking-Automation/vfs_app/trackiing_loging.py

import os
import csv
import random
import time
from datetime import datetime
from __init__ import *
# --- الإعدادات ---

# ---------------------------------------------------------
# 1. دوال تسجيل اللوجات (بديل الكلاس VFSLogger)
# ---------------------------------------------------------


def get_log_file_path():
    """تنشئ المجلدات (سنة/شهر) وترجع المسار الكامل لملف اليوم"""
    now = datetime.now()
    year_dir = now.strftime("%Y")
    month_dir = now.strftime("vfsg-logs-month.%m-%Y")
    file_name = now.strftime("vfsg-logs %d-%m-%Y.csv")

    # إنشاء المسار: logs_archive / 2026 / vfsg-logs-month.04-2026 /
    full_path = os.path.join(tracking_config["base_log_dir"], year_dir, month_dir)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    return os.path.join(full_path, file_name)


def log_vfs_result(category, message):
    """تكتب النتيجة في ملف الـ CSV الخاص باليوم"""
    path = get_log_file_path()
    file_exists = os.path.isfile(path)

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")

    # تعريف أعمدة الجدول

    # تجهيز السطر (Row) ووضع الرسالة في العمود المناسب للفئة
    row = {
        "Date (dd/mm/yyyy)": date_str,
        "Time (hh:mm:ss)": time_str,
        "Tourism": message if category == "Tourism" else "",
        "Business": message if category == "Business" else "",
        "Family/Friend Visit": message if "Family" in category else "",
        "Other (Medical, Cultural and sports, Entry Visa)": (
            message if "Other" in category else ""
        ),
    }

    # الكتابة في الملف (Append)
    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=log_files_headers)
        if not file_exists:
            writer.writeheader()  # كتابة العناوين لو الملف جديد
        writer.writerow(row)


# ---------------------------------------------------------
# 2. دوال المتصفح والفحص
# ---------------------------------------------------------


def pay_appointment():
    """هذه الدالة يتم استدعاؤها عند إيجاد موعد في Tourism"""
    print("\n[!!!] SUCCESS: Appointment Found! Starting Payment Logic...")
    pass


def get_alert_content():
    """قراءة نص التنبيه من الصفحة"""
    global driver
    try:
        driver.wait_for_element_visible(tracking_config["alert_selector"], timeout=7)
        return driver.get_text(tracking_config["alert_selector"]).strip()
    except:
        return "No alert found / Loading error"


def select_visa_subcategory(name):
    """تغيير الـ Sub-category فقط"""
    global driver
    selector = 'mat-select[formcontrolname="visaCategoryCode"]'
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            driver.find_element(selector),
        )
        driver.js_click(selector)
        time.sleep(1)

        option_xpath = f"//mat-option[contains(normalize-space(.), '{name}')]"
        driver.wait_for_element_visible(option_xpath, timeout=5)
        driver.js_click(option_xpath)

        time.sleep(3)  # انتظار الـ Angular ليحدث البيانات
        return True
    except Exception as e:
        print(f"Error selecting {name}: {e}")
        return False


def run_vfs_monitor():
    """المحرك الرئيسي للفحص والتبديل واللوج"""
    global driver
    print("[System] VFS Continuous Monitor Started...")

    while True:
        # 1. فحص الهدف الأساسي (Tourism)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking: Tourism")
        if select_visa_subcategory("Tourism"):
            result = get_alert_content()

            # استدعاء دالة اللوج بدلاً من الكلاس القديم
            log_vfs_result("Tourism", result)

            if (
                "no appointment slots" not in result.lower()
                and "No alert found" not in result
            ):
                pay_appointment()
                break

        # 2. التبديل لفئة عشوائية لكسر الكاش
        random_alt = random.choice(tracking_config["alt_categories"])
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Switching to (Cache Buster): {random_alt}"
        )

        if select_visa_subcategory(random_alt):
            alt_result = get_alert_content()

            # استدعاء دالة اللوج للفئة البديلة
            log_vfs_result(random_alt, alt_result)

        # 3. انتظار عشوائي قبل العودة لـ Tourism
        sleep_time = random.randint(30, 60)
        print(f"[System] Sleeping for {sleep_time}s...")
        time.sleep(sleep_time)
