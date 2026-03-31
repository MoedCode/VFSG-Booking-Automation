//VFSG-Booking-Automation/cppapp/auth.cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include "VFSG_Booking.h"

// Assuming these are defined in your other converted files (bot_actions.cpp, appointment.cpp, elements.cpp)
void smart_wait(double seconds, WebDriver& driver);
void human_delay();
void human_typing_any(WebDriver& driver, const std::vector<std::string>& selectors, const std::string& text, const std::string& label);
void human_click(WebDriver& driver, const std::string& selector, const std::string& label, int timeout);
void inject_control_panel(WebDriver& driver);
void fill_appointment_details(WebDriver& driver, const std::map<std::string, std::string>& details);

// The custom exception we defined in main.cpp
class BotControlException : public std::exception {
    std::string message;
public:
    BotControlException(std::string msg) : message(msg) {}
    const char* what() const noexcept override { return message.c_str(); }
};

void run_login_sequence(WebDriver& driver, std::string email, std::string password, std::string cookie_pref) {
    std::cout << "\n--- Starting Login Sequence ---" << std::endl;
    std::cout << "Opening VFS Global: " << vfs_url << std::endl;
    
    // Equivalent to uc_open_with_reconnect
    driver.Get(vfs_url); 
    
    std::cout << "Injecting Control Panel..." << std::endl;
    inject_control_panel(driver);

    std::cout << "Waiting for cookie banner..." << std::endl;
    smart_wait(4, driver);

    // --- ERROR CHECK BLOCK: On Load ---
    if (driver.IsElementVisible("a:contains('Go back to home')")) {
        std::cout << "Detected a VFS Server Error on load. Attempting recovery..." << std::endl;
        driver.FindElement(By::Css("a:contains('Go back to home')")).Click();
        smart_wait(5, driver);
        throw BotControlException("RESTART");
    }

    // Cookie Handling
    std::string pref = cookie_pref;
    std::transform(pref.begin(), pref.end(), pref.begin(), ::tolower);
    try {
        if (pref == "all") {
            driver.FindElement(By::Css("button#onetrust-accept-btn-handler")).Click();
            std::cout << "Accepted all cookies." << std::endl;
        } else if (pref == "necessary") {
            driver.FindElement(By::Css("button.ot-pc-refuse-all-handler")).Click();
            std::cout << "Accepted necessary cookies." << std::endl;
        }
    } catch (...) {
        std::cout << "Cookie banner skipped or not found." << std::endl;
    }

    smart_wait(2, driver);

    std::cout << "Handling verification/CAPTCHA..." << std::endl;
    smart_wait(6, driver);
    // Note: uc_gui_click_captcha is specific to SeleniumBase. 
    // In C++, you'd need a custom implementation or manual solve.
    std::cout << "CAPTCHA auto-click simulated..." << std::endl;

    smart_wait(5, driver);
    inject_control_panel(driver);

    std::cout << "Inserting credentials..." << std::endl;
    try {
        std::vector<std::string> email_selectors = {
            "input[formcontrolname='username']", "input[type='email']", "input[name*='email' i]"
        };
        std::vector<std::string> password_selectors = {
            "input[formcontrolname='password']", "input[type='password']"
        };

        human_typing_any(driver, email_selectors, email, "email");
        smart_wait(1, driver);
        human_typing_any(driver, password_selectors, password, "password");
        smart_wait(1, driver);

        std::cout << "Triggering form validation..." << std::endl;
        driver.FindElement(By::Css("body")).Click();
        human_delay();

        std::cout << "Clicking Sign In..." << std::endl;
        smart_wait(1.2, driver);
        human_click(driver, "button.mat-btn-lg", "Sign In button", 8);
    } catch (const std::exception& e) {
        std::cout << "Login interaction failed: " << e.what() << std::endl;
        throw BotControlException("LOGIN_INTERACTION_FAILED");
    }

    std::cout << "Waiting to verify dashboard..." << std::endl;
    smart_wait(10, driver);

    if (driver.GetCurrentUrl().find("dashboard") != std::string::npos) {
        std::cout << "Login successful! Reached Dashboard." << std::endl;
        smart_wait(8, driver);

        bool transition_successful = false;
        for (int attempt = 0; attempt < 15; ++attempt) {
            if (driver.GetCurrentUrl().find("dashboard") == std::string::npos) {
                transition_successful = true;
                break;
            }
            std::cout << "Click Attempt " << (attempt + 1) << ": Firing JS overrides..." << std::endl;
            
            // Aggressive JS Click logic
            std::string aggressive_js = R"raw_js(
                let btns = document.getElementsByTagName('button');
                for(let i=0; i<btns.length; i++){
                    if(btns[i].innerText.includes('Start New Booking')){
                        btns[i].click();
                        return true;
                    }
                }
                return false;
            )raw_js";
            driver.ExecuteScript(aggressive_js);
            smart_wait(1.5, driver);
        }

        if (!transition_successful) throw BotControlException("BOOKING_BUTTON_FAILED");

        std::cout << "Proceeding to fill appointment details..." << std::endl;
        fill_appointment_details(driver, appointment_details);
    } else {
        std::cout << "Still on login page. Manual intervention may be needed." << std::endl;
    }
}