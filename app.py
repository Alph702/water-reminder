from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import json
import os
import threading
import time

app = Flask(__name__)

class WaterReminder:
    def __init__(self):
        self.target_ml = 3000
        self.users_data = {}
        self.data_file = 'water_data.json'
        self.last_reminder_time = datetime.now()
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    if isinstance(data, dict):
                        self.users_data = data
                    else:
                        self.users_data = {}
                    # Reset daily intake for all users if it's a new day
                    for username in list(self.users_data.keys()):
                        if self.users_data[username].get('date') != current_date:
                            self.users_data[username]['intake'] = 0
                            self.users_data[username]['date'] = current_date
                            self.users_data[username]['last_drink_time'] = None
            except json.JSONDecodeError:
                self.users_data = {}
        
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users_data, f)

    def get_user_stats(self, username):
        if username not in self.users_data:
            current_date = datetime.now().strftime('%Y-%m-%d')
            self.users_data[username] = {
                'date': current_date,
                'intake': 0,
                'last_drink_time': None
            }
            self.save_data()
        
        user_data = self.users_data[username]
        daily_intake = user_data.get('intake', 0)
        remaining = max(0, self.target_ml - daily_intake)
        last_drink = user_data.get('last_drink_time')
        
        time_since_last_drink = None
        if last_drink:
            last_drink_dt = datetime.fromisoformat(last_drink)
            time_since_last_drink = int((datetime.now() - last_drink_dt).total_seconds() / 60)

        return {
            'username': username,
            'daily_intake': daily_intake,
            'remaining': remaining,
            'target': self.target_ml,
            'percentage': min(100, (daily_intake / self.target_ml) * 100),
            'minutes_since_last_drink': time_since_last_drink
        }

    def get_all_users_stats(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        all_stats = []
        for username, data in self.users_data.items():
            if data.get('date') == current_date:
                daily_intake = data.get('intake', 0)
                remaining = max(0, self.target_ml - daily_intake)
                all_stats.append({
                    'username': username,
                    'daily_intake': daily_intake,
                    'remaining': remaining,
                    'percentage': min(100, (daily_intake / self.target_ml) * 100)
                })
        return sorted(all_stats, key=lambda x: x['daily_intake'], reverse=True)

    def add_water_intake(self, username, ml):
        if username not in self.users_data:
            self.get_user_stats(username)
        
        current_time = datetime.now().isoformat()
        self.users_data[username]['intake'] += ml
        self.users_data[username]['last_drink_time'] = current_time
        self.save_data()
        return self.get_user_stats(username)

reminder = WaterReminder()

@app.route('/')
def index():
    return render_template('index.html', stats=None)

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/get_stats', methods=['POST'])
def get_stats():
    username = request.form.get('username')
    if not username:
        return jsonify({'success': False, 'error': 'Username is required'})
    stats = reminder.get_user_stats(username)
    all_users_stats = reminder.get_all_users_stats()
    return jsonify({'success': True, 'stats': stats, 'all_users_stats': all_users_stats})

@app.route('/get_all_stats')
def get_all_stats():
    all_stats = reminder.get_all_users_stats()
    return jsonify({'success': True, 'all_users_stats': all_stats})

@app.route('/add_water', methods=['POST'])
def add_water():
    try:
        username = request.form.get('username')
        ml = int(request.form.get('amount', 0))
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'})
        if ml > 0:
            stats = reminder.add_water_intake(username, ml)
            all_users_stats = reminder.get_all_users_stats()
            return jsonify({'success': True, 'stats': stats, 'all_users_stats': all_users_stats})
        return jsonify({'success': False, 'error': 'Invalid amount'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid input'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
