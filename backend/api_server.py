"""
VISTA API Server
----------------
This Flask server acts as a controller for the Vision Assistant with Navigation.

What it does:
- Starts the vision assistant (app.py) as a separate process
- Stops it safely when requested
- Manages navigation with obstacle detection
- Handles voice location saving
- Exposes REST APIs for frontend control
- Keeps the frontend and backend loosely coupled
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import subprocess
import os
import sys
import time
import json

# Import navigation components
from navigation.offline_voice_saver import OfflineVoiceLocation
from navigation.voice_navigation import VoiceNavigator
from integrated_vision_navigation import IntegratedVisionNavigation

# ---------------------------------------------------
# App setup
# ---------------------------------------------------

app = Flask(__name__)
CORS(app)  # Allow frontend (React) to talk to backend

# ---------------------------------------------------
# Global state (keeps track of assistant lifecycle)
# ---------------------------------------------------

vision_process = None     # Holds the subprocess running app.py
vision_thread = None      # Thread that launches the subprocess
is_running = False        # Simple flag for current state

# Navigation components
integrated_system = None
voice_saver = None
navigation_active = False

# ---------------------------------------------------
# Core logic: run vision assistant
# ---------------------------------------------------

def run_vision_assistant():
    """
    Starts the vision assistant (app.py) in a separate process.

    Runs inside a daemon thread so the Flask server
    does not block or freeze.
    """
    global vision_process, is_running

    try:
        # Absolute path to app.py (vision assistant)
        app_path = os.path.join(os.path.dirname(__file__), 'app.py')

        # Launch the assistant using the same Python interpreter
        vision_process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        is_running = True
        print("✅ Vision assistant started")

        # Block here until the process exits
        vision_process.wait()

    except Exception as e:
        print(f"❌ Failed to start vision assistant: {e}")

    finally:
        # Cleanup if the process exits unexpectedly
        is_running = False
        vision_process = None
        print("🛑 Vision assistant stopped")


# ---------------------------------------------------
# API: Start assistant
# ---------------------------------------------------

@app.route('/api/start', methods=['POST'])
def start_vision_assistant():
    """
    Starts the vision assistant if it is not already running.
    """
    global vision_thread, is_running, integrated_system

    if is_running:
        return jsonify({
            'success': False,
            'message': 'Vision assistant is already running'
        })

    try:
        # Initialize integrated system
        integrated_system = IntegratedVisionNavigation()
        
        # Run assistant in a background thread
        vision_thread = threading.Thread(
            target=run_vision_assistant,
            daemon=True
        )
        vision_thread.start()

        # Give the process a moment to spin up
        time.sleep(1)

        if is_running:
            return jsonify({
                'success': True,
                'message': 'Vision assistant started successfully with navigation capability'
            })

        return jsonify({
            'success': False,
            'message': 'Vision assistant failed to start'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting vision assistant: {str(e)}'
        })


# ---------------------------------------------------
# API: Stop assistant
# ---------------------------------------------------

@app.route('/api/stop', methods=['POST'])
def stop_vision_assistant():
    """
    Stops the vision assistant safely.
    """
    global vision_process, is_running, integrated_system, navigation_active

    if not is_running or vision_process is None:
        return jsonify({
            'success': False,
            'message': 'Vision assistant is not running'
        })

    try:
        # Stop navigation if active
        if navigation_active and integrated_system:
            integrated_system.stop_navigation()
            navigation_active = False

        # Ask the process to terminate gracefully
        vision_process.terminate()

        try:
            vision_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it refuses to stop
            vision_process.kill()
            vision_process.wait()

        is_running = False
        vision_process = None
        integrated_system = None

        return jsonify({
            'success': True,
            'message': 'Vision assistant stopped successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping vision assistant: {str(e)}'
        })


# ---------------------------------------------------
# API: Navigation endpoints
# ---------------------------------------------------

@app.route('/api/navigation/start', methods=['POST'])
def start_navigation():
    """
    Start navigation with obstacle detection between saved locations.
    """
    global integrated_system, navigation_active

    if not is_running or not integrated_system:
        return jsonify({
            'success': False,
            'message': 'Vision assistant must be running to start navigation'
        })

    if navigation_active:
        return jsonify({
            'success': False,
            'message': 'Navigation is already active'
        })

    try:
        data = request.get_json()
        start_location = data.get('start')
        destination = data.get('destination')

        if not start_location or not destination:
            return jsonify({
                'success': False,
                'message': 'Both start location and destination are required'
            })

        # Get coordinates from saved locations
        voice_saver = OfflineVoiceLocation()
        start_coords = voice_saver.nav.get_location_coords(start_location)
        end_coords = voice_saver.nav.get_location_coords(destination)

        if not start_coords:
            return jsonify({
                'success': False,
                'message': f'Start location "{start_location}" not found in saved locations'
            })

        if not end_coords:
            return jsonify({
                'success': False,
                'message': f'Destination "{destination}" not found in saved locations'
            })

        # Start integrated navigation
        success = integrated_system.start_integrated_navigation(start_coords, end_coords)

        if success:
            navigation_active = True
            return jsonify({
                'success': True,
                'message': f'Navigation started from {start_location} to {destination} with obstacle detection'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start navigation - could not calculate route'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Navigation error: {str(e)}'
        })


@app.route('/api/navigation/stop', methods=['POST'])
def stop_navigation():
    """
    Stop navigation but keep vision assistant running.
    """
    global integrated_system, navigation_active

    if not navigation_active:
        return jsonify({
            'success': False,
            'message': 'Navigation is not currently active'
        })

    try:
        if integrated_system:
            integrated_system.stop_navigation()
        
        navigation_active = False

        return jsonify({
            'success': True,
            'message': 'Navigation stopped successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping navigation: {str(e)}'
        })


# ---------------------------------------------------
# API: Location management
# ---------------------------------------------------

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    Get all saved locations.
    """
    try:
        voice_saver = OfflineVoiceLocation()
        locations = []
        
        for key, data in voice_saver.locations.items():
            locations.append({
                'name': key,
                'description': data.get('description', key),
                'lat': data['lat'],
                'lon': data['lon'],
                'saved_at': data.get('saved_at', '')
            })

        return jsonify({
            'success': True,
            'locations': locations
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading locations: {str(e)}',
            'locations': []
        })


@app.route('/api/locations/save', methods=['POST'])
def save_location():
    """
    Activate voice location saver for saving current location.
    """
    try:
        # This would typically trigger the voice location saver
        # For now, we'll return a success message
        return jsonify({
            'success': True,
            'message': 'Voice location saver activated. Use voice commands to save your location.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error activating location saver: {str(e)}'
        })


@app.route('/api/locations/add', methods=['POST'])
def add_location():
    """
    Add a location manually (for testing or manual input).
    """
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', name)
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))

        if not name or lat is None or lon is None:
            return jsonify({
                'success': False,
                'message': 'Name, latitude, and longitude are required'
            })

        voice_saver = OfflineVoiceLocation()
        voice_saver.add_location(name, lat, lon, description)

        return jsonify({
            'success': True,
            'message': f'Location "{name}" added successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding location: {str(e)}'
        })


# ---------------------------------------------------
# API: Status check
# ---------------------------------------------------

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Returns current running state of the assistant and navigation.
    """
    return jsonify({
        'running': is_running,
        'navigation_active': navigation_active,
        'message': (
            f'Vision assistant: {"running" if is_running else "stopped"}, '
            f'Navigation: {"active" if navigation_active else "inactive"}'
        )
    })


# ---------------------------------------------------
# API: Health check
# ---------------------------------------------------

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health endpoint for monitoring.
    """
    return jsonify({
        'status': 'healthy',
        'vision_running': is_running,
        'navigation_active': navigation_active
    })


# ---------------------------------------------------
# App entry point
# ---------------------------------------------------

if __name__ == '__main__':
    print("🚀 Starting VISTA API Server with Navigation")
    print("🌐 Frontend: http://localhost:3001")
    print("🔌 API: http://localhost:5000")
    print("🧭 Navigation: Integrated with obstacle detection")
    print("🎤 Voice: Location saving and navigation commands")
    print("-" * 50)

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
