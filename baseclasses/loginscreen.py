from kivy.uix.screenmanager import Screen

class LoginScreen(Screen):
    def __init__(self, con, cursor, cipher, password, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

        self.password = password

        #self.check_input_schedule = Clock.schedule_interval(self.checkInput, 0)

    def getPasswordFromDB(self):
        self.cursor.execute("SELECT password FROM password")
        encrypted = self.cursor.fetchall()[0][0]
        self.password = self.cipher.decrypt(encrypted)

    def loginBtn(self):
        if self.password == self.ids.login_pass_input.text:
            self.ids.login_pass_input.error = False
            self.manager.setMainScreen()

        else:
            self.ids.login_pass_input.error = True
    """
    def checkInput(self, *args):
        if self.password == self.ids.login_pass_input.text:
            self.ids.login_pass_input.error = False
            self.sm.current = "main_screen"

            self.check_input_schedule.cancel()

        # TODO: hide keyboard
    """
    def showPasswordBtn(self):
        button = self.ids.login_show_password_btn
        input = self.ids.login_pass_input

        if button.icon == "eye-outline":
            input.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input.password = True
            button.icon = "eye-outline"
