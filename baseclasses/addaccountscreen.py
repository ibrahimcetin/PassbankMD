from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

from kivymd.toast import toast


class AddAccountScreen(Screen):
    def __init__(self, con, cursor, cipher, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

    def goBackBtn(self):
        self.manager.setMainScreen()

    def addAccountBtn(self):
        site = self.ids.add_acc_site_input.text
        email = self.ids.add_acc_email_input.text
        username = self.ids.add_acc_username_input.text

        password = self.ids.add_acc_pass_input.text
        confirm_password = self.ids.add_acc_conf_pass_input.text

        if password == confirm_password:
            if not site:
                instance = self.ids.add_acc_site_input
                self.initFieldError(instance)

            elif not password:
                instance = self.ids.add_acc_pass_input
                self.initFieldError(instance)

            else:
                encrypted = self.cipher.encrypt(password)

                self.cursor.execute("INSERT INTO accounts VALUES(?,?,?,?)",(site, email, username, encrypted))
                self.con.commit()

                toast(f"{site} Account Added")

                self.manager.setMainScreen()

        else:
            instance = self.ids.add_acc_conf_pass_input
            self.initFieldError(instance)

    def showPasswordBtn(self):
        button = self.ids.add_acc_show_password_btn
        input_1 = self.ids.add_acc_pass_input
        input_2 = self.ids.add_acc_conf_pass_input

        if button.icon == "eye-outline":
            input_1.password = False
            input_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input_1.password = True
            input_2.password = True
            button.icon = "eye-outline"

    def checkField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkConfirmField(self, instance, text):
        if not text:
            return

        if text != self.ids.add_acc_pass_input.text:
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
