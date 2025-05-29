from flask import Flask, render_template, Response, jsonify, request
import cv2
import dlib
import numpy as np
import time
import json
from utils.eye_detector import EyeDetector
from utils.distance import DistanceCalculator
from utils.notification import NotificationManager
import threading
import time as time_module

app = Flask(__name__)

# Global variables
screen_time = 0
last_blink_time = time.time()
last_break_time = time.time()
eye_detector = EyeDetector()
distance_calculator = DistanceCalculator()
notification_manager = NotificationManager()
custom_break_end_time = None
exercise_end_time = None
custom_break_end_time = None
custom_break_active = False
break_timer_thread = None

# Default settings
settings = {
    "blink_reminder_enabled": True,
    "blink_reminder_time": 5,  # seconds
    "screen_time_reminder_enabled": True,
    "screen_time_interval": 20,  # minutes
    "distance_reminder_enabled": True,
    "min_distance": 45,  # cm
    "custom_break_enabled": False,
    "custom_break_interval": 45,  # minutes
    "exercise_active": False
}

# Lock for thread-safe operations
lock = threading.Lock()
def break_timer_countdown(minutes):
    global custom_break_end_time, custom_break_active
    custom_break_end_time = time_module.time() + (minutes * 60)
    custom_break_active = True
    # Wait until timer ends
    while time_module.time() < custom_break_end_time and custom_break_active:
        time_module.sleep(1)
    
    # If not canceled, send notification
    if custom_break_active:
        notification_manager.notify(
            "Break Time!",
            "Time for your scheduled break!",
            "custom_break"
        )
        with lock:
            custom_break_active = False

def generate_frames():
    global screen_time, last_blink_time, last_break_time, custom_break_end_time
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start_time = time.time()
    blink_count = 0  # Initialize blink counter
    last_eyes_state = True  # Track previous eye state
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Flip the frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)
        
        # Process frame for eye detection
        frame, eyes_open, eyes_detected = eye_detector.process_frame(frame)
        
        # Update blink count when eyes transition from open to closed
        if eyes_detected:
            if last_eyes_state and not eyes_open:
                blink_count += 1
            last_eyes_state = eyes_open
        
        # Display stats on frame
        # Screen Time
        cv2.putText(frame, f"Screen Time: {int(screen_time//60)}m {int(screen_time%60)}s", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Blink Count
        cv2.putText(frame, f"Blinks: {blink_count}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Distance if detected
        if eyes_detected and (distance := distance_calculator.calculate(frame, eye_detector.eye_landmarks)):
            cv2.putText(frame, f"Distance: {distance:.1f} cm", 
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Check if distance is too close
            if settings["distance_reminder_enabled"] and distance < settings["min_distance"]:
                notification_manager.notify(
                    "Distance Alert", 
                    f"You're too close to the screen! Maintain at least {settings['min_distance']} cm distance.",
                    "distance"
                )
        
        # EAR (Eye Aspect Ratio)
        if eyes_detected:
            ear = eye_detector.get_ear()  # Add this method to EyeDetector class
            cv2.putText(frame, f"EAR: {ear:.2f}", 
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Handle blink detection
        current_time = time.time()
        
        # Only track time and check reminders if eyes are detected and open
        if eyes_detected:
            if eyes_open:
                # Update screen time
                with lock:
                    screen_time += current_time - start_time
                
                # Check for blink reminder
                if settings["blink_reminder_enabled"] and (current_time - last_blink_time) > settings["blink_reminder_time"]:
                    notification_manager.notify(
                        "Blink Reminder", 
                        "Remember to blink your eyes!",
                        "blink"
                    )
            else:
                # Reset blink time when eyes are closed (indicating a blink)
                last_blink_time = current_time
            
            # Check for screen time break reminder (20-20-20 rule with adjustable time)
            screen_time_minutes = screen_time / 60
            if settings["screen_time_reminder_enabled"] and (screen_time_minutes - last_break_time/60) >= settings["screen_time_interval"]:
                notification_manager.notify(
                    "Screen Time Break", 
                    f"You've been looking at the screen for {settings['screen_time_interval']} minutes. Look at something 20 feet away for 20 seconds.",
                    "screen_time"
                )
                last_break_time = current_time
            
            # Check for custom break timer
            if settings["custom_break_enabled"] and custom_break_end_time and current_time >= custom_break_end_time:
                notification_manager.notify(
                    "Scheduled Break", 
                    "Time for your scheduled break!",
                    "custom_break"
                )
                with lock:
                    custom_break_end_time = None
        
        start_time = current_time
        
        # Convert to jpeg for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', settings=settings)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_screen_time')
def get_screen_time():
    with lock:
        minutes = int(screen_time // 60)
        seconds = int(screen_time % 60)
    return jsonify({'minutes': minutes, 'seconds': seconds})

@app.route('/reset_timer')
def reset_timer():
    global screen_time, last_break_time
    with lock:
        screen_time = 0
        last_break_time = time.time()
    return jsonify({'status': 'success'})

@app.route('/toggle_setting/<setting_name>/<value>')
def toggle_setting(setting_name, value):
    value_bool = value.lower() == 'true'
    
    if setting_name in settings:
        settings[setting_name] = value_bool
    
    return jsonify({'status': 'success', 'setting': setting_name, 'value': value_bool})

@app.route('/update_setting', methods=['POST'])
def update_setting():
    data = request.json
    setting_name = data.get('setting')
    value = data.get('value')
    
    if setting_name in settings:
        try:
            # Convert to appropriate type (float for distances, int for times)
            if setting_name in ['min_distance']:
                settings[setting_name] = float(value)
            else:
                settings[setting_name] = int(value)
            return jsonify({'status': 'success'})
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid value'}), 400
    
    return jsonify({'status': 'error', 'message': 'Setting not found'}), 404

@app.route('/set_custom_break', methods=['POST'])
def set_custom_break():
    global custom_break_end_time, custom_break_active, break_timer_thread
    
    data = request.json
    minutes = data.get('minutes', 0)
    
    if minutes > 0:
        # Cancel any existing timer
        cancel_custom_break_internal()
        
        # Start new timer in a thread
        break_timer_thread = threading.Thread(target=break_timer_countdown, args=(int(minutes),))
        break_timer_thread.daemon = True
        break_timer_thread.start()
        
        settings["custom_break_enabled"] = True
        
        return jsonify({
            'status': 'success', 
            'message': f'Break set for {minutes} minutes from now',
            'end_time': custom_break_end_time
        })
    
    return jsonify({'status': 'error', 'message': 'Invalid time'}), 400
def cancel_custom_break_internal():
    global custom_break_end_time, custom_break_active, break_timer_thread
    
    with lock:
        custom_break_active = False
        custom_break_end_time = None
        settings["custom_break_enabled"] = False

@app.route('/cancel_custom_break')
def cancel_custom_break():
    cancel_custom_break_internal()
    return jsonify({'status': 'success'})

@app.route('/get_break_time')
def get_break_time():
    with lock:
        if custom_break_end_time and custom_break_active:
            remaining = max(0, custom_break_end_time - time_module.time())
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            is_finished = remaining <= 0
            
            return jsonify({
                'active': True,
                'minutes': minutes,
                'seconds': seconds,
                'is_finished': is_finished
            })
    
    return jsonify({'active': False})

@app.route('/start_exercise')
def start_exercise():
    global exercise_end_time
    
    with lock:
        exercise_end_time = time.time() + 60  # 1 minute exercise
        settings["exercise_active"] = True
    
    return jsonify({'status': 'success'})

@app.route('/stop_exercise')
def stop_exercise():
    global exercise_end_time
    
    with lock:
        exercise_end_time = None
        settings["exercise_active"] = False
    
    return jsonify({'status': 'success'})

@app.route('/get_exercise_time')
def get_exercise_time():
    with lock:
        if exercise_end_time and settings["exercise_active"]:
            remaining = max(0, exercise_end_time - time.time())
            return jsonify({
                'active': True,
                'seconds': int(remaining)
            })
        else:
            settings["exercise_active"] = False
            return jsonify({'active': False})

@app.route('/get_settings')
def get_settings():
    return jsonify(settings)

if __name__ == '__main__':
    app.run(debug=True)
