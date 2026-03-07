import time
from playwright.sync_api import sync_playwright

# Configuration variables
WAIT_TIME_SECONDS = 300  # 5 minutes

def run_vfs_bot(playwright):
    # Connect to the already running Chrome browser via debugging port
    print("Connecting to the existing browser...")
    try:
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    except Exception as e:
        print("Failed to connect. Ensure Chrome is running with --remote-debugging-port=9222")
        return
    
    # Get the first context and the first page (your active tab)
    context = browser.contexts[0]
    page = context.pages[0]
    
    print(f"Successfully connected to page: {page.url}")
    
    # Ensure we are on the dashboard before starting the loop
    if "dashboard" not in page.url and "appointment" not in page.url:
        print("Please navigate to the VFS dashboard first.")
        return

    booking_in_progress = True
    while booking_in_progress:
        try:
            # Click 'Start New Booking' if the button is visible on the dashboard
            if page.locator("button:has-text('Start New Booking')").is_visible():
                page.click("button:has-text('Start New Booking')")
                # Wait for the dropdown menus to render
                page.wait_for_selector("mat-select", timeout=10000)

            print("Selecting booking categories...")
            
            # Select Application Centre 
            page.click("mat-select:nth-child(1)") 
            page.click("mat-option:has-text('The Netherlands Visa Application Centre, Cairo')")

            # Select Appointment Category
            page.click("mat-select:nth-child(2)")
            page.click("mat-option:has-text('Short Stay Visa - Type C')")

            # Select Sub-category (Tourism)
            page.click("mat-select:nth-child(3)")
            page.click("mat-option:has-text('Tourism')")

            # Wait briefly for the VFS API to return slot availability
            time.sleep(3) 
            
            # Check for the specific error message indicating no slots
            no_slots_msg = page.locator("text='We are sorry but no appointment slots are currently available'")
            
            if no_slots_msg.is_visible():
                print("No slots available. Waiting for 5 minutes...")
                # Refresh the state by returning to the dashboard
                page.goto("https://visa.vfsglobal.com/egy/en/nld/dashboard")
                time.sleep(WAIT_TIME_SECONDS)
            else:
                print("Appointment slot found! Proceeding to the next step...")
                # Click Continue to lock the slot
                page.click("button:has-text('Continue')")
                
                print("Reached the applicant details stage. Stopping the automated loop.")
                booking_in_progress = False 

        except Exception as e:
            print(f"An error occurred during the process: {e}")
            print("Refreshing and retrying in 5 minutes...")
            page.goto("https://visa.vfsglobal.com/egy/en/nld/dashboard")
            time.sleep(WAIT_TIME_SECONDS)

    print("Automation paused. Please proceed with the payment gateway manually.")

with sync_playwright() as playwright:
    run_vfs_bot(playwright)