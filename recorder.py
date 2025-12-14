import datetime
import json
import os
import time
from pynput import mouse, keyboard
from PIL import ImageGrab

class Recorder:
    def __init__(self, output_dir="session_data"):
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        self.log_file = os.path.join(output_dir, "log.json")
        self.events = []
        self.recording = False
        self.listeners = []
        
        # Ensure directories exist
        os.makedirs(self.images_dir, exist_ok=True)

    def _get_timestamp(self):
        return datetime.datetime.now().isoformat()

    def _save_screenshot(self, event_id):
        filename = f"screenshot_{event_id}.png"
        filepath = os.path.join(self.images_dir, filename)
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            return filepath
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

    def _log_event(self, event_type, details):
        if not self.recording:
            return

        event_id = int(time.time() * 1000)
        screenshot_path = None
        
        # Only screenshot on significant events
        if event_type in ["click", "press_special"]:
             screenshot_path = self._save_screenshot(event_id)

        event = {
            "id": event_id,
            "timestamp": self._get_timestamp(),
            "type": event_type,
            "details": details,
            "screenshot": screenshot_path
        }
        self.events.append(event)
        print(f"Logged: {event_type} - {details}")

        # Write to file immediately (append mode could be safer, but rewriting list for simplicity)
        with open(self.log_file, "w") as f:
            json.dump(self.events, f, indent=4)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self._log_event("click", {"x": x, "y": y, "button": str(button)})

    def on_press(self, key):
        try:
            self._log_event("press", {"key": key.char})
        except AttributeError:
             # Handle special keys differently if needed
             if key == keyboard.Key.enter:
                 self._log_event("press_special", {"key": "enter"})
             elif key == keyboard.Key.esc:
                 self.stop_recording()

    def start_recording(self):
        print(f"Recording started. Saving to {self.output_dir}")
        self.recording = True
        self.events = [] # Clear previous session in memory

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        self.mouse_listener.join()
        self.keyboard_listener.join()

    def stop_recording(self):
        print("Stopping recording...")
        self.recording = False
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
