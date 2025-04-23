import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist

class EyeDetector:
    def __init__(self):
        # Initialize dlib's face detector and facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
        
        # Define indexes for left and right eyes from the 68-point facial landmarks
        self.LEFT_EYE_IDXS = list(range(42, 48))
        self.RIGHT_EYE_IDXS = list(range(36, 42))
        
        # Threshold for EAR to determine if eyes are closed
        self.EAR_THRESHOLD = 0.25
        
        # Store eye landmarks for distance calculation
        self.eye_landmarks = None

    def eye_aspect_ratio(self, eye):
        # Compute the Euclidean distances between the vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        
        # Compute the Euclidean distance between the horizontal eye landmarks
        C = dist.euclidean(eye[0], eye[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

    def shape_to_np(self, shape, dtype="int"):
        # Convert dlib's shape object to numpy array
        coords = np.zeros((68, 2), dtype=dtype)
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        return coords

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)
        
        eyes_open = False
        eyes_detected = False
        
        for rect in rects:
            # Determine facial landmarks
            shape = self.predictor(gray, rect)
            shape = self.shape_to_np(shape)
            
            # Extract eye regions
            leftEye = shape[self.LEFT_EYE_IDXS]
            rightEye = shape[self.RIGHT_EYE_IDXS]
            
            # Store eye landmarks for distance calculation
            self.eye_landmarks = (leftEye, rightEye)
            
            # Calculate EAR for both eyes
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)
            
            # Average the EAR together for both eyes
            ear = (leftEAR + rightEAR) / 2.0
            
            # Draw eye regions
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            
            # Display EAR on frame
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Determine if eyes are open
            eyes_open = ear > self.EAR_THRESHOLD
            eyes_detected = True
            
            # Draw face bounding box
            cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 255, 0), 2)
        
        return frame, eyes_open, eyes_detected
