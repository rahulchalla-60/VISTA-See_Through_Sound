# VISTA - Complete Setup Guide

## 🚀 Quick Start

### 1. Backend Setup (Flask API)

```bash
cd backend
pip install flask flask-cors
python api_server.py
```

**Backend will run on:** http://localhost:5000

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
npm start
```

**Frontend will run on:** http://localhost:3001

## 🎯 How to Use

1. **Start both servers:**

   - Backend: `python backend/api_server.py`
   - Frontend: `npm start` (in frontend folder)

2. **Open browser:** http://localhost:3001

3. **Click the big START button** to begin vision assistance

4. **Click STOP** when done

## 🔧 What Happens When You Click START

1. Frontend sends request to backend API
2. Backend starts your `app.py` vision assistant
3. Camera opens with real-time detection
4. Objects are announced with TTS
5. Visual feedback shows on screen

## 🛠️ Troubleshooting

**Frontend won't start:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**Backend API errors:**

```bash
pip install flask flask-cors ultralytics opencv-python pyttsx3
```

**Camera not working:**

- Check if another app is using your camera
- Try different camera index in `app.py`

## 📁 Project Structure

```
VISTA-See_Through_Sound/
├── backend/
│   ├── app.py              # Main vision assistant
│   ├── api_server.py       # Flask API server
│   └── nodes/
│       ├── camera_node.py
│       ├── detection_node.py
│       └── spatial_analysis_node.py
└── frontend/
    ├── src/
    │   ├── App.js          # Main React component
    │   ├── App.css         # Styling
    │   └── index.js
    └── package.json
```

## 🎨 UI Features

- **Big Start/Stop Button** - Easy to use
- **Status Indicator** - Shows running state
- **Loading Animation** - Visual feedback
- **Responsive Design** - Works on mobile
- **Beautiful Gradients** - Modern look
