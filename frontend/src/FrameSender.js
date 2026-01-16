export default class FrameSender {
  constructor(videoElement, wsClient, fps = 8) {
    this.video = videoElement;
    this.ws = wsClient;
    this.fps = fps;

    this.canvas = document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");

    this.interval = null;
  }

  start() {
    const sendInterval = 1000 / this.fps;

    this.interval = setInterval(() => {
      if (!this.video.videoWidth || !this.video.videoHeight) return;

      this.canvas.width = 640;
      this.canvas.height = 480;

      this.ctx.drawImage(
        this.video,
        0,
        0,
        this.canvas.width,
        this.canvas.height
      );

      this.canvas.toBlob(
        (blob) => {
          if (blob) {
            this.ws.send(blob);
          }
        },
        "image/jpeg",
        0.7
      );
    }, sendInterval);
  }

  stop() {
    clearInterval(this.interval);
  }
}
