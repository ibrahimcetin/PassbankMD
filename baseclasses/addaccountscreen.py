from kivy.uix.screenmanager import Screen

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
            if site == "":
                toast("Site is required")

            elif password == "" or confirm_password == "":
                toast("Password is required")

            else:
                encrypted = self.cipher.encrypt(password)

                self.cursor.execute("INSERT INTO accounts VALUES(?,?,?,?)",(site, email, username, encrypted))
                self.con.commit()

                toast(f"{site} account added")

                self.manager.setMainScreen()

        else:
            toast("Passwords not match")

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
