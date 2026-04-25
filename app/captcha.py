# VFSG-Booking-Automation/app/captcha.py
import time
import winsound
from __init__ import driver

def monitor_and_solve_captcha(context="form", timeout=40):
    """
    مراقب كابتشا ذكي: يظل يبحث عن الكابتشا لمدة معينة (timeout).
    context: 'login' لصفحة الدخول أو 'form' لصفحة المواعيد.
    """
    if not driver:
        return False

    print(f"[Captcha] Monitoring started for {context} page (Timeout: {timeout}s)...")
    
    # السيلكتورز بناءً على تحديثات VFS و Cloudflare
    turnstile_selectors = [
        "div#cf-turnstile-wrapper",
        "iframe[src*='challenges.cloudflare.com']",
        "iframe[title*='security challenge']",
        "div.cf-turnstile"
    ]

    start_time = time.time()
    while time.time() - start_time < timeout:
        for selector in turnstile_selectors:
            try:
                if driver.is_element_present(selector) and driver.is_element_visible(selector):
                    print(f"[Captcha] detected! Attempting to interact...")
                    
                    # تنبيه صوتي للمستخدم
                    winsound.Beep(1000, 300)
                    
                    # محاولة النقر الآلي داخل الـ Iframe
                    try:
                        driver.switch_to_frame(selector)
                        # Cloudflare checkbox selector
                        checkbox = "input[type='checkbox']"
                        if driver.is_element_present(checkbox):
                            driver.js_click(checkbox)
                            print("[Captcha] Clicked checkbox inside iframe.")
                        driver.switch_to_default_content()
                    except:
                        driver.switch_to_default_content()

                    # انتظار كلمة Success! كما في الملف captcha[1].pdf
                    if wait_for_success(15):
                        return True
            except:
                continue
        
        # إذا لم يجدها، ينتظر ثانية ويكرر البحث
        time.sleep(1)
    
    print(f"[Captcha] Monitor finished. (No captcha found or already solved)")
    return True # نرجع True لنسمح للسكربت بالمتابعة في حال كانت الكابتشا اختيارية

def wait_for_success(timeout=10):
    """التحقق من ظهور نص Success! أو اختفاء حاوية الكابتشا"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # البحث عن كلمة Success في كامل الصفحة أو داخل عناصر الكابتشا
        if driver.is_text_visible("Success!", "div") or driver.is_text_visible("Success!", "span"):
            print("[Captcha] Status: SUCCESS confirmed.")
            return True
        
        # إذا اختفت الكابتشا تماماً، فهذا مؤشر جيد أيضاً
        if not driver.is_element_visible("iframe[title*='challenge']"):
             print("[Captcha] Container disappeared. Assuming success.")
             return True
             
        time.sleep(1)
    return False