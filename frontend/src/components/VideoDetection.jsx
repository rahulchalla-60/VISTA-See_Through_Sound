import { useState, useRef, useEffect } from 'react'
import './VideoDetection.css'

function VideoDetection() {
  const [isRunning, setIsRunning] = useState(false)
  const [detectedObjects, setDetectedObjects] = useState([])
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  // Start camera and object detection
  const startDetection = async () => {
    try {
      // Get camera access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      })
      
      videoRef.current.srcObject = stream
      streamRef.current = stream
      setIsRunning(true)
      
      // Start sending frames to AI every 500ms
      intervalRef.current = setInterval(() => {
        sendFrameToAI()
      }, 500)
      
    } catch (error) {
      alert('Could not access camera. Please allow camera permissions.')
    }
  }

  // Stop everything
  const stopDetection = () => {
    // Stop the interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    
    // Stop camera
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    
    // Reset everything
    setIsRunning(false)
    setDetectedObjects([])
    videoRef.current.srcObject = null
  }

  // Capture frame and send to AI
  const sendFrameToAI = () => {
    if (!videoRef.current || !canvasRef.current) return
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')
    
    // Draw video frame to canvas
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)
    
    // Convert to base64 image
    const imageData = canvas.toDataURL('image/jpeg', 0.8)
    const base64Data = imageData.split(',')[1]
    
    // Send to backend AI
    fetch('http://localhost:8000/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Data })
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        setDetectedObjects(result.objects || [])
        if (result.summary) {
          console.log('AI says:', result.summary)
        }
      }
    })
    .catch(error => {
      console.log('AI connection error:', error)
    })
  }

  // Clean up when component unmounts
  useEffect(() => {
    return () => {
      stopDetection()
    }
  }, [])

  return (
    <div className="video-detection">
      <h2>AI Object Detection</h2>
      
      <div className="video-container">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="video-stream"
        />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      <button
        onClick={isRunning ? stopDetection : startDetection}
        className={`main-btn ${isRunning ? 'stop' : 'start'}`}
      >
        {isRunning ? 'Stop' : 'Start Detection'}
      </button>

      <div className="status">
        <p>{isRunning ? '🟢 AI is watching' : '🔴 Not active'}</p>
      </div>

      {detectedObjects.length > 0 && (
        <div className="objects-found">
          <h3>Objects I can see:</h3>
          <ul>
            {detectedObjects.map((obj, index) => (
              <li key={index}>
                {obj.name} ({Math.round(obj.confidence * 100)}% sure)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default VideoDetection