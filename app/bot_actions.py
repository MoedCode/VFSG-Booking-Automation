# VFSG-Booking-Automation/app/bot_actions.py

import time
import random

class BotControlException(Exception):
    pass

def get_button_action(driver):
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

def human_delay():
    delay = random.uniform(1.2, 3.5)
    time.sleep(delay)

def _small_human_pause(min_s=0.25, max_s=0.8):
    time.sleep(random.uniform(min_s, max_s))


def human_click(driver, selector, label="element", timeout=12):
    driver.wait_for_element_visible(selector, timeout=timeout)

    try:
        driver.scroll_to(selector)
    except Exception:
        pass

    _small_human_pause()

    try:
        driver.hover(selector)
    except Exception:
        pass

    _small_human_pause(0.3, 0.9)

    try:
        # Some SeleniumBase builds expose move_to_element
        driver.move_to_element(selector)
        _small_human_pause(0.3, 0.8)
    except Exception:
        pass

    # Click with slight jitter to feel less robotic
    try:
        driver.click_with_offset(
            selector,
            x_offset=random.randint(-3, 3),
            y_offset=random.randint(-3, 3),
        )
    except Exception:
        try:
            driver.uc_click(selector)
        except Exception:
            try:
                driver.click(selector)
            except Exception:
                # Final fallback: Native JS click to punch through invisible overlays
                driver.js_click(selector)

def human_click_any(driver, selectors, label="element", timeout=12):
    selector = _wait_for_any_visible(driver, selectors, timeout=timeout)
    if not selector:
        raise Exception(f"No visible selector found for {label}.")
    human_click(driver, selector, label=label, timeout=timeout)
    return selector

def smart_wait(seconds, driver):
    for _ in range(int(seconds * 2)):
        action = get_button_action(driver)
        if action == 'stop':
            raise BotControlException("STOP")
        elif action == 'restart':
            raise BotControlException("RESTART")
        time.sleep(0.5)

def _wait_for_any_visible(driver, selectors, timeout=12):
    end_time = time.time() + timeout
    while time.time() < end_time:
        for sel in selectors:
            try:
                if driver.is_element_visible(sel):
                    return sel
            except Exception:
                pass
        time.sleep(0.2)
    return None

def _js_set_value(driver, selector, text):
    js = """
    const sel = arguments[0];
    const val = arguments[1];
    const el = document.querySelector(sel);
    if (!el) return false;
    el.focus();
    el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
    """
    try:
        return bool(driver.execute_script(js, selector, text))
    except Exception:
        return False

def human_typing(driver, selector, text):
    driver.wait_for_element_visible(selector, timeout=10)
    driver.click(selector, timeout=5)
    smart_wait(0.5, driver)
    driver.clear(selector)
    smart_wait(0.5, driver)

    # Type each character individually using send_keys
    for char in text:
        driver.send_keys(selector, char)
        time.sleep(random.uniform(0.08, 0.25))

def human_typing_any(driver, selectors, text, label="field"):
    selector = _wait_for_any_visible(driver, selectors, timeout=15)
    if not selector:
        raise Exception(f"No visible selector found for {label}.")

    # First attempt: human-like typing
    try:
        human_typing(driver, selector, text)
        current_value = driver.get_attribute(selector, "value")
        if current_value and current_value.strip():
            return selector
    except Exception:
        pass

    # Second attempt: SeleniumBase type
    try:
        driver.type(selector, text)
        current_value = driver.get_attribute(selector, "value")
        if current_value and current_value.strip():
            return selector
    except Exception:
        pass

    # Final attempt: direct JS set with events
    if _js_set_value(driver, selector, text):
        return selector

    raise Exception(f"Failed to type into {label} using selector: {selector}")

def fill_appointment_details(driver, details):
    print("\n--- Starting Appointment Details Form ---")
    smart_wait(5, driver) 

    for question, answer in details.items():
        print(f"Attempting to select: '{answer}'...")
        try:
            clean_question = question.replace("*", "").strip()
            dropdown_xpath = f'//mat-form-field[contains(., "{clean_question}")]//mat-select'
            
            driver.wait_for_element_visible(dropdown_xpath, timeout=15)
            driver.hover(dropdown_xpath)
            human_delay()
            driver.click(dropdown_xpath)
            
            smart_wait(1, driver) 

            option_xpath = f'//mat-option//span[contains(text(), "{answer}")]'
            
            driver.wait_for_element_visible(option_xpath, timeout=10)
            driver.hover(option_xpath)
            human_delay()
            driver.click(option_xpath)
            
            print(f"Successfully selected: {answer}")
            print("Waiting for the next field to synchronise...")
            smart_wait(4, driver) 

        except Exception as e:
            print(f"Failed to process the field '{clean_question}': {e}")
            raise Exception(f"Form filling failed at: {clean_question}")

    print("All appointment details filled successfully!")
