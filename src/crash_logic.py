class CrashDetector:
    def __init__(self):
        # We require vibration to be detected for X consecutive readings 
        # to filter out a single random bump/pothole.
        self.vibration_streak = 0
        self.required_streak = 3 

    def evaluate(self, current_reading):
        """
        Evaluate the latest sensor reading. Returns True if a crash is detected.
        We detect a crash using sustained vibration from the SW-420.
        """
        is_crash = False
        
        # 1. Vibration Logic (SW-420)
        if current_reading.get("vibration_detected"):
            self.vibration_streak += 1
        else:
            self.vibration_streak = 0
            
        if self.vibration_streak >= self.required_streak:
            print(f"CRASH DETECTED: Sustained vibration ({self.vibration_streak} ticks)")
            is_crash = True
            
        return is_crash
