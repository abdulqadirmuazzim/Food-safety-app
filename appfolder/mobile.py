from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from pyzbar import pyzbar  # For barcode decoding
import time
from pydub import AudioSegment
from pydub.playback import play
from api import call_api
import time

beep = AudioSegment.from_wav("beep.wav")

#


class WelcomeScreen(Screen):
    # When the user presses the scan button
    def scan_prod(self):
        if self.manager:
            print("product scanned!")
            print(self.manager.current)
            self.manager.current = "scan_code"


class ProductInfo(Screen):

    update = ObjectProperty(None)
    grid = ObjectProperty(None)
    textInput = ObjectProperty(None)

    def update_info(self):

        # label = Label(text="some info here")  # we can add a label or
        info = TextInput(
            text="some info",
            background_color=(0, 0, 0, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=40,
        )

        self.update.text = "Update"
        self.textInput.readonly = False
        self.grid.add_widget(info)


# page for scanning the barcode
class ScanBarcodePage(Screen):
    def __init__(self, **kwargs):
        super(ScanBarcodePage, self).__init__(**kwargs)
        self.box = BoxLayout(orientation="vertical")
        self.add_widget(self.box)

        # camera preview widget
        self.camera = Image()
        self.box.add_widget(self.camera)

        # add a home button
        self.home_button = Button(
            text="Back to home",
            size_hint=(0.3, 0.1),
            font_size=25,
            on_press=self.back_to_home,
        )
        self.add_widget(self.home_button)

        # Initialize opencv
        self.capture = None
        self.frame_size = (640, 480)
        # self.manager = ScreenManager()

        # barcode scanner
        self.barcode = None
        self.scan_code = False

        print("Screen Manager", self.manager)
        if self.manager == None:
            print("it's None")

    def back_to_home(self, event):
        self.manager.current = "welcome"

    def on_enter(self, *args):
        self.start_camera()

    def on_leave(self, *args):
        self.stop_scan()

    def start_camera(self):
        if self.manager.current == "scan_code" and not self.scan_code:
            self.scan_code = True
            # initialize the camera
            self.capture = cv2.VideoCapture(0)
            # start clock
            self.update_event = Clock.schedule_interval(self.update, 1 / 30)

    def update(self, clock):
        if self.scan_code and self.capture and self.capture.isOpened():
            success, frame = self.capture.read()
            # if the camera was successfully activated:
            if success:
                frame = cv2.resize(frame, self.frame_size)
                if not self.scan_code:
                    self.stop_scan()
                    self.manager.current = "product_info"
                    return
                else:
                    self.scan(frame)
                    self.make_api_call()

                # Convert to texture for Kivy display
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=frame.shape[1::-1], colorfmt="bgr")
                texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.camera.texture = texture

    # A function to scan the barcode
    def scan(self, frame):
        codes = pyzbar.decode(frame)

        for code in codes:
            if code.data != "":
                self.barcode = code.data.decode("utf-8")
                play(beep)
                print("Barcode detected:", self.barcode)

    def make_api_call(self):
        if self.barcode:
            params = {
                "fields": "product_name,_id,nutriscore_score,nutrition_grades,nutriscore_data,nutriments,misc_tags"
            }
            required_fields = [
                "energy",
                "energy-kcal",
                "fat",
                "saturated-fat",
                "carbohydrates",
                "sugars",
                "fiber",
                "proteins",
                "salt",
                "sodium",
            ]
            response = call_api(self.barcode, params=params)
            print(response)
            self.barcode = None
            self.stop_scan()

    def stop_scan(self):
        if self.scan_code and self.capture and self.capture.isOpened():
            self.update_event.cancel()
            self.scan_code = False
            self.capture.release()
            self.capture = None
            if self.manager:
                self.manager.current = "product_info"


# class CameraPage(Screen):
#     def capture(self):
#         camera = self.ids["camera"]
#         timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
#         camera.export_to_png(f"{timestr}_image.png")
#         self.manager.current = "product_info"
#         print("Image captured")

#     def change_cam(self):
#         camera = self.ids["camera"]
#         if camera.index == 0:
#             camera.index += 1
#         elif camera.index == 1:
#             camera.index -= 1
#         else:
#             camera.index = camera.index


app = Builder.load_file("food.kv")


class MyApp(App):

    def build(self):

        self.screen_manager = ScreenManager()

        welcome_screen = WelcomeScreen()
        scanning_page = ScanBarcodePage()
        product_info_page = ProductInfo()

        self.screen_manager.add_widget(welcome_screen)
        self.screen_manager.add_widget(scanning_page)
        self.screen_manager.add_widget(product_info_page)
        return app


MyApp().run()
