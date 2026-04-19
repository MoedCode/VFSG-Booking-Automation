import time
import random
import winsound
from datetime import datetime
from __init__ import *

# ---------------------------------------------------------
# دوال التنبيه وتسجيل الخروج
# ---------------------------------------------------------


def alert_user():
    """تشغيل صوت تنبيه متكرر لجذب انتباه العميل"""
    print("\n[!!!] ATTENTION: SLOT FOUND! [!!!]")
    for _ in range(5):
        winsound.Beep(1000, 500)  # تردد 1000 هرتز لمدة نصف ثانية
        time.sleep(0.1)


def log_out():
    """تسجيل الخروج من الحساب في حال عدم وجود مواعيد"""
    global driver
    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] [System] No slots found after switch process. Logging out..."
    )
    try:
        # 1. الضغط على القائمة المنسدلة "My Account"
        driver.wait_for_element_visible("a#navbarDropdown", timeout=5)
        driver.js_click("a#navbarDropdown")
        time.sleep(1)

        # 2. الضغط على زر "Logout"
        logout_btn = "a.dropdown-item.bg-brand-orange"
        driver.wait_for_element_visible(logout_btn, timeout=5)
        driver.js_click(logout_btn)

        print("[System] Logged out successfully.")
        time.sleep(3)
    except Exception as e:
        print(f"[Error] Failed to log out: {e}")


def handle_success():
    """يتم استدعاؤها عند إيجاد الموعد: تضغط استمرار، تنبه العميل، وتنتظر 3-5 دقائق"""
    global driver
    try:
        # الضغط على زر Continue (الزر البرتقالي في نهاية الفورم)
        continue_btn = "button.btn-brand-orange"
        driver.wait_for_element_visible(continue_btn, timeout=5)
        driver.js_click(continue_btn)
        print("[Action] Clicked 'Continue' button successfully!")
    except Exception as e:
        print(f"[Error] Could not click 'Continue': {e}")

    # تنبيه العميل
    alert_user()
    print("[System] Please complete the manual steps (Payment/Details).")

    # انتظار من 3 إلى 5 دقائق (180 إلى 300 ثانية) كما طلبت
    wait_time = random.randint(180, 300)
    print(
        f"[System] Pausing bot for {wait_time // 60} minutes and {wait_time % 60} seconds..."
    )
    time.sleep(wait_time)
    print("[System] Resuming tracking process...")


# ---------------------------------------------------------
# دوال المتصفح والفحص
# ---------------------------------------------------------


def get_alert_content():
    """قراءة نص التنبيه من الصفحة"""
    global driver
    try:
        driver.wait_for_element_visible(tracking_config["alert_selector"], timeout=5)
        return driver.get_text(tracking_config["alert_selector"]).strip()
    except:
        return "No alert found"


def select_visa_subcategory(name):
    """تغيير الـ Sub-category من القائمة المنسدلة"""
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
        print(f"[Error] Failed to select category '{name}': {e}")
        return False


def run_vfs_monitor():
    """المحرك الرئيسي للصيد والتبديل (Switch Process)"""
    global driver
    print("[System] VFS Hunter Started... Listening to GUI Target.")

    all_categories = [
        "Tourism",
        "Business",
        "Family/Friend Visit",
        "Other (Medical, Cultural and sports, Entry Visa)",
    ]

    while True:
        # قراءة الهدف الحالي من الـ GUI (الإعداد الافتراضي Tourism)
        target = tracking_config.get("main_target", "Tourism")
        print(f"\n{'-'*40}")
        print(f"🎯 HUNTING TARGET: {target}")
        print(f"{'-'*40}")

        # --- الخطوة 1: الفحص المبدئي للهدف ---
        select_visa_subcategory(target)
        initial_alert = get_alert_content()

        # إذا وجد موعداً للهدف في الفحص الأول
        if (
            "no appointment slots" not in initial_alert.lower()
            and "no alert found" not in initial_alert.lower()
        ):
            print(f"[SUCCESS] Slots found immediately for {target}!")
            handle_success()
            continue  # يبدأ الدورة من جديد بعد الانتظار 3-5 دقائق

        # --- الخطوة 2: عملية التبديل (Switch Process) ---
        print("[Info] No slots available. Starting Switch Process...")

        # ترتيب الفئات عشوائياً (مثلاً 1, 4, 2, 3)
        shuffled_cats = all_categories.copy()
        random.shuffle(shuffled_cats)

        target_found_in_switch = False

        for cat in shuffled_cats:
            print(f" -> Switching to: {cat}")
            select_visa_subcategory(cat)

            # انتظار بشري بين 1 إلى 5 ثواني كما طلبت
            time.sleep(random.uniform(1, 5))

            # نقرأ التنبيه للفئة الحالية
            current_alert = get_alert_content()

            # نحن نهتم فقط إذا كانت الفئة الحالية في اللفة هي "هدف العميل" ووجدنا فيها موعداً
            if cat == target:
                if (
                    "no appointment slots" not in current_alert.lower()
                    and "no alert found" not in current_alert.lower()
                ):
                    print(f"[SUCCESS] Slots found for {target} during switch process!")
                    handle_success()
                    target_found_in_switch = True
                    break  # نوقف دورة التبديل لأننا وجدنا الموعد

        # --- الخطوة 3: ما بعد عملية التبديل ---
        if target_found_in_switch:
            # إذا وجد موعد، يعود لبداية اللوب الرئيسي (بعد أن يكون قد انتظر 3-5 دقائق)
            continue

        # إذا انتهت عملية التبديل العشوائي (مر على 4 فئات) ولم يجد موعداً للهدف
        log_out()

        # ملاحظة: بعد تسجيل الخروج، نكسر حلقة البحث لإيقاف البوت.
        # يجب على العميل إعادة تسجيل الدخول (أو يمكنك برمجة إعادة الدخول لاحقاً).
        break
