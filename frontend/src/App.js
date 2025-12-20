import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState('Ready to start');
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setLoading(true);
    
    try {
      if (!isRunning) {
        // Start the vision assistant
        setStatus('Starting vision assistant...');
        const response = await axios.post('/api/start');
        
        if (response.data.success) {
          setIsRunning(true);
          setStatus('Vision Assistant Running - Camera Active');
        } else {
          setStatus('Failed to start: ' + response.data.message);
        }
      } else {
        // Stop the vision assistant
        setStatus('Stopping vision assistant...');
        const response = await axios.post('/api/stop');
        
        if (response.data.success) {
          setIsRunning(false);
          setStatus('Vision Assistant Stopped');
        } else {
          setStatus('Failed to stop: ' + response.data.message);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setStatus('Error: ' + (error.response?.data?.message || error.message));
    }
    
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 VISTA</h1>
        <h2>Vision Assistant for Blind People</h2>
        
        <div className="status-container">
          <div className={`status-indicator ${isRunning ? 'running' : 'stopped'}`}>
            {isRunning ? '🟢' : '🔴'}
          </div>
          <p className="status-text">{status}</p>
        </div>

        <button 
          className={`main-button ${isRunning ? 'stop' : 'start'} ${loading ? 'loading' : ''}`}
          onClick={handleToggle}
          disabled={loading}
        >
          {loading ? (
            <div className="spinner"></div>
          ) : (
            <>
              {isRunning ? '⏹️ STOP' : '▶️ START'}
              <span className="button-subtitle">
                {isRunning ? 'Stop Camera & Detection' : 'Start Camera & Detection'}
              </span>
            </>
          )}
        </button>

        <div className="info-section">
          <h3>How it works:</h3>
          <ul>
            <li>🎥 Camera captures live video</li>
            <li>🤖 AI detects objects in real-time</li>
            <li>📍 Provides spatial location (left/center/right)</li>
            <li>📏 Estimates distance to objects</li>
            <li>🔊 Announces objects with text-to-speech</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;