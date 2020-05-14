from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

from kivymd.toast import toast


class RegisterScreen(Screen):
    def __init__(self, con, cursor, cipher, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

    def registerBtn(self):
        password_field = self.ids.reg_pass_input
        confirm_password_field = self.ids.reg_confirm_pass_input

        if not password_field.text:
            self.initFieldError(password_field)

        elif password_field.text == confirm_password_field.text:
            self.manager.connectDatabase()

            encrypted = self.cipher.encrypt(password_field.text)

            self.cursor.execute("INSERT INTO password VALUES(?)",(encrypted,))
            self.con.commit()

            self.manager.setMainScreen()

        else:
            self.initFieldError(confirm_password_field)

    def showPasswordBtn(self):
        button = self.ids.reg_show_password_btn
        input_1 = self.ids.reg_pass_input
        input_2 = self.ids.reg_confirm_pass_input

        if button.icon == "eye-outline":
            input_1.password = False
            input_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input_1.password = True
            input_2.password = True
            button.icon = "eye-outline"

    def checkPasswordField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkPasswords(self, instance, text):
        if not text:
            return

        if text != self.ids.reg_pass_input.text:
            self.initFieldError(instance)

        else:
            self.closeFieldError(instance)

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
