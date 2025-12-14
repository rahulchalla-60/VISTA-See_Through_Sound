class SpatialAnalysis:
    def __init__(self):
        """
        Minimal SpatialAnalysis class
        - No initialization parameters required
        - frame_width passed as parameter to classify_position
        """
        pass  # No initialization needed for minimal version
    
    def classify_position(self, box, frame_width):
        x1, _, x2, _ = box
        cx = (x1 + x2) / 2

        if cx < frame_width / 3:
            return "left"
        elif cx < 2 * frame_width / 3:
            return "center"
        else:
            return "right"
    
    def estimate_distance(self, box, scale_factor=1000):
        _, y1, _, y2 = box
        height = y2 - y1
        if height == 0:
            return None
        return round(scale_factor / height, 1)
