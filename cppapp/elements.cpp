//VFSG-Booking-Automation/cppapp/elements.cpp
#include <iostream>
#include <string>
#include <webdriverxx/webdriverxx.h> // Example WebDriver library for C++

using namespace webdriverxx;

/**
 * Injects a floating control panel with Stop and Restart buttons into the browser.
 * This is the C++ conversion of the logic in element.py.
 */
void inject_control_panel(WebDriver& driver) {
    // JavaScript to inject a floating control panel
    // Using a Raw String Literal to handle the multiline JS easily
    std::string js_code = R"raw_js(
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
    )raw_js";

    try {
        // Execute the script in the browser context
        driver.ExecuteScript(js_code);
    }
    catch (const std::exception& e) {
        // Equivalent to "pass" in Python - ignore errors during page reloads
    }
}