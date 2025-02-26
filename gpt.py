from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
import numpy as np
from pyzbar.pyzbar import decode  # For barcode scanning


class BarcodeScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # Camera Feed Display
        self.image = Image()
        self.add_widget(self.image)

        # Label for displaying barcode result
        self.result_label = Label(text="Scan a barcode...", size_hint_y=None, height=50)
        self.add_widget(self.result_label)

        # OpenCV Camera Capture
        self.capture = cv2.VideoCapture(0)  # Use the first available camera
        self.fps = 30
        self.start_scanning()

    def start_scanning(self):
        """Continuously capture frames from the camera and detect barcodes"""
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)  # Flip the image for correct orientation
            decoded_objects = decode(frame)  # Scan for barcodes

            for obj in decoded_objects:
                barcode_data = obj.data.decode("utf-8")
                self.result_label.text = (
                    f"Detected: {barcode_data}"  # Update label with barcode
                )

                # Draw a bounding box around detected barcode
                pts = np.array(obj.polygon, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

            # Convert the frame to Kivy texture
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
            )
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.image.texture = texture

        # Schedule next frame update
        App.get_running_app().root_window.bind(on_draw=self.start_scanning())

    def on_stop(self):
        """Release the camera when the app stops"""
        self.capture.release()


class BarcodeScannerApp(App):
    def build(self):
        return BarcodeScanner()


if __name__ == "__main__":
    BarcodeScannerApp().run()
