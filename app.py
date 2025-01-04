from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os
from plyer import notification
import threading
import time

app = Flask(__name__)

class WaterReminder:
    def __init__(self):
        self.target_ml = 3000
        self.daily_intake = 0
        self.data_file = 'water_data.json'
        self.last_notification = datetime.now() - timedelta(hours=1)  # Set to past to trigger immediate notification
        self.notification_interval = timedelta(minutes=60)  # Notify every 60 minutes
        self.load_data()
        # Start notification thread
        self.notification_thread = threading.Thread(target=self._notification_loop, daemon=True)
        self.notification_thread.start()

    def _notification_loop(self):
        while True:
            current_time = datetime.now()
            if current_time - self.last_notification >= self.notification_interval:
                remaining = max(0, self.target_ml - self.daily_intake)
                if remaining > 0:
                    notification.notify(
                        title='Water Reminder',
                        message=f'Time to drink water! You still need {remaining}ml to reach your daily goal.',
                        app_icon=None,
                        timeout=10,
                    )
                self.last_notification = current_time
            time.sleep(60)  # Check every minute

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    current_date = datetime.now().date().isoformat()
                    if data.get('date') == current_date:
                        self.daily_intake = data.get('intake', 0)
                    else:
                        self.daily_intake = 0
            except:
                self.daily_intake = 0
        
    def save_data(self):
        data = {
            'date': datetime.now().date().isoformat(),
            'intake': self.daily_intake
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f)

    def add_water_intake(self, ml):
        self.daily_intake += ml
        self.save_data()
        remaining = max(0, self.target_ml - self.daily_intake)
        return {
            'daily_intake': self.daily_intake,
            'remaining': remaining,
            'target': self.target_ml,
            'percentage': min(100, (self.daily_intake / self.target_ml) * 100)
        }

reminder = WaterReminder()

@app.route('/')
def index():
    stats = reminder.add_water_intake(0)  # Get current stats without adding water
    return render_template('index.html', stats=stats)

@app.route('/add_water', methods=['POST'])
def add_water():
    try:
        ml = int(request.form.get('amount', 0))
        if ml > 0:
            stats = reminder.add_water_intake(ml)
            return jsonify({'success': True, **stats})
        return jsonify({'success': False, 'error': 'Invalid amount'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid input'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
