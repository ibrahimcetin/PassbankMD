import shutil
from threading import Thread

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

from kivymd.toast import toast


class AddAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

        self.getOptions()

    def addAccountButton(self, site_field, password_field, confirm_password_field):
        site = site_field.text
        email = self.ids.email_field.text
        username = self.ids.username_field.text

        password = password_field.text
        confirm_password = confirm_password_field.text

        if password == confirm_password:
            if not site:
                self.initFieldError(site_field)

            elif not password:
                self.initFieldError(password_field)

            else:
                encrypted = self.cipher.encrypt(password)

                self.cursor.execute("INSERT INTO accounts VALUES(?,?,?,?)",(site, email, username, encrypted))
                self.con.commit()

                toast(f"{site} Account Added")

                self.manager.setMainScreen() # refresh main screen

                if self.auto_backup: # auto backup
                    shutil.copy2("pass.db", self.auto_backup_location)

                if self.remote_database:
                    query = "INSERT INTO accounts VALUES({},{},{},{})".format(repr(site), repr(email), repr(username), repr(encrypted))
                    try:
                        Thread(target=self.manager.runRemoteDatabaseQuery(query)).start()
                    except:
                        self.cursor.execute("INSERT INTO offline_queries (query) VALUES(?)",(query,))
                        self.con.commit()
                        self.manager.internet_connection = False

        else:
            self.initFieldError(confirm_password_field)

    def getOptions(self):
        self.cursor.execute("SELECT auto_backup, auto_backup_location, remote_database FROM options")
        options = self.cursor.fetchone()

        self.auto_backup = bool(options[0])
        self.auto_backup_location = options[1]
        self.remote_database = bool(options[2])

    def showPasswordBtn(self, button, field_1, field_2):
        if button.icon == "eye-outline":
            field_1.password = False
            field_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field_1.password = True
            field_2.password = True
            button.icon = "eye-outline"

    def checkField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkConfirmField(self, instance, text):
        if not text:
            return

        if text != self.ids.password_field.text:
            self.initFieldError(instance)

        else:
            self.closeFieldError(instance)

    def goBackBtn(self):
        self.manager.setMainScreen()

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
