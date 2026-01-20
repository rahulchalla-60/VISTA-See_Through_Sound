import VideoDetection from './components/VideoDetection'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Vision Assistant for Blind People</h1>
        <p>Real-time object detection to help navigate the world</p>
      </header>
      
      <main className="app-main">
        <VideoDetection />
      </main>
      
      <footer className="app-footer">
        <p>Built with React + YOLO Object Detection</p>
      </footer>
    </div>
  )
}

export default App
