from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition, NoTransition
from kivy.core.window import Window

from pyaes import AESCipher
from baseclasses.registerscreen import RegisterScreen
from baseclasses.loginscreen import LoginScreen
from baseclasses.mainscreen import MainScreen
from baseclasses.addaccountscreen import AddAccountScreen

import os
import sqlite3


class Manager(ScreenManager):
    def __init__(self, app, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)

        self.transition = NoTransition() # FadeTransition(duration=0.2, clearcolor=app.theme_cls.bg_dark)
        # FadeTransition disabled because when run on_resume (or on_pause) method, it give error.
        Window.bind(on_keyboard=self.on_key)

        self.setStartScreen()

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.current_screen.name == "register_screen" or self.current_screen.name == "login_screen" or self.current_screen.name == "main_screen":
                return False # exit the app

            if self.current_screen.name == "add_account_screen":
                self.setMainScreen()
                return True # do not exit the app

    def connectDatabase(self):
        if not os.path.isdir("/sdcard/passbank"):
            os.mkdir("/sdcard/passbank")

        self.con = sqlite3.connect("/sdcard/passbank/pass.db")
        self.cursor = self.con.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS accounts (site TEXT, email TEXT, username TEXT, password TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS password (password TEXT)")

    def getCipher(self):
        key = "F:NnQw}c(06BdclrX8_mJbGq]i#m5&hw"
        iv = "lA%u]-hF&GRx{P`s"

        self.cipher = AESCipher(key, iv)

    def getPasswordFromDB(self):
        self.cursor.execute("SELECT password FROM password")
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
        Builder.load_file("kv/register_screen.kv")

        self.register_screen = RegisterScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="register_screen")
        self.add_widget(self.register_screen)
        self.register_screen.manager = self
        self.current = "register_screen"

    def setLoginScreen(self):
        if self.has_screen("login_screen"):
            self.remove_widget(self.login_screen) # this if statement for reset screen
            del self.login_screen

        else:
            Builder.load_file("kv/login_screen.kv") # for load once

        # always run in this method
        self.login_screen = LoginScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, password=self.password, name="login_screen")
        self.add_widget(self.login_screen)
        self.login_screen.manager = self # This line exists because if when i giving 'self'(manager) as argument to PostDownloaderScreen, i get error. This is a escape from error.
        self.current = "login_screen"

    def setMainScreen(self):
        if self.has_screen("main_screen"):
            self.main_screen.initUI()
            self.current = "main_screen"

        else:
            Builder.load_file("kv/main_screen.kv")

            self.main_screen = MainScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="main_screen")
            self.add_widget(self.main_screen)
            self.main_screen.manager = self
            self.current = "main_screen"

    def setAddAccountScreen(self):
        if self.has_screen("add_account_screen"):
            self.remove_widget(self.add_account_screen) # this if statement for reset screen
            del self.add_account_screen

        else:
            Builder.load_file("kv/add_account_screen.kv") # for load once

        # always run in this method
        self.add_account_screen = AddAccountScreen(con=self.con, cursor=self.cursor, cipher=self.cipher, name="add_account_screen")
        self.add_widget(self.add_account_screen)
        self.add_account_screen.manager = self # This line exists because if when i giving 'self'(manager) as argument to PostDownloaderScreen, i get error. This is a escape from error.
        self.current = "add_account_screen"

