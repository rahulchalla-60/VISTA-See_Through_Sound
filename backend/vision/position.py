def get_object_position(bbox, frame_width):
    """
    Determines whether an object is on the left, center, or right of the frame.

    Args:
        bbox (list): [x1, y1, x2, y2]
        frame_width (int): width of the video frame

    Returns:
        str: 'left', 'center', or 'right'
    """

    x1, _, x2, _ = bbox

    # Center of the bounding box
    object_center_x = (x1 + x2) / 2

    # Define regions
    left_boundary = frame_width / 3
    right_boundary = (frame_width / 3) * 2

    if object_center_x < left_boundary:
        return "left"
    elif object_center_x > right_boundary:
        return "right"
    else:
        return "center"
