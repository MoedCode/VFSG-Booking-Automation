//VFSG-Booking-Automation/cppapp/bot_actions.cpp
#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <thread>
#include <chrono>
#include "VFSG_Booking.h"
#include <webdriverxx/webdriverxx.h> // Or the specific path to your C++ WebDriver library
using namespace webdriverxx;        // If the library uses this namespace
// Re-declaring the Exception for local use
std::string get_button_action(WebDriver& driver);
class BotControlException : public std::exception {
    std::string message;
public:
    BotControlException(std::string msg) : message(msg) {}
    const char* what() const noexcept override { return message.c_str(); }
};

// --- Helper Functions ---

void _small_human_pause(float min_s = 0.25f, float max_s = 0.8f) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> dist(min_s, max_s);
    int ms = static_cast<int>(dist(gen) * 1000);
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

void human_delay() {
    _small_human_pause(1.2f, 3.5f);
}

// --- UI Control Logic ---

std::string get_button_action(WebDriver& driver) {
    try {
        // Checking for Stop button data-action attribute
        auto stop_status = driver.ExecuteScript(
            "return document.getElementById('yalla-stop-btn')?.getAttribute('data-action');"
        );
        if (stop_status.IsString() && stop_status.AsString() == "stop") return "stop";

        // Checking for Restart button data-action attribute
        auto restart_status = driver.ExecuteScript(
            "return document.getElementById('yalla-restart-btn')?.볍getAttribute('data-action');"
        );
        if (restart_status.IsString() && restart_status.AsString() == "restart") return "restart";
    } catch (...) {}
    return "";
}

void smart_wait(double seconds, WebDriver& driver) {
    auto start_time = std::chrono::steady_clock::now();
    while (true) {
        auto elapsed = std::chrono::steady_clock::now() - start_time;
        if (std::chrono::duration_cast<std::chrono::seconds>(elapsed).count() >= seconds) break;

        std::string action = get_button_action(driver);
        if (action == "stop") throw BotControlException("STOP");
        if (action == "restart") throw BotControlException("RESTART");

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

// --- Interaction Logic ---

void human_click(WebDriver& driver, const std::string& selector, const std::string& label = "element", int timeout = 12) {
    std::cout << "Attempting human click on: " << label << std::endl;
    
    // 1. Scroll & Pause
    try {
        auto element = driver.FindElement(By::Css(selector));
        driver.ExecuteScript("arguments[0].scrollIntoView();", element);
    } catch (...) {}
    _small_human_pause();

    // 2. Hover & Move
    try {
        auto element = driver.FindElement(By::Css(selector));
        auto actions = MoveTo(element);
        _small_human_pause(0.3f, 0.9f);
        actions.Perform();
    } catch (...) {}

    // 3. Click with Random Offset
    try {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dist(-3, 3);
        
        auto element = driver.FindElement(By::Css(selector));
        auto actions = MoveTo(element);
        actions.MoveByOffset(dist(gen), dist(gen)).Click().Perform();
    } catch (...) {
        // Fallback to standard click if offset fails
        driver.FindElement(By::Css(selector)).Click();
    }
}

void human_typing(WebDriver& driver, const std::string& selector, const std::string& text) {
    auto element = driver.FindElement(By::Css(selector));
    element.Click(); // Focus
    _small_human_pause(0.4f, 0.6f);
    element.Clear();
    _small_human_pause(0.4f, 0.6f);

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> type_dist(0.08f, 0.25f);

    for (char c : text) {
        std::string s(1, c);
        element.SendKeys(s);
        int delay_ms = static_cast<int>(type_dist(gen) * 1000);
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    }
}

void human_typing_any(WebDriver& driver, const std::vector<std::string>& selectors, const std::string& text, const std::string& label = "field") {
    for (const auto& sel : selectors) {
        try {
            if (driver.FindElement(By::Css(sel)).IsDisplayed()) {
                human_typing(driver, sel, text);
                return;
            }
        } catch (...) {}
    }
    throw std::runtime_error("Could not find visible selector for " + label);
}