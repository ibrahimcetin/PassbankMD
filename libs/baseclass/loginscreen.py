from kivy.uix.screenmanager import Screen, FadeTransition, NoTransition
from kivy.animation import Animation

from kivymd.theming import ThemeManager


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.cursor = kwargs.get("cursor")

        self.theme_cls = ThemeManager()

        self.getOptions()

    def getOptions(self):
        self.cursor.execute("SELECT animation_options, fast_login FROM options")
        options = self.cursor.fetchone()

        self.transition_animation = bool(int(options[0][0]))
        self.fast_login = bool(options[1])

    def loginButton(self, password_field):
        if not password_field.text:
            password_field.helper_text = "Please enter password"
            self.initFieldError(password_field)

        elif self.manager.getCipher(password_field.text):
            self.manager.transition = (
                FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark)
                if self.transition_animation
                else NoTransition()
            )
            self.manager.setMainScreen()

        else:
            password_field.helper_text = "Password not correct"
            self.initFieldError(password_field)

    def showPasswordButton(self, button, field):
        if button.icon == "eye-outline":
            field.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field.password = True
            button.icon = "eye-outline"

    def fastLogin(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

            if self.manager.getCipher(instance.text):
                self.manager.transition = (
                    FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark)
                    if self.transition_animation
                    else NoTransition()
                )
                self.manager.setMainScreen()

    def initFieldError(self, instance):
        instance.error = True

    def closeFieldError(self, instance):
        instance.error = False
