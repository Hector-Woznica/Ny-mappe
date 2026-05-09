# Flask Website - name: "Musikspil til Plejehjem, Gratis"

## Overview
A simple Flask-based website that allows users to view services and book appointments.

## Pages
- About (Who we are, services offered, where we operate)
- Schedule (Available locations and time slots)
- Contact
- Statistics (Statistics for vist)

## Database Design

### Table 1: Services
- service_id
- type_of_service
- location

### Table 2: Bookings
- booking_id
- nursing_home_name
- location
- booking_time
- service_type

## Website Logic
- User selects a service and location
- Only show locations within a defined limit (e.g., distance <= 20 km)
- Allow user to choose an available time slot
- Store booking details in the database
- Optional: integrate a map system to display locations



