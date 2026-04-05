# VFSG-Booking-Automation/app/auth.py

import time

try:
    from app.bot_actions import (
        smart_wait,
        human_delay,
        human_typing_any,
        human_click,
        human_click_any,
        BotControlException,
    )

    # Import from the new standalone file
    from app.appointment import fill_appointment_details
    from app.element import inject_control_panel
    from app.__init__ import vfs_url, appointment_details
except ModuleNotFoundError:
    from bot_actions import (
        smart_wait,
        human_delay,
        human_typing_any,
        human_click,
        human_click_any,
        BotControlException,
    )

    # Import from the new standalone file
    from appointment import fill_appointment_details
    from elements import inject_control_panel
    from __init__ import vfs_url, appointment_details


def run_login_sequence(driver, email, password, cookie_pref):
    print("\n--- Starting Login Sequence ---")
    print(f"Opening VFS Global: {vfs_url}")
    driver.uc_open_with_reconnect(vfs_url, reconnect_time=6)

    print("Injecting Control Panel...")
    inject_control_panel(driver)

    print("Waiting for cookie banner...")
    smart_wait(4, driver)

    # --- ERROR CHECK BLOCK: On Load ---
    if driver.is_element_visible('a:contains("Go back to home")'):
        print("Detected a VFS Server Error (500, 504, or 429) on load.")
        print("Attempting to recover by clicking 'Go back to home'...")
        driver.click('a:contains("Go back to home")')
        smart_wait(5, driver)
        raise BotControlException("RESTART")

    pref = cookie_pref.strip().lower()
    try:
        if pref == "all":
            driver.click("button#onetrust-accept-btn-handler", timeout=2)
            print("Accepted all cookies.")
        elif pref == "necessary":
            driver.click("button.ot-pc-refuse-all-handler", timeout=2)
            print("Accepted necessary cookies.")
    except Exception:
        print("Cookie banner skipped or not found.")

    smart_wait(2, driver)

    print("Waiting for CAPTCHA to fully render before clicking...")
    smart_wait(6, driver)
    print("Handling verification/CAPTCHA...")
    try:
        driver.uc_gui_click_captcha()
    except Exception:
        print("CAPTCHA auto-click not needed or failed. Continuing...")

    smart_wait(5, driver)

    inject_control_panel(driver)

    print("Inserting credentials with human-like typing...")
    try:
        email_selectors = [
            'input[formcontrolname="username"]',
            'input[formcontrolname="userName"]',
            'input[formcontrolname="email"]',
            'input[type="email"]',
            'input[name*="email" i]',
            'input[placeholder*="email" i]',
        ]
        password_selectors = [
            'input[formcontrolname="password"]',
            'input[type="password"]',
            'input[name*="pass" i]',
            'input[placeholder*="password" i]',
        ]

        human_typing_any(driver, email_selectors, email, label="email")
        smart_wait(1, driver)

        human_typing_any(driver, password_selectors, password, label="password")
        smart_wait(1, driver)

        print("Triggering form validation...")
        driver.click("body")

        human_delay()

        print("Preparing to click Sign In with human-like motion...")
        smart_wait(1.2, driver)
        human_click(driver, "button.mat-btn-lg", label="Sign In button", timeout=8)

    except Exception as e:
        print(f"Could not interact with login fields securely: {e}")
        raise BotControlException("LOGIN_INTERACTION_FAILED")

    print("Waiting to verify dashboard...")
    smart_wait(10, driver)

    # --- ERROR CHECK BLOCK: Post-Login ---
    if driver.is_element_visible('a:contains("Go back to home")'):
        print("Detected a VFS Server Error (500, 504, or 429) after login attempt.")
        print("Attempting to recover by clicking 'Go back to home'...")
        driver.click('a:contains("Go back to home")')
        smart_wait(5, driver)
        raise BotControlException("RESTART")

    if "dashboard" in driver.get_current_url():
        print("Login successful! Reached Dashboard.")
        print("Waiting for the dashboard UI to render...")
        smart_wait(8, driver)

        print("Initiating Active Polling Loop for 'Start New Booking'...")

        transition_successful = False

        # ACTIVE POLLING LOOP: Continuously fire JS clicks until the URL leaves the dashboard
        for attempt in range(15):
            current_url = driver.get_current_url()

            # If the URL no longer contains "dashboard", the click worked and we moved pages
            if "dashboard" not in current_url:
                print("\nURL transitioned successfully! Leaving dashboard.")
                transition_successful = True
                break

            print(f"Click Attempt {attempt + 1}: Firing JS overrides...")

            # Method 1: SeleniumBase Native JS Click
            try:
                driver.js_click(
                    '//button[contains(normalize-space(), "Start New Booking")]'
                )
            except Exception:
                pass

            # Method 2: Raw DOM Javascript Execution
            aggressive_js = """
            let btns = document.getElementsByTagName('button');
            for(let i=0; i<btns.length; i++){
                if(btns[i].innerText.includes('Start New Booking') || btns[i].textContent.includes('Start New Booking')){
                    btns[i].click();
                    return true;
                }
            }
            return false;
            """
            try:
                driver.execute_script(aggressive_js)
            except Exception:
                pass

            # Pause to allow the VFS server to process the click and change the URL
            smart_wait(1.5, driver)

        if not transition_successful:
            print("All 15 polling attempts failed to trigger a page transition.")
            raise BotControlException("BOOKING_BUTTON_FAILED")

        # --- ERROR CHECK BLOCK: Post-Click ---
        if driver.is_element_visible('a:contains("Go back to home")'):
            print(
                "Detected a VFS Server Error (500, 504, or 429) after clicking 'Start New Booking'."
            )
            print("Attempting to recover by clicking 'Go back to home'...")
            driver.click('a:contains("Go back to home")')
            smart_wait(5, driver)
            raise BotControlException("RESTART")

        # --- Wait for the Application Details page to fully load ---
        print("Waiting for the Application Details page to render...")
        try:
            for _ in range(30):
                if "application-detail" in driver.get_current_url():
                    print("Verified target URL.")
                    break
                time.sleep(0.5)
        except Exception:
            pass

        smart_wait(3, driver)

        # 5. Execute Form Filling
        print("Proceeding to fill appointment details...")
        try:
            fill_appointment_details(driver, appointment_details)
        except Exception as e:
            print(f"Form filling interrupted: {e}")

    else:
        print("Still on login page. Manual intervention may be needed.")

    print(
        "Sequence complete. Monitoring buttons. You can click Stop or Restart in the browser."
    )

    while True:
        smart_wait(2, driver)
