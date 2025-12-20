"""
VISTA API Server
----------------
This Flask server acts as a controller for the Vision Assistant.

What it does:
- Starts the vision assistant (app.py) as a separate process
- Stops it safely when requested
- Exposes REST APIs for start / stop / status
- Keeps the frontend and backend loosely coupled
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import subprocess
import os
import sys
import time

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
    global vision_thread, is_running

    if is_running:
        return jsonify({
            'success': False,
            'message': 'Vision assistant is already running'
        })

    try:
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
                'message': 'Vision assistant started successfully'
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
    global vision_process, is_running

    if not is_running or vision_process is None:
        return jsonify({
            'success': False,
            'message': 'Vision assistant is not running'
        })

    try:
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
# API: Status check
# ---------------------------------------------------

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Returns current running state of the assistant.
    """
    return jsonify({
        'running': is_running,
        'message': (
            'Vision assistant is running'
            if is_running else
            'Vision assistant is stopped'
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
    return jsonify({'status': 'healthy'})


# ---------------------------------------------------
# App entry point
# ---------------------------------------------------

if __name__ == '__main__':
    print("🚀 Starting VISTA API Server")
    print("🌐 Frontend: http://localhost:3000")
    print("🔌 API: http://localhost:5000")
    print("-" * 40)

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
