from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.recycleview.views import RecycleDataViewBehavior

# from kivy.uix.recycleview import RecycleView
import cv2
from pyzbar import pyzbar  # For barcode decoding
from pydub import AudioSegment
from pydub.playback import play
from api import call_api

beep = AudioSegment.from_wav("beep.wav")


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
    nutri_grade = ObjectProperty(None)
    code = ObjectProperty(None)
    data = ListProperty([])

    def update_info(self):

        # label = Label(text="some info here")  # we can add a label or
        print("Info updated")
        self.manager.current = "update_page"

    def on_enter(self, *args):
        app = App.get_running_app()

        if app.current_product:
            product = app.current_product

            for key, items in product.get("nutriments").items():
                self.data.append({"key": key, "item": str(items)})

            barcode = product.get("code")
            grades = product.get("nutrigrades")
            self.code.text = barcode
            self.nutri_grade.text = grades


class LabelClass(RecycleDataViewBehavior, BoxLayout):

    def __init__(self, **kwargs):
        super(LabelClass, self).__init__(**kwargs)
        self.font_size = 20
        self.label = Label(
            font_size=self.font_size,
            size_hint=(0.2, 0.1),
            pos_hint={"y": 0},
            color=(1, 1, 1, 1),
        )

        self.input = Label(
            font_size=self.font_size,
            size_hint=(0.5, 0.1),
            pos_hint={"y": 0},
            # background_normal="",
            color=(1, 1, 1, 1),
            # background_color=(0, 0, 0, 0),
        )
        self.add_widget(self.label)
        self.add_widget(self.input)

    def refresh_view_attrs(self, rv, index, data):
        """This method is automatically called to update data in the RecycleView."""
        self.label.text = data.get("key", "Unknown")
        self.input.text = data.get("item", "N/A")


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
                self.code_data = code
                self.barcode = code.data.decode("utf-8")
                play(beep)
                print("Barcode detected:", self.barcode)

    def make_api_call(self):
        if self.barcode:
            params = {
                "fields": "product_name,_id,nutriscore_score,nutrition_grades,nutriscore_data,nutriments,misc_tags"
            }
            app = App.get_running_app()
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
            # select the nutriment dictionary
            if response:
                nutriments = response.get("nutriments", None)
                # get the nutriscore and grades
                score = response.get("nutriscore_score", None)
                grades = response.get("nutrition_grades", None)
                # get the nutrition data
                nutri_data = {
                    field: nutriments.get(field, None) for field in required_fields
                }
                nutritional_info = {
                    "nutriments": nutri_data,
                    "nutriscore": score,
                    "nutrigrades": grades,
                    "code": self.barcode,
                }

                # Add the nutri_data dict to the app instance for access across other classes
                app.add_scan_data(nutritional_info)

                self.barcode = None
                self.stop_scan()
                return
            else:
                print(self.code_data.rect)
                self.stop_scan()

    def stop_scan(self):
        if self.scan_code and self.capture and self.capture.isOpened():
            self.update_event.cancel()
            self.scan_code = False
            self.capture.release()
            self.capture = None
            self.barcode = None
            if self.manager:
                self.manager.current = "product_info"


class UpdatePage(Screen):
    # This is the page where updates will happen if the Nutrition info is incomplete
    def __init__(self, **kwargs):
        super(UpdatePage, self).__init__(**kwargs)


app = Builder.load_file("food.kv")


class MyApp(App):

    current_product = ObjectProperty(None)
    scan_history = ObjectProperty([])

    def build(self):

        return app

    def add_scan_data(self, product_data):
        self.current_product = product_data
        self.scan_history.append(product_data)


MyApp().run()
