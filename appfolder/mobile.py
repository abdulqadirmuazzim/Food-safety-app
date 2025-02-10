from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


# from api import call_api


class WelcomeScreen(Screen):
    def scan_prod(self):
        # api = call_api(
        #     params={"fields": "product_name,code,nutrient_grade,nutriscore_score"}
        # )
        print("product scanned!")


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


class CameraPage(Screen):
    def capture(self):
        cam = self.ids["camera"]
        cam.export_to_png("image.png")
        print("Image captured")


app = Builder.load_file("food.kv")


class MyApp(App):
    def build(self):
        return app


MyApp().run()
