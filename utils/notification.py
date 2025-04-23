import time
from plyer import notification

class NotificationManager:
    def __init__(self):
        # Store last notification times to prevent notification spam
        self.last_notification_times = {
            "blink": 0,
            "distance": 0,
            "screen_time": 0,
            "custom_break": 0,
            "exercise": 0
        }
        
        # Cooldown periods for different notification types (in seconds)
        self.cooldowns = {
            "blink": 10,         # 10 seconds between blink reminders
            "distance": 30,       # 30 seconds between distance reminders
            "screen_time": 1200,  # 20 minutes (1200 seconds) between screen time reminders
            "custom_break": 60,   # 1 minute between custom break notifications
            "exercise": 300       # 5 minutes between exercise notifications
        }
    
    def notify(self, title, message, notification_type="general"):
        """
        Send desktop notification with spam protection
        """
        current_time = time.time()
        
        # Check cooldown for this notification type
        if notification_type in self.last_notification_times:
            last_time = self.last_notification_times[notification_type]
            cooldown = self.cooldowns.get(notification_type, 0)
            
            if current_time - last_time < cooldown:
                # Still in cooldown period, don't send notification
                return False
        
        try:
            # Send notification
            notification.notify(
                title=title,
                message=message,
                app_name="Eye Care Assistant",
                timeout=10  # notification stays for 10 seconds
            )
            
            # Update last notification time
            if notification_type in self.last_notification_times:
                self.last_notification_times[notification_type] = current_time
            
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False

    def update_cooldown(self, notification_type, new_cooldown):
        """
        Update the cooldown period for a specific notification type
        """
        if notification_type in self.cooldowns:
            self.cooldowns[notification_type] = new_cooldown
            return True
        return False
