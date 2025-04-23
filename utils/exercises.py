class EyeExercises:
    def __init__(self):
        # List of eye exercises with instructions and duration
        self.exercises = [
            {
                "name": "Focus Change",
                "instructions": "Hold your finger a few inches from your eye. Focus on it. Slowly move your finger away. Focus far away, then back on your finger.",
                "duration": 10  # seconds
            },
            {
                "name": "20-20-20",
                "instructions": "Look at something at least 20 feet away for 20 seconds.",
                "duration": 20  # seconds
            },
            {
                "name": "Eye Rolling",
                "instructions": "Roll your eyes in a clockwise direction for 10 seconds, then counterclockwise for 10 seconds.",
                "duration": 20  # seconds
            },
            {
                "name": "Palming",
                "instructions": "Rub your hands together until warm. Place them over your closed eyes for 10 seconds without pressing on the eyes.",
                "duration": 10  # seconds
            }
        ]
    
    def get_one_minute_routine(self):
        """
        Returns a sequence of exercises that total 60 seconds
        """
        return self.exercises
    
    def get_exercise_by_index(self, index):
        """
        Get a specific exercise by index
        """
        if 0 <= index < len(self.exercises):
            return self.exercises[index]
        return None
