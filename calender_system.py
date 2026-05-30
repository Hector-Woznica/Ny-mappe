# Define the calendar system for the restaurant reservation system
from datetime import date, datetime, timedelta


    
class CalendarSystem:
    # take number of weeks you want to show
    def __init__(self, num_weeks=8):
        self.num_weeks = num_weeks
        self.today = date.today()
        self.time_slots = {12: True, 13: True, 14: True, 15: True, 16: True, 17: True, 18: True, 19: True}
        self.calender_setup(num_weeks)
       
    def calender_setup(self, num_weeks):
       # loop for making dictionary of dates and time slots
        self.calendar = {}
        previous_saturday = self.today - timedelta(days=self.today.weekday() + 2)  # Get the previous Saturday
        previous_sunday = previous_saturday + timedelta(days=1)  # Get the following Sunday
        for i in range(num_weeks+1):
            saturday = previous_saturday + timedelta(days=i * 7)
            sunday = previous_sunday + timedelta(days=i * 7)
            self.calendar[saturday] = self.time_slots.copy()
            self.calendar[sunday] = self.time_slots.copy()

    def display_calendar(self):
        for date, slots in self.calendar.items():
            print(f"{date}: {slots}")


    

if __name__ == "__main__":
    calendar_system = CalendarSystem(num_weeks=8)
    calendar_system.display_calendar()