# VFSG-Booking-Automation/app/appointment.py

try:
    from app.bot_actions import smart_wait, human_delay
except ModuleNotFoundError:
    from bot_actions import smart_wait, human_delay

def fill_appointment_details(driver, details):
    print("\n--- Starting Appointment Details Form ---")
    
    # Wait for the Appointment Details page to fully render
    smart_wait(5, driver)

    for question, answer in details.items():
        print(f"Attempting to select: '{answer}'...")
        try:
            # 1. Find and click the dropdown menu
            clean_question = question.replace("*", "").strip()
            dropdown_xpath = f'//mat-form-field[contains(., "{clean_question}")]//mat-select'

            driver.wait_for_element_visible(dropdown_xpath, timeout=15)
            driver.hover(dropdown_xpath)
            human_delay()
            driver.click(dropdown_xpath)

            # Brief pause to allow the Angular overlay animation
            smart_wait(1, driver)

            # 2. Find and click the correct option inside the opened menu overlay
            option_xpath = f'//mat-option//span[contains(text(), "{answer}")]'

            driver.wait_for_element_visible(option_xpath, timeout=10)
            driver.hover(option_xpath)
            human_delay()
            driver.click(option_xpath)

            print(f"Successfully selected: {answer}")
            
            # 3. Wait for the server to process the selection
            print("Waiting for the next field to synchronise...")
            smart_wait(4, driver)

        except Exception as e:
            print(f"Failed to process the field '{clean_question}': {e}")
            raise Exception(f"Form filling failed at: {clean_question}")

    print("All appointment details filled successfully!")