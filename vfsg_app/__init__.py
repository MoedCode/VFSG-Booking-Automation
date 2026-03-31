# VFSG-Booking-Automation/vfs_app/__init__.py
import sys
import atexit
from seleniumbase import Driver
import time

user = {"email": "sirmohamedh@gmail.com", "pwd": "Moed!vsfG@26"}
appointment_details = {
    "Choose your Application Centre*": "The Netherlands Visa Application Centre, Cairo",
    "Choose your appointment category*": "Short Stay Visa - Type C",
    "Choose your sub-category*": "Tourism",
}
COOKIE_CHOICE = "All"
DEFAULT_URL = "https://visa.vfsglobal.com/egy/en/nld/login"
driver = None
COOKE_CLICK_DELAY = 10
email_selectors = [
    'input[formcontrolname="username"]',
    'input[formcontrolname="userName"]',
    'input[formcontrolname="email"]',
    'input[type="email"]',
    'input[name*="email" i]',
    'input[placeholder*="email" i]',
]
password_selectors = [
    'input[formcontrolname="password"]',
    'input[type="password"]',
    'input[name*="pass" i]',
    'input[placeholder*="password" i]',
]
cmd = """
open chrome https://visa.vfsglobal.com/egy/en/nld/login
"""
