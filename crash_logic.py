class CrashDetector:
    def __init__(self):
        # We require vibration to be detected for X consecutive readings 
        # to filter out a single random bump/pothole.
        self.vibration_streak = 0
        self.required_streak = 3 
        
        self.accel_threshold_g = 3.0 # High G-force threshold

    def evaluate(self, current_reading):
        """
        Evaluate the latest sensor reading. Returns True if a crash is detected.
        We can detect a crash using EITHER a sustained vibration OR a massive G-force spike.
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
            
        # 2. Accelerometer Logic (MPU6050 - if connected)
        accel = current_reading.get("acceleration_g", 1.0)
        if accel > self.accel_threshold_g:
            print(f"CRASH DETECTED: High G-force spike ({accel}G)")
            is_crash = True
            
        return is_crash
