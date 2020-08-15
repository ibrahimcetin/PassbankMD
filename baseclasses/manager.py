from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition, NoTransition
from kivy.core.window import Window

from pyaes import AESCipher
from baseclasses.registerscreen import RegisterScreen
from baseclasses.loginscreen import LoginScreen
from baseclasses.mainscreen import MainScreen
from baseclasses.addaccountscreen import AddAccountScreen
from baseclasses.optionsscreen import OptionsScreen, DatabaseOptionsScreen

import os
import sqlite3


class Manager(ScreenManager):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.transition = NoTransition() # FadeTransition(duration=0.2, clearcolor=app.theme_cls.bg_dark)
        # FadeTransition disabled because when run on_resume (or on_pause) method, it give error.
        Window.bind(on_keyboard=self.on_key)

        self.con = None
        self.cursor = None
        self.cipher = None
        self.password = None
        self.file_manager_open = None

        self.setStartScreen()

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.current_screen.name == "register_screen" or self.current_screen.name == "login_screen" or self.current_screen.name == "main_screen":
                return False # exit the app

            elif self.current_screen.name == "add_account_screen" or self.current_screen.name == "options_screen":
                self.setMainScreen()
                return True # do not exit the app

            elif self.current_screen.name == "database_options_screen":
                self.setOptionsScreen()
                return True

            if self.file_manager_open == True:
                self.database_options_screen.file_manager.back()
                return True

    def connectDatabase(self):
        self.con = sqlite3.connect("pass.db")
        self.cursor = self.con.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS accounts (site TEXT, email TEXT, username TEXT, password TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS options (master_password TEXT, sort_by TEXT, auto_backup INT, auto_backup_location TEXT, fast_login INT)")

    def getCipher(self):
        key = "F:NnQw}c(06BdclrX8_mJbGq]i#m5&hw"
        iv = "lA%u]-hF&GRx{P`s"

        self.cipher = AESCipher(key, iv)

    def getPasswordFromDB(self):
        self.cursor.execute("SELECT master_password FROM options")
        encrypted = self.cursor.fetchone()

        if encrypted:
            self.password = self.cipher.decrypt(encrypted[0])

        else:
            self.password = False

    def setStartScreen(self):
        self.connectDatabase()
        self.getCipher()
        self.getPasswordFromDB()

        if self.password:
            self.setLoginScreen()
        else:
            self.setRegisterScreen()

    def setRegisterScreen(self):
        Window.softinput_mode = ""

        Builder.load_file("kv/register_screen.kv")

        self.register_screen = RegisterScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="register_screen")
        self.add_widget(self.register_screen)
        self.current = "register_screen"

    def setLoginScreen(self):
        Window.softinput_mode = ""

        if self.has_screen("login_screen"):
            self.remove_widget(self.login_screen) # this if statement for reset screen
            del self.login_screen

        else:
            Builder.load_file("kv/login_screen.kv") # for load once

        # always run in this method
        self.login_screen = LoginScreen(cursor=self.cursor, cipher=self.cipher, password=self.password, name="login_screen")
        self.add_widget(self.login_screen)
        self.current = "login_screen"

    def setMainScreen(self):
        Window.release_keyboard() # for autoLogin function in loginscreen.py
        Window.softinput_mode = ""

        if self.has_screen("main_screen"):
            self.main_screen.initUI()
            self.current = "main_screen"

        else:
            Builder.load_file("kv/main_screen.kv")

            self.main_screen = MainScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="main_screen")
            self.add_widget(self.main_screen)
            self.current = "main_screen"

    def setAddAccountScreen(self):
        Window.softinput_mode = "below_target"

        if self.has_screen("add_account_screen"):
            self.remove_widget(self.add_account_screen) # this if statement for reset screen
            del self.add_account_screen

        else:
            Builder.load_file("kv/add_account_screen.kv") # for load once

        # always run in this method
        self.add_account_screen = AddAccountScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="add_account_screen")
        self.add_widget(self.add_account_screen)
        self.current = "add_account_screen"

    def setOptionsScreen(self):
        Window.softinput_mode = ""

        if self.has_screen("options_screen"):
            self.current = "options_screen"

        else:
            Builder.load_file("kv/options_screen.kv") # for load once

            self.options_screen = OptionsScreen(name="options_screen")
            self.add_widget(self.options_screen)
            self.current = "options_screen"

    def setDatabaseOptionsScreen(self):
        Window.softinput_mode = ""

        if self.has_screen("database_options_screen"):
            self.current = "database_options_screen"

        else:
            self.database_options_screen = DatabaseOptionsScreen(con=self.con, cursor=self.cursor, name="database_options_screen")
            self.add_widget(self.database_options_screen)
            self.current = "database_options_screen"
