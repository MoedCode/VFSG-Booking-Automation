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
    human_delay(5, 8)
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
    selectors = dashboard_config["booking_config"]["selectors"]

    try:
        field_map = [
            ("Choose your Application Centre*", selectors["fields"]["center"]),
            ("Choose your appointment category*", selectors["fields"]["category"]),
            ("Choose your sub-category*", selectors["fields"]["subcategory"]),
        ]

        for label, selector in field_map:
            target_value = appointment_details.get(label)
            if not target_value:
                continue

            print(f"[Action] Opening dropdown for: {label}")

            # 1. Wait for and click the dropdown
            driver.wait_for_element_visible(selector, timeout=15)
            # Use normal click first to trigger Angular events; fallback to js_click
            try:
                driver.click(selector)
            except:
                driver.js_click(selector)

            # 2. Wait for the overlay container to appear
            # VFS options usually appear in a global overlay div
            human_delay(1.0, 1.8)

            # 3. Find and click the option
            # We use a more robust XPath that looks for the mat-option itself
            option_xpath = (
                f"//mat-option//span[contains(normalize-space(), '{target_value}')]"
            )

            try:
                # Wait specifically for the option to be clickable
                driver.wait_for_element_clickable(option_xpath, timeout=10)
                print(f"[Action] Clicking option: {target_value}")
                driver.click(option_xpath)

                # CRITICAL: Wait for the dropdown to close and the site to process the choice
                # (VFS often reloads the sub-category list based on the category)
                human_delay(2.0, 3.0)

            except Exception:
                print(f"[Warning] Could not find or click option: {target_value}")
                # Optional: print available options for debugging
                # options = driver.find_elements("tag name", "mat-option")
                # print(f"Available: {[opt.text for opt in options]}")

        # 4. Handle the Continue Button
        cont_btn = selectors["continue_btn"]
        driver.wait_for_element_visible(cont_btn, timeout=10)

        # Check if the button is still disabled
        is_disabled = driver.get_attribute(cont_btn, "disabled")

        if is_disabled == "true" or is_disabled == "":
            print(
                "[Error] Form is invalid (Continue button disabled). Retrying final selection..."
            )
            # Sometimes a quick re-click of the last item helps trigger the UI
            return False

        print("[System] Form valid. Clicking Continue...")
        driver.js_click(cont_btn)
        return True

    except Exception as e:
        print(f"[Error] Failed to fill form: {e}")
    return False
