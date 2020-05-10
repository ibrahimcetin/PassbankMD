from kivy.uix.screenmanager import Screen

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

        if password_field.text == "":
            toast("Password required")

        elif password_field.text == confirm_password_field.text:
            self.manager.connectDatabase()

            encrypted = self.cipher.encrypt(password_field.text)

            self.cursor.execute("INSERT INTO password VALUES(?)",(encrypted,))
            self.con.commit()

            self.manager.setMainScreen()

        else:
            toast("Passwords not match")

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
