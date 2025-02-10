from kivy.app import App
from kivy.app import Widget
from app import scan_product


class MyLayout(Widget):

    def press(self):
        product = scan_product()
        self.code = product["code"]
        return print(self.code)


class FirstApp(App):
    def build(self):
        return MyLayout()


if __name__ == "__main__":
    FirstApp().run()
