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
        driver.move_to_element(selector)
        _small_human_pause(0.3, 0.8)
    except Exception:
        pass

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

    for char in text:
        driver.send_keys(selector, char)
        time.sleep(random.uniform(0.08, 0.25))

def human_typing_any(driver, selectors, text, label="field"):
    selector = _wait_for_any_visible(driver, selectors, timeout=15)
    if not selector:
        raise Exception(f"No visible selector found for {label}.")

    try:
        human_typing(driver, selector, text)
        current_value = driver.get_attribute(selector, "value")
        if current_value and current_value.strip():
            return selector
    except Exception:
        pass

    try:
        driver.type(selector, text)
        current_value = driver.get_attribute(selector, "value")
        if current_value and current_value.strip():
            return selector
    except Exception:
        pass

    if _js_set_value(driver, selector, text):
        return selector

    raise Exception(f"Failed to type into {label} using selector: {selector}")