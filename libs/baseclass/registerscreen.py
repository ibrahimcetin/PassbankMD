import os

from kivy.uix.screenmanager import Screen

from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFlatButton


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        # self.manager defined in Screen class when screen added to screen manager

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

    def initCipher(self, password):
        salt = os.urandom(32)
        cipher = self.manager.createCipher(password, salt)

        nonce = os.urandom(16)
        encrypted = nonce + cipher.encrypt(nonce, password.encode(), None)

        return encrypted, salt

    def registerButton(self, password_field, confirm_password_field):
        if not password_field.text:
            self.initFieldError(password_field)

        elif password_field.text == confirm_password_field.text:
            encrypted, salt = self.initCipher(password_field.text)

            self.cursor.execute(
                "INSERT INTO options VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    encrypted.hex(),
                    salt.hex(),
                    "a_to_z",
                    "1,1",
                    "1,1",
                    0,
                    "",
                    0,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    1,
                    15,
                    "1,1,1,1",
                ),
            )
            self.con.commit()

            self.manager.getCipher(password_field.text)
            self.manager.setMainScreen()

            snackbar = Snackbar(
                text="Make sure that you Remember your Master Password",
                duration=600,
            )
            snackbar.buttons = [
                MDFlatButton(
                    text="GOT IT", text_color=(1, 0, 1, 1), on_press=snackbar.dismiss
                )
            ]
            snackbar.open()

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

    def initFieldError(self, instance):
        instance.error = True

    def closeFieldError(self, instance):
        instance.error = False
