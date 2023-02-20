import sqlite3

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition, NoTransition

from kivymd.theming import ThemeManager

import psycopg2

import cryptography
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .registerscreen import RegisterScreen
from .loginscreen import LoginScreen
from .mainscreen import MainScreen
from .addaccountscreen import AddAccountScreen
from .optionsscreen import (
    OptionsScreen,
    AppearanceOptionsScreen,
    DatabaseOptionsScreen,
    SecurityOptionsScreen,
    ChangeMasterPasswordScreen,
    PasswordSuggestionOptionsScreen,
)


class Manager(ScreenManager):
    con = None
    cursor = None

    cipher = None

    pg_con = None
    pg_cursor = None

    internet_connection = True

    register_screen = None
    login_screen = None
    main_screen = None
    add_account_screen = None

    options_screen = None
    appearance_options_screen = None
    database_options_screen = None
    security_options_screen = None
    change_master_password_screen = None
    password_suggestion_options = None

    master_password_exists = False
    file_manager_open = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Window.bind(on_keyboard=self.on_key)

        self.theme_cls = ThemeManager()

        self.options_screen_names = [
            "appearance_options_screen",
            "database_options_screen",
            "security_options_screen",
            "password_suggestion_options_screen",
        ]

        self.setStartScreen()

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if (
                self.current_screen.name == "register_screen"
                or self.current_screen.name == "login_screen"
                or self.current_screen.name == "main_screen"
            ):
                return False  # exit the app

            elif (
                self.current_screen.name == "add_account_screen"
                or self.current_screen.name == "options_screen"
            ):
                self.setMainScreen()
                return True  # do not exit the app

            elif self.file_manager_open == True:
                self.database_options_screen.file_manager.back()
                return True

            elif self.current_screen.name in self.options_screen_names:
                self.setOptionsScreen()
                return True

            elif self.current_screen.name == "change_master_password_screen":
                self.setSecurityOptionsScreen()
                return True

    def connectDatabase(self):
        self.con = sqlite3.connect("pass.db", check_same_thread=False)
        self.cursor = self.con.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS accounts (id TEXT, site TEXT, email TEXT, username TEXT, password TEXT, twofa TEXT)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS options (master_password TEXT, salt TEXT, sort_by TEXT, list_subtitles TEXT, animation_options TEXT, auto_backup INT, auto_backup_location TEXT, remote_database INT, db_name TEXT, db_user TEXT, db_pass TEXT, db_host TEXT, db_port TEXT, fast_login INT, auto_exit INT, password_length INT, password_suggestion_options TEXT)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS offline_queries (id INTEGER PRIMARY KEY, query TEXT)"
        )

    def connectRemoteDatabase(self, pg_data):
        def connect():
            try:
                self.pg_con = psycopg2.connect(
                    database=pg_data[1],
                    user=pg_data[2],
                    password=pg_data[3],
                    host=pg_data[4],
                    port=pg_data[5],
                )
                self.pg_cursor = self.pg_con.cursor()

                self.pg_cursor.execute(
                    "CREATE TABLE IF NOT EXISTS accounts (id TEXT, site TEXT, email TEXT, username TEXT, password TEXT, twofa TEXT)"
                )
                self.pg_cursor.execute(
                    "CREATE TABLE IF NOT EXISTS options (master_password TEXT, salt TEXT)"
                )

                self.internet_connection = True
            except:
                self.internet_connection = False

        if pg_data is not None:
            if all(pg_data):
                Clock.schedule_once(lambda _: connect())

    def runRemoteDatabaseQuery(self, query):
        def run_query(query):
            try:
                self.pg_cursor.execute(query)
                self.pg_con.commit()

                self.internet_connection = True
            except Exception as error:
                print(error)

                self.cursor.execute(
                    "INSERT INTO offline_queries (query) VALUES(?)", (query,)
                )
                self.con.commit()

                self.internet_connection = False

        Clock.schedule_once(lambda _: run_query(query))

    def createCipher(self, password, salt):
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=2**3, p=1)

        key = kdf.derive(password.encode())
        cipher = AESGCM(key)

        return cipher

    def getCipher(self, password):
        self.cursor.execute("SELECT master_password, salt FROM options")
        encrypted, salt = map(bytes.fromhex, self.cursor.fetchone())

        cipher = self.createCipher(password, salt)

        try:
            result = cipher.decrypt(encrypted[:16], encrypted[16:], None)
            if result.decode() == password:
                self.cipher = cipher
                return True
        except cryptography.exceptions.InvalidTag:
            return False

    def checkMasterPasswordExists(self):
        self.cursor.execute("SELECT master_password FROM options")
        encrypted = self.cursor.fetchone()

        self.master_password_exists = True if encrypted else False

    def initOptionsScreen(self):
        self.appearance_options_screen = AppearanceOptionsScreen(
            con=self.con, cursor=self.cursor, name="appearance_options_screen"
        )
        self.database_options_screen = DatabaseOptionsScreen(
            con=self.con, cursor=self.cursor, name="database_options_screen"
        )
        self.security_options_screen = SecurityOptionsScreen(
            con=self.con, cursor=self.cursor, name="security_options_screen"
        )
        self.password_suggestion_options_screen = PasswordSuggestionOptionsScreen(
            con=self.con, cursor=self.cursor, name="password_suggestion_options_screen"
        )

    def setStartScreen(self):
        self.connectDatabase()

        self.cursor.execute(
            "SELECT remote_database, db_name, db_user, db_pass, db_host, db_port FROM options"
        )
        pg_data = self.cursor.fetchone()
        self.connectRemoteDatabase(pg_data)

        self.checkMasterPasswordExists()

        if self.master_password_exists:
            self.setLoginScreen()
        else:
            self.setRegisterScreen()

    def setRegisterScreen(self):
        Window.softinput_mode = ""

        self.register_screen = RegisterScreen(
            con=self.con, cursor=self.cursor, name="register_screen"
        )
        self.add_widget(self.register_screen)
        self.current = "register_screen"

    def setLoginScreen(self):
        Window.softinput_mode = ""

        if self.has_screen("login_screen"):
            self.remove_widget(self.login_screen)  # this if statement for reset screen
            del self.login_screen

        # always run in this method
        self.login_screen = LoginScreen(cursor=self.cursor, name="login_screen")
        self.add_widget(self.login_screen)
        self.current = "login_screen"

    def setMainScreen(self):
        Window.release_keyboard()  # for autoLogin function in loginscreen.py
        Window.softinput_mode = ""

        if self.has_screen("main_screen"):
            self.main_screen.initUI()
            self.current = "main_screen"

        else:
            self.initOptionsScreen()

            self.main_screen = MainScreen(
                con=self.con,
                cursor=self.cursor,
                pg_con=self.pg_con,
                pg_cursor=self.pg_cursor,
                cipher=self.cipher,
                internet_connection=self.internet_connection,
                name="main_screen",
            )
            self.add_widget(self.main_screen)
            self.current = "main_screen"

    def setAddAccountScreen(self):
        Window.softinput_mode = "below_target"

        if self.has_screen("add_account_screen"):
            self.remove_widget(
                self.add_account_screen
            )  # this if statement for reset screen
            del self.add_account_screen

        # always run in this method
        self.add_account_screen = AddAccountScreen(
            con=self.con,
            cursor=self.cursor,
            cipher=self.cipher,
            name="add_account_screen",
        )
        self.add_widget(self.add_account_screen)
        self.current = "add_account_screen"

    def setOptionsScreen(self):
        if self.current_screen.name == "appearance_options_screen":
            self.appearance_options_screen.getOptions()  # update self.animation_options
            self.transition = (
                FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark)
                if self.appearance_options_screen.animation_options[0]
                else NoTransition()
            )

        if self.has_screen("options_screen"):
            self.current = "options_screen"

        else:
            self.options_screen = OptionsScreen(name="options_screen")
            self.add_widget(self.options_screen)
            self.current = "options_screen"

    def setAppearanceOptionsScreen(self):
        if self.has_screen("appearance_options_screen"):
            self.current = "appearance_options_screen"

        else:
            self.add_widget(self.appearance_options_screen)
            self.current = "appearance_options_screen"

    def setDatabaseOptionsScreen(self):
        if self.has_screen("database_options_screen"):
            self.current = "database_options_screen"

        else:
            self.add_widget(self.database_options_screen)
            self.current = "database_options_screen"

    def setSecurityOptionsScreen(self):
        if self.has_screen("security_options_screen"):
            self.current = "security_options_screen"

        else:
            self.add_widget(self.security_options_screen)
            self.current = "security_options_screen"

    def setChangeMasterPasswordScreen(self):
        Window.softinput_mode = "below_target"

        if self.has_screen("change_master_password_screen"):
            self.remove_widget(
                self.change_master_password_screen
            )  # this if statement for reset screen
            del self.change_master_password_screen

        # always run in this method
        self.change_master_password_screen = ChangeMasterPasswordScreen(
            con=self.con,
            cursor=self.cursor,
            cipher=self.cipher,
            name="change_master_password_screen",
        )
        self.add_widget(self.change_master_password_screen)
        self.current = "change_master_password_screen"

    def setPasswordSuggestionOptionsScreen(self):
        if self.has_screen("password_suggestion_options_screen"):
            self.current = "password_suggestion_options_screen"

        else:
            self.add_widget(self.password_suggestion_options_screen)
            self.current = "password_suggestion_options_screen"
