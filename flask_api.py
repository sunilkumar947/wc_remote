from flask import Flask, jsonify
from threading import Thread
from table import AppTrackerThread
from screen_time import ScreenTimeWidget
from break_time import BreakWidget
from PyQt6.QtCore import QDateTime

app = Flask(__name__)

# Initialize components
app_tracker_thread = AppTrackerThread()
break_widget = BreakWidget()
screen_time_widget = ScreenTimeWidget(break_widget)

# Start the AppTrackerThread
app_tracker_thread.start()

@app.route('/api/all-data', methods=['GET'])
def get_all_data():
    """Return all data in a consolidated format."""
    if not screen_time_widget or not break_widget or not app_tracker_thread:
        return jsonify({"error": "One or more components not initialized."})

    # Prepare consolidated data
    all_data = {
        "login_time": screen_time_widget.login_time.toString("yyyy-MM-dd HH:mm:ss"),
        "total_break_time": break_widget.total_break_time,
        "screen_time": screen_time_widget.format_time(screen_time_widget.screen_time),
        "app_durations": [
            {"app_name": app_name, "duration": f"{duration // 60} min {duration % 60} sec"}
            for app_name, duration in app_tracker_thread.app_durations.items()
        ],
    }
    return jsonify(all_data)


def run_flask():
    """Run Flask app in a separate thread."""
    app.run(debug=False, port=5000, use_reloader=False)


if __name__ == "__main__":
    # Run Flask in a separate thread to allow PyQt6 app to function concurrently
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
