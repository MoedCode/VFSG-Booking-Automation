import re

try:
    from app.bot_actions import smart_wait, human_delay
except ModuleNotFoundError:
    from bot_actions import smart_wait, human_delay


def _xpath_literal(value):
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    parts = value.split('"')
    return 'concat(' + ', \'"\', '.join(f'"{part}"' for part in parts) + ')'


def _normalize_label(text):
    cleaned = text.replace("*", " ").strip().lower()
    cleaned = cleaned.replace("your ", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _wait_for_appointment_page(driver):
    print("Waiting for Appointment Details page...")
    driver.wait_for_text("Appointment Details", timeout=20)
    smart_wait(2, driver)


def _visible_dropdowns():
    return [
        '(//*[@role="combobox"])[1]',
        '(//*[@role="combobox"])[2]',
        '(//*[@role="combobox"])[3]',
    ]


def _candidate_dropdown_xpaths(question, index):
    question_literal = _xpath_literal(question.replace("*", "").strip())

    return [
        (
            f'(//mat-form-field['
            f'.//*[self::label or self::mat-label]'
            f'[contains(normalize-space(.), {question_literal})]'
            f']//*[self::mat-select or @role="combobox"])[1]'
        ),
        (
            f'(//*[contains(@class, "mat-mdc-form-field") or self::mat-form-field]'
            f'[.//*[contains(normalize-space(.), {question_literal})]]'
            f'//*[self::mat-select or @role="combobox"])[1]'
        ),
        _visible_dropdowns()[index],
    ]


def _find_dropdown(driver, question, index):
    normalized_question = _normalize_label(question)

    for xpath in _candidate_dropdown_xpaths(question, index):
        try:
            if driver.is_element_visible(xpath):
                text = driver.get_text(xpath).strip()
                if text:
                    normalized_text = _normalize_label(text)
                    if normalized_question in normalized_text or normalized_text in normalized_question:
                        return xpath
                return xpath
        except Exception:
            continue

    raise Exception(f"Could not locate dropdown for '{question}'")


def _is_value_already_selected(driver, dropdown_xpath, answer):
    try:
        selected_text = driver.get_text(dropdown_xpath).strip()
    except Exception:
        return False

    return _normalize_label(answer) in _normalize_label(selected_text)


def _open_dropdown(driver, dropdown_xpath):
    driver.wait_for_element_visible(dropdown_xpath, timeout=15)

    try:
        driver.scroll_to(dropdown_xpath)
    except Exception:
        pass

    human_delay()

    try:
        driver.click(dropdown_xpath)
    except Exception:
        driver.js_click(dropdown_xpath)

    smart_wait(1, driver)


def _option_xpaths(answer):
    answer_literal = _xpath_literal(answer)
    return [
        f'(//*[@role="option"][contains(normalize-space(.), {answer_literal})])[1]',
        f'(//mat-option[contains(normalize-space(.), {answer_literal})])[1]',
        f'(//*[contains(@class, "mat-mdc-option")][contains(normalize-space(.), {answer_literal})])[1]',
        f'(//span[contains(normalize-space(.), {answer_literal})])[1]',
        f'(//div[contains(normalize-space(.), {answer_literal})])[1]',
    ]


def _click_answer_option(driver, answer):
    for xpath in _option_xpaths(answer):
        try:
            if not driver.is_element_visible(xpath):
                continue

            try:
                driver.scroll_to(xpath)
            except Exception:
                pass

            human_delay()

            try:
                driver.click(xpath)
            except Exception:
                driver.js_click(xpath)

            smart_wait(1, driver)
            return
        except Exception:
            continue

    raise Exception(f"Could not locate option '{answer}'")


def _select_dropdown_answer(driver, question, answer, index):
    dropdown_xpath = _find_dropdown(driver, question, index)
    clean_question = question.replace("*", "").strip()

    if _is_value_already_selected(driver, dropdown_xpath, answer):
        print(f"'{clean_question}' is already set to '{answer}'")
        return

    print(f"Opening '{clean_question}'...")
    _open_dropdown(driver, dropdown_xpath)

    print(f"Selecting '{answer}'...")
    _click_answer_option(driver, answer)

    for _ in range(12):
        if _is_value_already_selected(driver, dropdown_xpath, answer):
            print(f"Confirmed '{answer}' for '{clean_question}'")
            return
        smart_wait(0.5, driver)

    raise Exception(f"Selection was not applied for '{clean_question}'")


def fill_appointment_details(driver, details):
    print("\n--- Starting Appointment Details Form ---")
    _wait_for_appointment_page(driver)

    for index, (question, answer) in enumerate(details.items()):
        try:
            _select_dropdown_answer(driver, question, answer, index)
            print("Waiting for dependent fields to refresh...")
            smart_wait(3, driver)
        except Exception as e:
            clean_question = question.replace("*", "").strip()
            print(f"Failed to process the field '{clean_question}': {e}")
            raise Exception(f"Form filling failed at: {clean_question}")

    print("All appointment details filled successfully!")