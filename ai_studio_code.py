import os
from datetime import datetime
import random
import time
from __init__ import *

# --- الإعدادات الجديدة لعملية الفحص المستمر ---
CHECK_CONFIG = {
    "categories": [
        "Tourism", 
        "Business", 
        "Family/Friend Visit", 
        "Other (Medical, Cultural and sports, Entry Visa)"
    ],
    "main_target": "Tourism",
    "alert_selector": 'div[role="alert"]', # السليكتور بتاع رسالة الـ No Slots أو الـ Available
    "log_folder": "logs"
}

class SlotLogger:
    """مسئول عن إنشاء ملفات اللوج اليومية وتنسيق الجدول"""
    def __init__(self):
        if not os.path.exists(CHECK_CONFIG["log_folder"]):
            os.makedirs(CHECK_CONFIG["log_folder"])

    def get_file_path(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(CHECK_CONFIG["log_folder"], f"log_{date_str}.txt")

    def write_header(self):
        path = self.get_file_path()
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                f.write(f"{timestamp}\n")
                f.write("-" * 120 + "\n")
                header = f"{'attempts':<15} | {'Tourism':<25} | {'Business/Family':<25} | {'Other':<25}\n"
                f.write("-" * 120 + "\n")
                f.write(header)
                f.write("-" * 120 + "\n")

    def log_attempt(self, attempt_num, results):
        # results expected to be a dict: {"Tourism": "text", "Business": "text", ...}
        path = self.get_file_path()
        with open(path, "a", encoding="utf-8") as f:
            # توزيع النتائج على الأعمدة (تبسيط للجدول)
            res_tourism = results.get("Tourism", "N/A")[:23]
            res_biz_fam = results.get("Business", "N/A")[:23] # دمجناهم للتبسيط في العرض
            res_other = results.get("Other", "N/A")[:23]
            
            line = f"{attempt_num:<15} | {res_tourism:<25} | {res_biz_fam:<25} | {res_other:<25}\n"
            f.write(line)
            
            # لو خلصنا لفة أو حصل تغيير في الوقت، ممكن نضيف فاصل (اختياري)
            # f.write("-" * 120 + "\n")

# تعريف الدالة الفاضية للدفع/الحجز كما طلبت
def pay_and_book_appointment():
    print("\n[!!!] SLOT FOUND IN TOURISM! Triggering Payment Function...")
    # هنا تضع كود إكمال البيانات والدفع
    pass

def get_alert_text():
    """تقرأ النص الموجود داخل الـ alert div"""
    global driver
    try:
        if driver.is_element_present(CHECK_CONFIG["alert_selector"]):
            return driver.get_text(CHECK_CONFIG["alert_selector"])
    except:
        pass
    return "No alert found"

def select_sub_category(category_name):
    """تغير التصنيف الفرعي فقط لسرعة الفحص"""
    global driver
    try:
        selector = 'mat-select[formcontrolname="visaCategoryCode"]'
        driver.wait_for_element_visible(selector, timeout=5)
        driver.js_click(selector)
        driver.wait_for_element_visible(".cdk-overlay-pane", timeout=5)
        
        option_xpath = f"//mat-option[contains(normalize-space(.), '{category_name}')]"
        driver.js_click(option_xpath)
        time.sleep(2) # انتظار تحديث الصفحة
        return True
    except Exception as e:
        print(f"[Error] Failed to select {category_name}: {e}")
        return False

def run_continuous_check():
    """الدالة الرئيسية للفحص والتبديل واللوجات"""
    global driver
    logger = SlotLogger()
    attempt_count = 1
    
    print("[System] Starting Continuous Slot Monitoring...")
    
    while True:
        logger.write_header() # التأكد من وجود الهيدر لو بدأنا يوم جديد
        
        current_results = {}
        
        # 1. فحص Tourism أولاً (الهدف الأساسي)
        print(f"\n[Attempt {attempt_count}] Checking Main Target: Tourism...")
        select_sub_category(CHECK_CONFIG["main_target"])
        res_text = get_alert_text()
        current_results["Tourism"] = res_text
        
        if "no appointment slots are currently available" not in res_text.lower():
            # إذا كانت الرسالة غير موجودة، يعني احتمال كبير فيه مواعيد!
            print("[Success] Possible slots found in Tourism!")
            pay_and_book_appointment()
            break # نخرج من اللوب ونبدأ عملية الحجز
        
        # 2. بما إن Tourism مفيش، نلف على الباقي عشوائياً عشان "نصحصح" السيرفر
        others = [c for c in CHECK_CONFIG["categories"] if c != CHECK_CONFIG["main_target"]]
        random.shuffle(others)
        
        for cat in others:
            print(f"  -> Cycling through: {cat}")
            select_sub_category(cat)
            res = get_alert_text()
            
            # تخزين النتيجة في اللوج (بشكل مبسط)
            if "Business" in cat: current_results["Business"] = res
            elif "Family" in cat: current_results["Family"] = res
            else: current_results["Other"] = res
            
            time.sleep(random.uniform(1, 3))
        
        # 3. تسجيل المحاولة كاملة في ملف اللوج
        logger.log_attempt(attempt_count, current_results)
        print(f"[Log] Attempt {attempt_count} saved to daily file.")
        
        attempt_count += 1
        # انتظار عشوائي قبل المحاولة القادمة لتجنب البلوك
        wait_time = random.randint(30, 120) 
        print(f"[System] Sleeping for {wait_time}s before next cycle...")
        time.sleep(wait_time)

# --- تعديل دالة fill_appointment_form لتدخل في مود الفحص ---
def fill_appointment_form():
    global driver
    print("[System] Attempting to fill the Appointment Form...")

    try:
        # تعبئة البيانات الأساسية (المركز والكاتيجوري الأساسي) أول مرة فقط
        # نستخدم نفس المنطق بتاعك في الكود السابق لملء أول خانتين
        # ... (كود ملء centerCode و selectedSubvisaCategory) ...
        
        # بدلاً من ملء Tourism والخروج، سنقوم بتشغيل الفحص المستمر
        run_continuous_check()
        return True

    except Exception as e:
        print(f"\n[Critical Error] Failed while interacting with the form:\n{e}")
        return False