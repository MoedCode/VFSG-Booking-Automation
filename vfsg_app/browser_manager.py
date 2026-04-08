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
    timeout = 50
    start_time = time.time()

    found_selector = None

    # while time.time() - start_time < timeout:
    i = 0
    for i in range(0, 45):
        for selector in dashboard_config["selectors"]["start_booking"]:
            if driver.is_element_visible(selector):
                print(f"\n\n function <start_new_booking> {i} trials \n")

                found_selector = selector
                break
            time.sleep(1)
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


        driver.js_click(found_selector)
        return True
    except Exception as e:
        print(f"[Error] Failed to click Start Booking: {e}")
        return False


"""
def fill_appointment():
    global driver
    selectors = dashboard_config["booking_config"]["selectors"]
    field_map = [
                ("Choose your Application Centre*", selectors["fields"]["center"]),
                ("Choose your appointment category*", selectors["fields"]["category"]),
                ("Choose your sub-category*", selectors["fields"]["subcategory"])
                
            ]
    for label, selector in field_map:
        target_value = appointment_details.get(label)
        if not target_value:
            print(f"Not Match {f} ")
            continue
"""


def fill_appointment_details():
    global driver
    print("[System] Filling Appointment Details...")

    fields = dashboard_config["booking_config"]["mapped_fields"]
    print(fields)
    try:
        for label, selector in fields:
            target_value = appointment_details.get(label)
            if not target_value:
                continue
            print(f"[Action] Processing: {label} -> {target_value}")
            # 1. Wait for and scroll to the dropdown
            driver.wait_for_element_visible(selector, timeout=15)
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                driver.find_element(selector),
            )
            human_delay(1, 2)

            # 2. Click to open dropdown
            driver.js_click(selector)

            # 3. CRITICAL: Wait for the Material Overlay to appear
            # We wait for the 'cdk-overlay-container' which holds the options
            driver.wait_for_element_visible(".cdk-overlay-container", timeout=5)
            human_delay(1, 1.5)

            # 4. Use a 'Normalize-Space' XPath
            # This ignores extra spaces/newlines that VFS often adds to 'Tourism'
            option_xpath = (
                f"//mat-option[contains(normalize-space(.), '{target_value}')]"
            )

            if driver.is_element_present(option_xpath):
                print(f"[Action] Found {target_value}. Clicking...")
                # Scroll the option into view inside the dropdown list
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'nearest'});",
                    driver.find_element(option_xpath),
                )
                driver.js_click(option_xpath)

                # 5. Wait for VFS to refresh the next dropdown
                print(f"[System] Selected {target_value}. Waiting for site refresh...")
                human_delay(2.5, 4)
            else:
                print(f"[Warning] Could not find option: {target_value}")
                # Fallback for Sub-category
                if "sub-category" in label.lower():
                    print("[System] Fallback: Clicking first available option...")
                    driver.js_click("mat-option")
                    human_delay(2, 3)

        # 6. Final Check for Continue Button
        cont_btn = "button.btn-brand-orange"
        if driver.is_element_visible(cont_btn):
            # Check if button is disabled (VFS uses the 'aria-disabled' or 'disabled' attribute)
            is_disabled = driver.get_attribute(cont_btn, "disabled")
            if is_disabled == "true" or is_disabled == "":
                # Sometimes 'disabled' exists without a value
                print("[Error] Form invalid (Continue button disabled).")
                return False

            print("[System] Success! Clicking Continue.")
            driver.js_click(cont_btn)
            return True

    except Exception as e:
        print(f"[Error] Failed during form filling: {e}")
    return False
