# VISTA Frontend

Minimal React frontend for the Vision Assistant system.

## Features

- 🎯 Big start/stop button for camera control
- 🎨 Beautiful gradient UI design
- 📱 Responsive design for mobile and desktop
- 🔄 Real-time status updates
- ⚡ Loading states and error handling

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open in browser:**
   - Frontend: http://localhost:3001
   - Make sure backend API is running on http://localhost:5000

## Usage

1. Click the **START** button to begin camera detection
2. The system will:
   - Open your camera
   - Start real-time object detection
   - Provide audio announcements with spatial information
3. Click the **STOP** button to end the session

## API Endpoints

- `POST /api/start` - Start the vision assistant
- `POST /api/stop` - Stop the vision assistant  
- `GET /api/status` - Get current status
- `GET /health` - Health check

## Build for Production

```bash
npm run build
```