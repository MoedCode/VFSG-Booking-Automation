# VFSG-Booking-Automation/app/main.py

from seleniumbase import Driver

# Allow running from project root (python -m app.main) or from app/ (python main.py)
try:
    from app.bot_actions import smart_wait, BotControlException
    from app.auth import run_login_sequence
    from app.__init__ import user, COOKIE_CHOICE
except ModuleNotFoundError:
    from bot_actions import smart_wait, BotControlException
    from auth import run_login_sequence
    from __init__ import user, COOKIE_CHOICE

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
