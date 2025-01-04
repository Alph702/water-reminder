# Water Reminder

A Flask-based water intake tracking application that helps you maintain proper hydration throughout the day.

## Features

- Track daily water intake with a beautiful web interface
- Visual progress bar showing progress towards daily goal
- Quick-add buttons for common amounts
- Custom amount input
- Persistent data storage across sessions
- Daily reset of water intake

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python water_reminder.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

- Use the quick-add buttons to log common water intake amounts (100ml, 200ml, 300ml, 500ml)
- Enter a custom amount in milliliters using the input field
- Track your progress towards the daily goal of 3000ml
- Data automatically resets at midnight for the next day

## Note

The application stores your daily water intake in `water_data.json`. This file is automatically created when you first use the application.
