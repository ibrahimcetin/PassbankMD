from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

class LoginScreen(Screen):
    def __init__(self, con, cursor, cipher, password, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

        self.password = password

    def loginBtn(self):
        instance = self.ids.login_pass_input

        if not self.ids.login_pass_input.text:
            self.initFieldError(instance)

        elif self.password == self.ids.login_pass_input.text:
            self.manager.setMainScreen()

        else:
            self.initFieldError(instance)

    def showPasswordBtn(self):
        button = self.ids.login_show_password_btn
        input = self.ids.login_pass_input

        if button.icon == "eye-outline":
            input.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input.password = True
            button.icon = "eye-outline"

    def checkPassword(self, instance, text): # Works after pressing enter
        if text == self.password:
            self.loginBtn()

        else:
            self.initFieldError(instance)

    def autoLogin(self, instance, text): # Running always
        if not text:
            return

        else:
            self.closeFieldError(instance)

            if text == self.password:
                self.loginBtn()

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
