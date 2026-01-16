def estimate_distance(bbox, frame_height):
    """
    Estimates relative distance of an object based on bounding box height.

    Args:
        bbox (list): [x1, y1, x2, y2]
        frame_height (int): height of the video frame

    Returns:
        str: 'very near', 'near', 'far', or 'very far'
    """

    _, y1, _, y2 = bbox
    box_height = y2 - y1

    # Normalize box height with frame height
    height_ratio = box_height / frame_height

    if height_ratio > 0.6:
        return "very near"
    elif height_ratio > 0.4:
        return "near"
    elif height_ratio > 0.2:
        return "far"
    else:
        return "very far"
