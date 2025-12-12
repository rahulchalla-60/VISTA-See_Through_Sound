import cv2

class CameraNode:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)

    def stream(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Return frame live to next node
            yield {"frame": frame}

            # Quit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Camera stopped by user (q pressed).")
                break

        self.release()

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()