import os

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.utils import platform

from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        # self.manager defined in Screen class when screen added to screen manager

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

    def registerButton(self, password_field, confirm_password_field):
        if not password_field.text:
            self.initFieldError(password_field)

        elif password_field.text == confirm_password_field.text:
            encrypted = self.cipher.encrypt(password_field.text)

            path = os.getenv("EXTERNAL_STORAGE") if platform == "android" else os.path.expanduser("~")

            self.cursor.execute("INSERT INTO options VALUES(?,?,?,?,?,?,?,?,?,?)", (encrypted, "a_to_z", "1,1", "1,1", 0, path, 1, 1, 15, "1,1,1,1"))
            self.con.commit()

            self.manager.setMainScreen()

            self.snackbar = Snackbar(
                text="Make sure that you Remember your Master Password",
                padding="20dp",
                button_text="GOT IT",
                button_color=(1, 0, 1, 1),
                duration=60,
                button_callback=self.closeSnackbar
            )
            self.snackbar.show()

        else:
            self.initFieldError(confirm_password_field)

    def showPasswordButton(self, button, field_1, field_2):
        if button.icon == "eye-outline":
            field_1.password = False
            field_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field_1.password = True
            field_2.password = True
            button.icon = "eye-outline"

    def checkPasswordField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkPasswords(self, instance, text):
        if not text:
            return

        if text != self.ids.password_field.text:
            self.initFieldError(instance)

        else:
            self.closeFieldError(instance)

    def closeSnackbar(self, button):
        self.snackbar.duration = 0

    def initFieldError(self, instance):
        instance.error = True

        Animation(
            duration=0.2, _current_error_color=instance.error_color
        ).start(instance)
        Animation(
            _current_right_lbl_color=instance.error_color,
            _current_hint_text_color=instance.error_color,
            _current_line_color=instance.error_color,
            _line_width=instance.width, duration=0.2, t="out_quad"
        ).start(instance)

    def closeFieldError(self, instance):
        Animation(
            duration=0.2, _current_error_color=(0, 0, 0, 0)
        ).start(instance)
        Animation(
            duration=0.2,
            _current_line_color=instance.line_color_focus,
            _current_hint_text_color=instance.line_color_focus,
            _current_right_lbl_color=instance.line_color_focus,
        ).start(instance)

        instance.error = False
