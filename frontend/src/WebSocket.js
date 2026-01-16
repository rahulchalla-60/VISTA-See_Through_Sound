class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.onMessageCallback = null;
  }

  connect() {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    this.socket.onclose = () => {
      console.log("❌ WebSocket disconnected");
    };

    this.socket.onerror = (error) => {
      console.error("⚠️ WebSocket error:", error);
    };

    this.socket.onmessage = (event) => {
      if (!this.onMessageCallback) return;

      try {
        const data = JSON.parse(event.data);
        this.onMessageCallback(data);
      } catch (err) {
        console.error("Invalid JSON from backend", err);
      }
    };
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    }
  }

  onMessage(callback) {
    this.onMessageCallback = callback;
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

export default WebSocketClient;
