import { useState, useRef, useEffect, useCallback } from 'react'
import './VideoDetection.css'

function VideoDetection() {
  const [isActive, setIsActive] = useState(false)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  const stopEverything = useCallback(() => {
    // Stop detection interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    // Stop video stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    
    setIsActive(false)
  }, [])

  const startEverything = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setIsActive(true)
        
        // Start detection automatically
        intervalRef.current = setInterval(() => {
          const frame = captureFrame()
          if (frame) {
            sendFrameToBackend(frame)
          }
        }, 500)
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('Could not access camera. Please check permissions.')
    }
  }

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)
    
    return canvas.toDataURL('image/jpeg', 0.8)
  }

  const sendFrameToBackend = async (frameData) => {
    try {
      // Remove data:image/jpeg;base64, prefix
      const base64Data = frameData.split(',')[1]
      
      const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: base64Data })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Detection result:', result)
        // Handle detection results here
      }
    } catch (error) {
      console.error('Error sending frame to backend:', error)
    }
  }

  useEffect(() => {
    return () => {
      stopEverything()
    }
  }, [stopEverything])

  return (
    <div className="video-detection">
      <h2>Object Detection</h2>
      
      <div className="video-container">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="video-stream"
        />
        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />
      </div>

      <div className="controls">
        <button
          onClick={isActive ? stopEverything : startEverything}
          className={`main-btn ${isActive ? 'stop' : 'start'}`}
        >
          {isActive ? 'Stop' : 'Start'}
        </button>
      </div>

      <div className="status">
        <p>Status: {isActive ? '🟢 Active - Detecting Objects' : '🔴 Inactive'}</p>
      </div>
    </div>
  )
}

export default VideoDetection