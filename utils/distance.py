import numpy as np

class DistanceCalculator:
    def __init__(self):
        # Known average distance between human eyes in centimeters
        self.KNOWN_WIDTH = 6.3  # Average human interpupillary distance
        
        # Focal length approximation (needs calibration for more accurate results)
        self.focal_length = None
        
        # For calibration
        self.calibrated = False
        self.calibration_distance = 60  # cm - typical distance user might be from screen

    def calibrate(self, pixel_width):
        """
        Calibrate the system to better estimate distances
        """
        self.focal_length = (pixel_width * self.calibration_distance) / self.KNOWN_WIDTH
        self.calibrated = True
        return self.focal_length

    def calculate(self, frame, eye_landmarks):
        """
        Calculate the distance from the camera to the face
        """
        if eye_landmarks is None:
            return None
        
        left_eye, right_eye = eye_landmarks
        
        # Calculate the center of each eye
        left_eye_center = np.mean(left_eye, axis=0).astype(int)
        right_eye_center = np.mean(right_eye, axis=0).astype(int)
        
        # Calculate the pixel distance between the eyes
        pixel_width = np.sqrt(
            (right_eye_center[0] - left_eye_center[0]) ** 2 +
            (right_eye_center[1] - left_eye_center[1]) ** 2
        )
        
        # If not calibrated, calibrate first
        if not self.calibrated:
            self.calibrate(pixel_width)
        
        # Calculate distance using the formula: distance = (known_width * focal_length) / pixel_width
        distance = (self.KNOWN_WIDTH * self.focal_length) / pixel_width
        
        return distance
