# VFSG-Booking-Automation/app/main.py

from seleniumbase import Driver
import time
import random

# Allow running from project root (python -m app.main) or from app/ (python main.py)
try:
    from app.bot_actions import (
        smart_wait,
        human_delay,
        human_typing,
        human_typing_any,
        human_click,
        BotControlException,
        fill_appointment_details,
    )
    from app.elements import inject_control_panel
    from app.__init__ import *
except ModuleNotFoundError:
    from bot_actions import (
        smart_wait,
        human_delay,
        human_typing,
        human_typing_any,
        human_click,
        BotControlException,
        fill_appointment_details,
    )
    from elements import inject_control_panel
    from __init__ import *

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
            driver.click('button#onetrust-accept-btn-handler', timeout=2)
            print("Accepted all cookies.")
        elif pref == "necessary":
            driver.click('button.ot-pc-refuse-all-handler', timeout=2)
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
        driver.click('body')

        human_delay()

        print("Preparing to click Sign In with human-like motion...")
        smart_wait(1.2, driver)
        human_click(driver, 'button.mat-btn-lg', label="Sign In button", timeout=8)

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
        smart_wait(5, driver)

        print("Looking for 'Start New Booking' text...")
        try:
            target_selector = "contains:Start New Booking"

            driver.wait_for_element_visible(target_selector, timeout=20)
            print("Element is fully visible on screen. Applying human hesitation...")
            human_delay()

            print("Approaching 'Start New Booking' with human-like motion...")
            smart_wait(1.5, driver)
            try:
                human_click(driver, target_selector, label="Start New Booking", timeout=10)
                print("Clicked 'Start New Booking' with human-like click.")
            except Exception:
                print("Human click failed. Trying tag-agnostic JS click as fallback...")
                driver.js_click(target_selector)
                print("Clicked 'Start New Booking' via JS fallback.")

        except Exception as fallback_e:
            print(f"All standard and JS clicks failed: {fallback_e}")
            raise BotControlException("BOOKING_BUTTON_FAILED")

        # --- ERROR CHECK BLOCK: Post-Click ---
        if driver.is_element_visible('a:contains("Go back to home")'):
            print("Detected a VFS Server Error (500, 504, or 429) after clicking 'Start New Booking'.")
            print("Attempting to recover by clicking 'Go back to home'...")
            driver.click('a:contains("Go back to home")')
            smart_wait(5, driver)
            raise BotControlException("RESTART")

        # --- Wait for the URL transition ---
        print("Waiting for the Application Details page to load...")
        try:
            for _ in range(30): 
                if "application-detail" in driver.get_current_url():
                    print("URL changed successfully. Proceeding to form.")
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

    print("Sequence complete. Monitoring buttons. You can click Stop or Restart in the browser.")

    while True:
        smart_wait(2, driver)

def main():
    driver = Driver(uc=True, headless=False)

    while True:
        try:
            run_login_sequence(driver, user["email"], user["pwd"], COOKIE_CHOICE)

        except BotControlException as control:
            command = str(control)
            if command == "STOP":
                print("\n🛑 Stop command received from the browser! Ending the script...")
                break

            elif command == "RESTART":
                print("\n🔄 Restart command received! Restarting the sequence...")
                continue

            elif command in ["LOGIN_INTERACTION_FAILED", "BOOKING_BUTTON_FAILED"]:
                print(f"\nFailed to interact securely ({command}). Waiting 15 minutes before retrying to prevent account restriction...")
                try:
                    smart_wait(900, driver)
                except BotControlException as sub_control:
                    if str(sub_control) == "STOP":
                        print("\n🛑 Stop command received! Ending the script...")
                        break
                    elif str(sub_control) == "RESTART":
                        continue

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Waiting 15 minutes to prevent IP/User ID ban... (Click Stop in the browser to cancel)")
            try:
                smart_wait(900, driver)
            except BotControlException as control:
                if str(control) == "STOP":
                    print("\n🛑 Stop command received! Ending the script...")
                    break
                elif str(control) == "RESTART":
                    continue
    
    print("Shutting down the WebDriver...")
    driver.quit()

if __name__ == "__main__":
    main()
