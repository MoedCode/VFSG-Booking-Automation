from seleniumbase import Driver
import time
import random

# A custom exception to control the flow of the bot
class BotControlException(Exception):
    pass

def human_delay():
    # Pauses the script for a random decimal amount of seconds to mimic human hesitation
    delay = random.uniform(1.2, 3.5)
    time.sleep(delay)

def inject_control_panel(driver):
    # JavaScript to inject a floating control panel with Stop and Restart buttons
    js_code = """
    if (!document.getElementById('yalla-visa-panel')) {
        let panel = document.createElement('div');
        panel.id = 'yalla-visa-panel';
        panel.style.position = 'fixed';
        panel.style.top = '20px';
        panel.style.right = '20px';
        panel.style.zIndex = '999999';
        panel.style.backgroundColor = 'white';
        panel.style.padding = '10px';
        panel.style.border = '2px solid #ccc';
        panel.style.borderRadius = '8px';
        panel.style.display = 'flex';
        panel.style.gap = '10px';
        panel.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        
        // Stop Button
        let stopBtn = document.createElement('button');
        stopBtn.id = 'yalla-stop-btn';
        stopBtn.innerHTML = '🛑 Stop Bot';
        stopBtn.style.cssText = 'padding:10px 15px; background-color:#dc3545; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; font-size:14px;';
        stopBtn.onclick = function() { 
            this.setAttribute('data-action', 'stop'); 
            this.innerHTML = 'Stopping...'; 
        };
        
        // Restart Button
        let restartBtn = document.createElement('button');
        restartBtn.id = 'yalla-restart-btn';
        restartBtn.innerHTML = '🔄 Restart Process';
        restartBtn.style.cssText = 'padding:10px 15px; background-color:#ffc107; color:black; border:none; border-radius:5px; cursor:pointer; font-weight:bold; font-size:14px;';
        restartBtn.onclick = function() { 
            this.setAttribute('data-action', 'restart'); 
            this.innerHTML = 'Restarting...'; 
        };
        
        panel.appendChild(stopBtn);
        panel.appendChild(restartBtn);
        document.body.appendChild(panel);
    }
    """
    try:
        driver.execute_script(js_code)
    except Exception:
        pass # Ignore errors if the page is currently reloading

def get_button_action(driver):
    # Checks the HTML attributes to see if a button was clicked
    try:
        stop_clicked = driver.execute_script("return document.getElementById('yalla-stop-btn')?.getAttribute('data-action');")
        if stop_clicked == 'stop':
            return 'stop'
        
        restart_clicked = driver.execute_script("return document.getElementById('yalla-restart-btn')?.getAttribute('data-action');")
        if restart_clicked == 'restart':
            return 'restart'
    except Exception:
        pass
    return None

def smart_wait(seconds, driver):
    # Replaces time.sleep(). Checks the UI buttons every 0.5 seconds while waiting.
    for _ in range(int(seconds * 2)):
        action = get_button_action(driver)
        if action == 'stop':
            raise BotControlException("STOP")
        elif action == 'restart':
            raise BotControlException("RESTART")
        time.sleep(0.5)

def run_login_sequence(driver, email, password, cookie_pref):
    vfs_url = "https://visa.vfsglobal.com/egy/en/nld/login"
    
    print("\n--- Starting Login Sequence ---")
    print(f"Opening VFS Global: {vfs_url}")
    driver.uc_open_with_reconnect(vfs_url, reconnect_time=6)

    print("Injecting Control Panel...")
    inject_control_panel(driver)

    print("Waiting for cookie banner...")
    smart_wait(4, driver) 
    
    # 1. Handle Cookie Consent
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

    smart_wait(1, driver)

    # 2. Handle CAPTCHA
    print("Waiting for CAPTCHA to fully render before clicking...")
    smart_wait(6, driver) # Give Cloudflare time to build the iframe
    print("Handling verification/CAPTCHA...")
    try:
        driver.uc_gui_click_captcha()
    except Exception as e:
        print("CAPTCHA auto-click not needed or failed. Continuing...")
    
    smart_wait(5, driver)
    
    # Re-inject the panel just in case the page refreshed
    inject_control_panel(driver)

    # 3. Insert Credentials (Angular Fix Applied)
    print("Inserting credentials carefully for Angular...")
    try:
        # Click the field FIRST to trigger focus, then type
        driver.click('input[formcontrolname="username"]', timeout=5)
        smart_wait(0.5, driver)
        driver.type('input[formcontrolname="username"]', email)
        
        smart_wait(0.5, driver)
        
        driver.click('input[formcontrolname="password"]', timeout=5)
        smart_wait(0.5, driver)
        driver.type('input[formcontrolname="password"]', password)
        
        # Click the background body to force Angular to register the inputs
        print("Triggering form validation...")
        driver.click('body')
        
        print("Applying human delay before moving mouse to Sign In...")
        human_delay()
        
        print("Hovering over Sign In button...")
        try:
            driver.hover('button.mat-btn-lg')
            smart_wait(0.5, driver)
            
            print("Clicking Sign In...")
            driver.click('button.mat-btn-lg', timeout=5) 
        except Exception:
            print("Standard Sign In click failed. Forcing click via JavaScript...")
            driver.execute_script("document.querySelector('button.mat-btn-lg').click();")
            
    except Exception as e:
        print(f"Could not interact with login fields: {e}")

    print("Waiting to verify dashboard...")
    smart_wait(10, driver)
    
    # 4. Dashboard and Start New Booking
    if "dashboard" in driver.get_current_url():
        print("Login successful! Reached Dashboard.")
        print("Waiting for the dashboard UI to fully render...")
        smart_wait(4, driver) 
        
        print("Looking for 'Start New Booking' button...")
        try:
            driver.wait_for_text("Start New Booking", timeout=20)
            print("Text found. Applying human hesitation...")
            human_delay() 
            
            button_selector = 'button:contains("Start New Booking")'
            print("Moving mouse cursor to 'Start New Booking'...")
            driver.hover(button_selector)
            human_delay()
            
            driver.click(button_selector, timeout=5)
            print("Clicked 'Start New Booking' successfully.")
            smart_wait(5, driver)
            
        except Exception as e:
            print("Standard click failed, attempting fallback Angular selector...")
            try:
                fallback_xpath = '//*[contains(text(), "Start New Booking")]/ancestor-or-self::button'
                human_delay() 
                
                print("Moving mouse cursor to fallback element...")
                driver.hover(fallback_xpath)
                smart_wait(0.5, driver)
                
                driver.click(fallback_xpath, timeout=10)
                print("Clicked 'Start New Booking' using fallback XPath.")
                smart_wait(5, driver)
                
            except Exception as fallback_e:
                print("Standard clicks failed. Forcing via JavaScript...")
                try:
                    js_click = """
                    let buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        if (btn.innerText.includes('Start New Booking')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                    """
                    if driver.execute_script(js_click):
                        print("Forced click successful via JavaScript.")
                    else:
                        print("Could not find the button via JavaScript.")
                except Exception as js_e:
                    print(f"JavaScript click also failed: {js_e}")
            
    else:
        print("Still on login page. Manual intervention may be needed.")
        
    print("Sequence complete. Monitoring buttons. You can click Stop or Restart in the browser.")
    
    while True:
        smart_wait(2, driver)
def main():
    USER_EMAIL = "sirmohamedh@gmail.com"
    USER_PASS = "Moed!vsfG@26"
    COOKIE_CHOICE = "All" 
    
    # Initialize the browser once
    driver = Driver(uc=True, headless=False)
    
    # The outer loop allows the "Restart" button to work
    while True:
        try:
            run_login_sequence(driver, USER_EMAIL, USER_PASS, COOKIE_CHOICE)
            
        except BotControlException as control:
            command = str(control)
            if command == "STOP":
                print("\n🛑 Stop command received from the browser! Ending the script...")
                break 
                
            elif command == "RESTART":
                print("\n🔄 Restart command received! Restarting the sequence...")
                continue 
                
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Automatically restarting in 5 seconds... (Click Stop in the browser to cancel)")
            try:
                # Give the user 5 seconds to click Stop if it's stuck in an error loop
                smart_wait(5, driver)
            except BotControlException as control:
                if str(control) == "STOP":
                    print("\n🛑 Stop command received! Ending the script...")
                    break
    
    print("Shutting down the WebDriver...")
    driver.quit()

if __name__ == "__main__":
    main()