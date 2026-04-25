# VFS Global Booking Automation (VFSG-Bot)

An advanced automation suite designed to streamline the appointment booking process for VFS Global. This tool features a stealth browser implementation to bypass bot detection, a dedicated captcha monitoring system, and a multi-threaded GUI for real-time control.

## 🚀 Key Features

* **Stealth Browsing:** Built on `SeleniumBase` with Undetected-ChromeDriver (UC) mode to minimize detection by Cloudflare and other WAFs.
* **Intelligent Captcha Solver:** A dedicated monitor (`captcha.py`) that actively hunts for Cloudflare Turnstile challenges and handles them automatically.
* **Dynamic Hunting Loop:** Automatically switches between visa sub-categories to "refresh" the session and catch available slots instantly.
* **Dual Interface:** Includes a modern `CustomTkinter` GUI for ease of use and a Terminal CLI for power users.
* **Human-Like Interaction:** Implements randomized delays and JavaScript-based clicks to mimic human behavior.
* **Instant Alerts:** Auditory alerts (Beeps) triggered immediately upon finding an available slot.

---

## 📂 Project Structure

```text
VFSG-Booking-Automation/
├── app/
│   ├── __init__.py           # Shared configurations, credentials, and selectors
│   ├── browser_manager.py    # Core browser logic (Login, Form Filling, Hunting)
│   ├── captcha.py            # Turnstile/Cloudflare monitoring and interaction
│   ├── gui.py                # Main Dashboard (CustomTkinter)
│   └── main.py               # Entry point (Handles GUI and CLI threads)
├── resources.md              # Additional technical notes
└── README.md                 # Project documentation
```

---

## 🛠️ Installation

### Prerequisites
* Python 3.10+
* Google Chrome installed

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/VFSG-Booking-Automation.git
   cd VFSG-Booking-Automation
   ```
2. Install dependencies:
   ```bash
   pip install seleniumbase customtkinter
   ```
3. Install the SeleniumBase driver:
   ```bash
   sbase install chromedriver
   ```

---

## ⚙️ Configuration (`app/__init__.py`)

Before running, update the `user` dictionary in `app/__init__.py` with your VFS credentials:

```python
user = {
    "email": "your-email@example.com", 
    "pwd": "your-password"
}
```

You can also modify the `tracking_config` to set your primary target category (e.g., "Tourism" or "Business").

---

## 🚀 Usage

### Running the Dashboard
Launch the main controller to open the GUI and Terminal simultaneously:
```bash
python app/main.py
```

### Automation Workflow
1.  **Launch:** Click "Launch With Chrome" in the GUI.
2.  **Automated Login:** The bot will navigate to VFS, handle cookies, enter credentials, and solve any initial captchas.
3.  **The Hunt:** Once on the appointment details page, the bot will enter a "Hunting Loop." It selects your target category, checks for slots, and if none are found, switches to an alternative category to reset the session before trying again.
4.  **Success:** When a slot is detected, the bot plays a high-pitched alert and stops at the payment/finalization screen for manual completion.

---

## 🛡️ Captcha Handling Logic
The `captcha.py` module operates as a background observer. It:
1.  Scans for Turnstile iframes using multiple CSS selectors.
2.  Triggers an audible beep to notify the user if manual intervention is preferred.
3.  Attempts to automatically click the verification checkbox.
4.  Waits for the "Success!" state before allowing the automation to proceed.

---

## 📦 Compilation (Creating an EXE)
To bundle the application into a single executable for Windows:
```bash
pyinstaller --noconfirm --onefile --windowed --name "VFS_Booking_Bot" \
--add-data "app/__init__.py:app" \
--collect-all seleniumbase \
--collect-all customtkinter \
app/main.py
```

---

## ⚠️ Disclaimer
This tool is for educational purposes and personal use only. Use it responsibly and in accordance with VFS Global's Terms of Service. The developers are not responsible for account suspensions or misuse of this software.