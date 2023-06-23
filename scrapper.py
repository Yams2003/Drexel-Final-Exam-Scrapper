from bs4 import BeautifulSoup
from ics import Calendar, Event
import arrow
import requests
import os


def get_exam_schedule(course_parts):
    # Get the page and parse it
    page = requests.get("https://drexel.edu/registrar/scheduling/exams/")
    soup = BeautifulSoup(page.text, "html.parser")

    # Find all row elements within the table body
    table_body = soup.find('tbody')
    rows = table_body.find_all('tr')

    # Get all information of each course
    courseIDs = [row.find_all('td')[1].text for row in rows]
    prof = [row.find_all('td')[3].text for row in rows]
    date = [row.find_all('td')[4].text for row in rows]
    time = [row.find_all('td')[5].text for row in rows]
    location = [row.find_all('td')[6].text for row in rows]

    # Create a new calendar
    cal = Calendar()

    # Use a flag to determine whether we found a class
    flag = False

    # Compare each courseID with the user input and print the exam time if it matches
    for course in courseIDs:
        course_parts_c = course.split()  # Split the course name into parts
        if len(course_parts_c) >= 2 and course_parts_c[0].lower() == course_parts[0].lower() and course_parts_c[
            1].lower() == course_parts[1].lower():
            flag = True
            ind = courseIDs.index(course)
            print("\n")
            print("=" * 40)  # Print a divider line
            print(f"Exam Schedule for {course}:")
            print("-" * 40)  # Print a divider line
            print(f"Professor: {prof[ind]}")
            print(f"Date: {date[ind]}")
            print(f"Time: {time[ind]}")
            print(f"Location: {location[ind]}")
            print("=" * 40)  # Print a divider line
            print("\n")

            # If the user wants to add the exam to their calendar, create a new event
            option = input("Would you like to add this exam to your calendar? (y/n): ")
            if option.lower() == "y":
                event = Event()
                event.name = f"{course} Final Exam"
                # Convert time to proper format
                start_time = time[ind].split("-")[0].strip()
                start_time = start_time[:2] + ":" + start_time[2:]
                end_time = time[ind].split("-")[1].strip()
                end_time = end_time[:2] + ":" + end_time[2:]
                start_datetime = arrow.get(date[ind] + " " + start_time, 'MMM DD, YYYY HH:mm')  # Start time of the exam
                end_datetime = arrow.get(date[ind] + " " + end_time, 'MMM DD, YYYY HH:mm')  # End time of the exam
                event.begin = start_datetime.replace(tzinfo='America/New_York')  # Set time zone for start time
                event.end = end_datetime.replace(tzinfo='America/New_York')  # Set time zone for end time
                event.location = location[ind]

                # Add the event to the calendar
                cal.events.add(event)

    # If we have any events, write the calendar to a file
    if len(cal.events) > 0:
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(downloads_folder, "exam_schedule.ics")
        with open(file_path, 'w') as f:
            f.write(str(cal))
        print(f"iCalendar file saved to: {file_path}")

    return flag


# Ask for the course name
course_name = input("Please enter the course name and number (e.g., 'ACCT 110'): ")
course_parts = course_name.split()

found = get_exam_schedule(course_parts)

if not found:
    print("Exam time not found")
