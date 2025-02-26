from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from pyzbar import pyzbar  # For barcode decoding
import time
from pydub import AudioSegment
from pydub.playback import play
from appfolder import api


sound = AudioSegment.from_wav("beep.wav")


class BarcodeScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Create camera preview widget
        self.camera_preview = Image()
        self.add_widget(self.camera_preview)

        # button
        self.button = Button(
            text="I am A button", size_hint=(0.3, 0.1), on_press=self.say_hi
        )
        self.add_widget(self.button)

        # Initialize OpenCV camera capture
        self.capture = cv2.VideoCapture(0)
        self.frame_size = (640, 480)  # Reduced resolution for better performance

        # Set up barcode scanner parameters
        self.scanning = False
        self.last_barcode = None

        # Start camera processing
        Clock.schedule_interval(self.update, 1.0 / 30)  # 30 fps

    def say_hi(self, event):
        self.scanning = True
        print("Scanning started")

    def update(self, dt):
        # Capture frame from OpenCV
        ret, frame = self.capture.read()
        if ret:
            # Process frame
            frame = cv2.resize(frame, self.frame_size)
            self.process_frame(frame)

            # Convert to texture for Kivy display
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=frame.shape[1::-1], colorfmt="bgr")
            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.camera_preview.texture = texture

    def process_frame(self, frame):
        if not self.scanning:
            return

        # Convert to grayscale for barcode detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect and decode barcodes
        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            # Prevent duplicate scans
            if barcode_data != self.last_barcode:
                self.last_barcode = barcode_data
                self.barcode_detected(barcode_data, barcode_type)

            # Draw bounding box (optional)
            self.draw_barcode(frame, barcode)

    def draw_barcode(self, frame, barcode):
        # Draw rectangle around the barcode
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (10, 255, 220), 2)
        time.sleep(10)

    def barcode_detected(self, data, btype):
        print(f"Detected {btype} barcode: {data}")
        # Add your handling logic here (e.g., show popup, play sound, etc.)
        # Example: self.parent.show_barcode_result(data)
        play(sound)
        api.call_api(code=data)

        # Temporarily stop scanning after detection
        self.scanning = False
        # Clock.schedule_once(self.resume_scanning, 2)

    def resume_scanning(self, dt):
        self.scanning = True
        self.last_barcode = None

    def on_stop(self):
        # Release camera when app stops
        self.capture.release()


class BarcodeScannerApp(App):
    def build(self):
        return BarcodeScanner()

    def on_stop(self):
        self.root.on_stop()


if __name__ == "__main__":
    BarcodeScannerApp().run()
