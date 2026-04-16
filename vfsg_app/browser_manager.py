# VFSG-Booking-Automation/vfs_app/browser_manager.py
from __init__ import *


def open_browser(url=None):
    """Opens a new Chrome instance with Undetected-Driver (UC) mode."""
    global driver
    if driver:
        print("[!] Chrome is already open. Use \\ec to close it first.")
        return

    target = url if url else DEFAULT_URL
    print(f"[System] Launching Stealth Chrome at: {target}")

    try:
        # uc=True enables Undetected-ChromeDriver mode
        # heading=False ensures the window is visible
        driver = Driver(browser="chrome", uc=True, headless=False)
        driver.get(target)
    except Exception as e:
        print(f"[Error] SeleniumBase failed to launch: {e}")


def close_browser():
    """Closes the browser using SeleniumBase internal cleanup."""
    global driver
    if driver:
        print("\n[System] Closing Chrome (SeleniumBase)...")
        try:
            # SeleniumBase Driver objects have quit built-in
            driver.quit()
        except:
            pass
        driver = None
        print("[System] Chrome closed.")


# Safety net for Ctrl+C
# atexit.register(close_browser)


def human_delay(min_time=1.2, max_time=3.5):
    """Simulates human-like waiting intervals."""
    time.sleep(random.uniform(min_time, max_time))


def click_button(selector="", selector_type="#"):
    global driver
    if not driver:
        return False, "no driver provided"
    if selector_type.lower().strip() in "class":
        selector_type = "."
    if selector_type.lower().strip() in "id":
        selector_type = "#"
    element = f"{selector_type}{selector}"
    if driver.is_element_visible(element):
        driver.click()


def handle_cookies():
    global driver
    choice = cookies["choice"]
    btn_id = cookies["buttons"]["id"][choice]
    human_delay(8, 10)
    try:
        # بنر VFS بيستخدم ID محدد وهو onetrust-accept-btn-handler
        if driver.is_element_visible("#onetrust-accept-btn-handler"):
            # driver.click("#onetrust-accept-btn-handler")

            driver.click(btn_id, timeout=2)
            print("[System] Cookies accepted.")
            return True
    except:
        pass
    return False


def login_to_vfs():
    global driver
    print("[System] Attempting to login...")
    human_delay(3, 5)
    try:
        # 1. Handle Email Input
        found_email = False
        for selector in auth_config["selectors"]["email"]:
            if driver.is_element_visible(selector):
                human_delay(1, 1.5)
                driver.type(selector, user["email"])
                found_email = True
                break
        if not found_email:
            print("[Error] Email field not found!")
            return False

        # 2. Handle Password Input
        found_pwd = False
        for selector in auth_config["selectors"]["password"]:
            if driver.is_element_visible(selector):
                human_delay(1, 1.5)
                driver.type(selector, user["pwd"])
                found_pwd = True
                break
        if not found_pwd:
            print("[Error] Password field not found!")
            return False

        # 3. Handle Submit Button Click
        human_delay(2, 3)  # Wait for the button to become enabled after typing
        found_submit = False
        for selector in auth_config["selectors"]["submit"]:
            if driver.is_element_visible(selector):
                print(f"[System] Clicking submit button: {selector}")
                driver.click(selector)
                human_delay(1, 2)
                found_submit = True
                break

        if not found_submit:
            print("[Warning] Submit button not found. Trying 'Enter' key...")
            human_delay(1, 2)
            driver.send_keys(auth_config["selectors"]["password"][0], "\n")
            return True

        return True

    except Exception as e:
        print(f"[Error] Login execution failed: {e}")
    return False


def handle_cookies():
    global driver
    btn_id = cookies["buttons"]["id"][cookies["choice"]]
    human_delay(4, 6)  # Wait for the banner to load
    try:
        if driver.is_element_visible("#onetrust-accept-btn-handler"):
            driver.click(btn_id)
            print("[System] Cookies handled.")
            return True
    except:
        pass
    return False


def start_new_booking():
    """Waits for the dashboard to load and clicks 'Start New Booking'."""
    global driver
    print("[System] Waiting for Dashboard to load...")

    # 1. Wait for any of the selectors to become visible (Timeout: 30 seconds)
    # This handles the 'empty page' delay you mentioned.
    timeout = 30
    start_time = time.time()

    found_selector = None

    while time.time() - start_time < timeout:
        for selector in dashboard_config["selectors"]["start_booking"]:
            if driver.is_element_visible(selector):
                found_selector = selector
                break
        if found_selector:
            break
        time.sleep(1)  # Check every second

    if not found_selector:
        print("[Error] Dashboard took too long to load or button not found.")
        return False

    # 2. Small human delay before clicking
    human_delay(2, 4)

    try:
        print(f"[System] Dashboard loaded. Clicking: {found_selector}")
        # Use js_click if a normal click is blocked by the Material ripple effect
        human_delay(1, 2)

        driver.js_click(found_selector)
        return True
    except Exception as e:
        print(f"[Error] Failed to click Start Booking: {e}")
        return False


import time
import random

# Your requested configuration structure
booking_config = {
    # Selector to verify the form actually loaded
    "form_container": "mat-card.form-card",
    "form_header": "h1:contains('Appointment Details')",
    # List of dictionaries for the fields and your desired answers
    "selections": [
        {
            "label_name": "Choose your Application Centre",
            "dropdown_selector": "mat-select[formcontrolname='centerCode']",
            "target_value": "The Netherlands Visa Application Centre, Cairo",
        },
        {
            "label_name": "Choose your appointment category",
            "dropdown_selector": "mat-select[formcontrolname='selectedSubvisaCategory']",
            "target_value": "Short Stay Visa - Type C",
        },
        {
            "label_name": "Choose your sub-category",
            "dropdown_selector": "mat-select[formcontrolname='visaCategoryCode']",
            "target_value": "Tourism",
        },
    ],
}


def fill_appointment_form():
    global driver
    print("[System] Attempting to fill the Appointment Form...")

    try:
        # STEP 1: Ensure the Booking Form Exists
        # We wait for the specific <mat-card> that holds the form
        print("[Action] Waiting for the booking form to appear...")
        driver.wait_for_element_visible(booking_config["form_container"], timeout=15)

        # Optional double-check: verify the header text
        if driver.is_element_visible(booking_config["form_header"]):
            print("[Success] 'Appointment Details' form detected.")
        else:
            print("[Warning] Form container found, but header is missing.")

        # STEP 2: Loop through each requested field in order
        for item in booking_config["selections"]:
            label = item["label_name"]
            selector = item["dropdown_selector"]
            target = item["target_value"]

            print(f"\n[Action] Processing: {label}")

            # Wait for the specific dropdown field to be visible in the DOM
            driver.wait_for_element_visible(selector, timeout=10)

            # Center the element to avoid "Click Intercepted" errors
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                driver.find_element(selector),
            )
            time.sleep(0.5)  # Brief pause after scrolling

            # STEP 3: Open the dropdown menu
            print(f"  -> Opening dropdown...")
            driver.js_click(selector)

            # STEP 4: Wait for the Angular Overlay (The list of choices) to appear
            # This is critical. The options don't exist until this pane appears.
            driver.wait_for_element_visible(".cdk-overlay-pane", timeout=10)

            # STEP 5: Click the desired option
            # We use an XPath with normalize-space to ensure exact text matching
            # even if VFS adds weird spaces or line breaks in their HTML
            option_xpath = f"//mat-option[contains(normalize-space(.), '{target}')]"

            print(f"  -> Selecting option: {target}")
            driver.wait_for_element_visible(option_xpath, timeout=5)
            driver.js_click(option_xpath)

            # STEP 6: Apply the requested human delay
            print("  -> Applying human delay...")
            human_delay(1, 2)

            # Additional safety: Wait for VFS to process the selection
            # When you pick a center, the next box is disabled for ~1-2 seconds while it loads categories
            time.sleep(1.5)

        print("\n[Success] All form fields filled successfully!")
        return True

    except Exception as e:
        print(f"\n[Critical Error] Failed while interacting with the form:\n{e}")
        return False
