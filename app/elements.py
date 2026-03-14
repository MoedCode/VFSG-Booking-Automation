#VFSG-Booking-Automation/app/element.py
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
