//VFSG-Booking-Automation/cppapp/VFSG_Booking.h
#ifndef VFSG_BOOKING_H
#define VFSG_BOOKING_H

#include <string>
#include <map>

// User Credentials
inline std::map<std::string, std::string> user = {
    {"email", "sirmohamedh@gmail.com"},
    {"pwd", "Moed!vsfG@26"}
};

// Appointment details mapping

inline std::map<std::string, std::string> appointment_details = {
    {"Choose your Application Centre*", "The Netherlands Visa Application Centre, Cairo"},
    {"Choose your appointment category*", "Short Stay Visa - Type C"},
    {"Choose your sub-category*", "Tourism"}
};

// Global Configuration
inline std::string COOKIE_CHOICE = "All";
inline std::string vfs_url = "https://visa.vfsglobal.com/egy/en/nld/login";

#endif