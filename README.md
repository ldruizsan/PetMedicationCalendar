# Pet Medication Dosage Scheduler 🐾💊

## Overview

The Pet Medication Dosage Scheduler is a web application designed to help pet owners easily create, manage, and visualize medication schedules for their pets. It allows users to input pet details and a single medication regimen with multiple dosage steps, then displays this schedule on an interactive calendar. Users can also download a printable PDF version of the calendar.

## Features

*   **Pet Details Management:**
    *   Store and update pet's name, type (Dog/Cat), age, and weight.
*   **Single Medication Scheduling:**
    *   Define one medication at a time.
    *   Set the medication name.
    *   Add multiple dosage steps, each with:
        *   Dosage amount (e.g., 1.0, 0.5)
        *   Unit type (e.g., Tablet(s), mL, mg)
        *   Frequency of administration (in hours)
        *   Duration of the step (in days)
        *   Start date for the step
*   **Interactive Calendar View:**
    *   Displays all medication doses on a monthly calendar.
    *   Each event shows the dosage amount and unit.
    *   Events are color-coded (currently a single default color).
    *   Checkboxes on calendar events for visual tracking (not saved).
*   **Data Management:**
    *   Ability to "Set / Update" the current medication, replacing any previous one.
    *   Clear the current medication schedule.
    *   Clear all pet and medication data.
*   **User Feedback:**
    *   Flash messages for successful operations, errors, or warnings.
*   **Printable PDF Calendar:**
    *   Download a PDF version of the currently displayed medication calendar, including a title with pet and medication names.
*   **Dynamic Form for Dosage Steps:**
    *   Easily add or remove dosage steps when defining a medication.
    *   Start dates for subsequent steps can be auto-calculated.

## How It Works

The application is built using the Flask web framework in Python.

1.  **Backend (Flask - `appv2.py`):**
    *   Manages HTTP requests and routes.
    *   Uses Flask's session to store pet details and the current medication information temporarily in the user's browser.
    *   `generate_event_data` function: Takes the medication details and calculates all individual dosage events (start time, end time, title) for the calendar.
    *   Provides API endpoints:
        *   `/`: Renders the main page (`index.html`).
        *   `/update_pet`: Handles updates to pet details.
        *   `/set_med`: Adds or updates the single medication in the session.
        *   `/clear_medication`: Clears the current medication from the session.
        *   `/clear_all`: Clears medication (and optionally pet details).
        *   `/get_schedule_events`: Returns JSON data for FullCalendar to display events.
2.  **Frontend (`templates/index.html`):**
    *   Uses Jinja2 templating to dynamically display data from the Flask backend (e.g., pet details, current medication).
    *   Contains forms for inputting pet and medication data.
    *   Integrates **FullCalendar.js** to render the interactive medication schedule.
    *   JavaScript is used for:
        *   Dynamically adding/removing dosage step fields in the medication form.
        *   Fetching event data from the backend for FullCalendar.
        *   Implementing the "Download PDF" functionality using **html2canvas** (to capture the calendar as an image) and **jsPDF** (to create the PDF document).

## Key Technologies Used

*   **Backend:**
    *   Python 3
    *   Flask
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   JavaScript
*   **Libraries:**
    *   FullCalendar.js (for the interactive calendar)
    *   html2canvas.js (for capturing HTML to canvas for PDF generation)
    *   jsPDF.js (for client-side PDF generation)

## Setup and Running the Application

1.  **Prerequisites:**
    *   Python 3.x
    *   `pip` (Python package installer)

2.  **Clone the Repository (if applicable):**


3.  **Create and Activate a Virtual Environment (Recommended):**
    