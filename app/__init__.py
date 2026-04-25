# VFSG-Booking-Automation/app/__init__.py
import sys
import atexit
from seleniumbase import Driver
import time
import random
from datetime import datetime
import winsound



user1 = {"email": "elsalamfurnituremoving@gmail.com", "pwd": "Moed!vsfG@26"}
user = {"email": "sirmohamedh@gmail.com", "pwd": "Moed!vsfG@26"}
appointment_details = {
    "Choose your Application Centre*": "The Netherlands Visa Application Centre, Cairo",
    "Choose your appointment category*": "Short Stay Visa - Type C",
    "Choose your sub-category*": "Tourism",
}
cookies={
    "buttons":{
        "click_delay":10,
        "id":{
        "accept-all":"button#onetrust-accept-btn-handler",
        "accept-necessary":"onetrust-reject-all-handler"
        }
    },
    "choice":"accept-all"
}
cookies_choice = "All"
DEFAULT_URL = "https://visa.vfsglobal.com/egy/en/nld/login"
driver = None

dashboard_config = {
    "selectors": {
        "start_booking": [
            "button:contains('Start New Booking')", # Best for VFS
            "button.btn-brand-orange",             # Their standard orange button
            "button[routerlink='/how-to-apply']",   # Common Angular route link
            ".mat-mdc-button-touch-target"          # The target span you found
        ]
    },
    "booking_config" :{
    "selectors": {
        "fields": {
            "center": 'mat-select[formcontrolname="centerCode"]',
            "category": 'mat-select[formcontrolname="selectedSubvisaCategory"]',
            "subcategory": 'mat-select[formcontrolname="visaCategoryCode"]'
        },
        "option_tag": "mat-option",
        "continue_btn": "button.btn-brand-orange"
    },
        "mapped_fields" : [
        ("Choose your Application Centre*", 'mat-select[formcontrolname="centerCode"]'),
        ("Choose your appointment category*", 'mat-select[formcontrolname="selectedSubvisaCategory"]'),
        ("Choose your sub-category*", 'mat-select[formcontrolname="visaCategoryCode"]'),
    ]
    
}
}
auth_config_old={
    
    "typing_delay":1,
    "selectors":{
        "email": [
            'input[formcontrolname="username"]',
            'input[formcontrolname="userName"]',
            'input[formcontrolname="email"]',
            'input[type="email"]',
            'input[name*="email" i]',
            'input[placeholder*="email" i]',
        ],
        "password" : [
            'input[formcontrolname="password"]',
            'input[type="password"]',
            'input[name*="pass" i]',
            'input[placeholder*="password" i]',
        ]
    }
}
auth_config = {
    "typing_delay": 1,
    "selectors": {
        "email": [
            'input[formcontrolname="username"]',
            'input#email',
            'input[type="email"]',
        ],
        "password": [
            'input[formcontrolname="password"]',
            'input#password',
            'input[type="password"]',
        ],
        "submit": [
            'button.btn-brand-orange',      # Specific VFS orange button class
            'button.mat-btn-lg',            # Large material button class
            'button[mat-stroked-button]',   # Angular material attribute
            'button.mdc-button--outlined'   # Material Design Component class
        ]
    }
}

log_files_headers = [
    "Date (dd/mm/yyyy)",
    "Time (hh:mm:ss)",
    "Tourism",
    "Business",
    "Family/Friend Visit",
    "Other (Medical, Cultural and sports, Entry Visa)",
]
tracking_config = {
    "main_target": "Tourism",
    "alt_categories": [
        "Business",
        "Family/Friend Visit",
        "Other (Medical, Cultural and sports, Entry Visa)",
    ],
    "alert_selector": 'div[role="alert"]',
    "base_log_dir": "logs_archive",
}

cmd = """
open chrome https://visa.vfsglobal.com/egy/en/nld/login
PYTHONPATH=$PYTHONPATH:/home/pro-eng/pyenv-0/lib/python3.12/site-packages pyinstaller --noconfirm --onefile --windowed --name "VFS_Booking_Bot" --add-data "vfsg_app/__init__.py:vfsg_app" --add-data "vfsg_app/browser_manager.py:vfsg_app" --collect-all seleniumbase --collect-all customtkinter vfsg_app/gui.py
>> --name "VFS_Booking_Bot" `
>> --add-data "vfsg_app/__init__.py;vfsg_app" `
>> --add-data "vfsg_app/browser_manager.py;vfsg_app" `     
>> --collect-all seleniumbase `
>> --collect-all customtkinter `
>> --paths "vfsg_app" `
>> vfsg_app/gui.py
"""