# VFSG-Booking-Automation/vfs_app/main.py

from __init__ import *
from browser_manager import *
# Configuration



def main():
    global driver
    print("--- SeleniumBase Browser Controller ---")
    print("Commands: \\e (Exit All), \\ec (Close Chrome), \\o [url] (Open)")

    while True:
        try:
            raw_input = input("\nAction >> ").strip().lower()
            if not raw_input:
                continue

            # EXIT EVERYTHING
            if raw_input in ["\\e", "exit", "exit script"]:
                close_browser()
                print("Goodbye!")
                sys.exit(0)

            # CLOSE BROWSER ONLY
            elif raw_input in ["\\ec", "exit chrome"]:
                if driver:
                    close_browser()
                else:
                    print("[!] No active session.")

            # OPEN BROWSER
            elif raw_input.startswith(("\\oc", "open chrome")):
                parts = raw_input.split()
                # logic: if using "\o google.com" -> url is parts[1]
                # logic: if using "open chrome google.com" -> url is parts[2]
                url_to_open = None
                if raw_input.startswith("\\oc") and len(parts) > 1:
                    url_to_open = parts[1]
                elif raw_input.startswith("open chrome") and len(parts) > 2:
                    url_to_open = parts[2]

                open_browser(url_to_open if url_to_open else DEFAULT_URL)
                # time.sleep(7)
                print(f"=> {handle_cookies()} :", end="\t")
            else:

                print(f"[?] Unknown command: {raw_input}")

        except KeyboardInterrupt:
            print("\n[User] Force quit detected.")
            close_browser()
            sys.exit(0)
        except Exception as e:
            print(f"\n[Runtime Error] {e}")


if __name__ == "__main__":
    main()
