from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
#from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.icon_definitions import md_icons
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.toast import toast

import sqlite3
import random
import string
from pyaes import AESCipher

# TODO: Use text field error message instead of toast message

kv_string = """
<BaseScreen>

    MDToolbar:
        title: "Passbank"
        elevation: 10
        pos_hint: {"top": 1}

<RegisterScreen>

    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .7

        MDLabel:
            text: "Welcome to Passbank"
            halign: "center"
            font_style: "Button"

        Widget:

        MDBoxLayout:
            adaptive_height: True

            MDTextField:
                id: reg_pass_input
                hint_text: "Password"
                password: True
                #helper_text_mode: "on_error"

            MDIconButton:
                id: reg_show_password
                icon: "eye-outline"
                on_press: root.showPassword()

        MDTextField:
            id: reg_confirm_pass_input
            hint_text: "Confirm Password"
            password: True
            #helper_text_mode: "on_error"

        MDRaisedButton:
            text: "Register"
            pos_hint: {"center_x": .5}
            on_press: root.register()


<LoginScreen>

    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .7

        MDLabel:
            text: "Welcome to Passbank"
            halign: "center"
            font_style: "Button"

        Widget:

        MDBoxLayout:
            adaptive_height: True

            MDTextField:
                id: login_pass_input
                hint_text: "Password"
                password: True
                helper_text: "Password not correct"
                helper_text_mode: "on_error"

            MDIconButton:
                id: login_show_password
                icon: "eye-outline"
                on_press: root.showPassword()

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": .5}
            on_press: root.login()


<CustomThreeLineIconListItem>
    IconLeftWidget:
        icon: root.icon

<MainScreen>

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: [0, 55, 0, 0]

        MDBoxLayout:
            size_hint_y: None
            height: self.minimum_height

            MDIconButton:
                icon: 'magnify'

            MDTextField:
                id: search_field
                hint_text: 'Search Account'
                on_text: root.setAccounts()

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                default_size: None, 250
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

    MDFloatingActionButtonSpeedDial:
        data: root.btn_data
        rotation_root_button: True
        callback: root.actionBtn

<ContentCustomBottomSheet>:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"

    MDToolbar:
        id: sheet_toolbar
        #title: "Edit"
        elevation: 10
        pos_hint: {"top": 1}
        right_action_items: [["trash-can-outline", lambda button: root.deleteAccountDialog()], ["eye-outline", lambda button: root.showPassword()], ["content-copy", lambda button: root.copyPassword()], ["content-save", lambda button: root.updateAccount()]]

    MDBoxLayout:
        adaptive_height: True
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint_x: .7

        MDTextField:
            id: sheet_site_input
            hint_text: "Site"
            #required: True
            #helper_text_mode: "on_error"

        MDTextField:
            id: sheet_email_input
            hint_text: "EMail"

        MDTextField:
            id: sheet_username_input
            hint_text: "Username"

        MDSeparator:

        MDBoxLayout:
            adaptive_height: True

            MDTextField:
                id: sheet_pass_input
                hint_text: "Password"
                password: True
                #helper_text: "Passwords not match"
                #helper_text_mode: "on_error"

            MDIconButton:
                id: sheet_show_password
                icon: "eye-outline"
                on_press: root.showNewPassword()

        MDTextField:
            id: sheet_confirm_pass_input
            hint_text: "New Password Confirm"
            password: True
            #helper_text: "Passwords not match"
            #helper_text_mode: "on_error"

        Widget:
            size_hint_y: None
            height: dp(40)


<AddAccountScreen>

    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .7

        MDLabel:
            text: "Add New Account"
            halign: "center"
            font_style: "Button"

        MDTextField:
            id: add_acc_site_input
            hint_text: "Site"
            #required: True
            #helper_text_mode: "on_error"

        MDTextField:
            id: add_acc_email_input
            hint_text: "EMail"

        MDTextField:
            id: add_acc_username_input
            hint_text: "Username"

        MDBoxLayout:
            adaptive_height: True

            MDTextField:
                id: add_acc_pass_input
                hint_text: "Password"
                password: True
                #required: True
                #helper_text_mode: "on_error"

            MDIconButton:
                id: add_acc_show_password
                icon: "eye-outline"
                on_press: root.showPassword()

        MDTextField:
            id: add_acc_conf_pass_input
            hint_text: "Confirm Password"
            password: True
            #required: True
            #helper_text_mode: "on_error"

        MDRaisedButton:
            text: "Add Account"
            pos_hint: {"center_x": .5}
            on_press: root.addAccount()

"""

Builder.load_string(kv_string)


def connectDatabase():
    con = sqlite3.connect("pass.db")
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS accounts (site TEXT, email TEXT, username TEXT, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS password (password TEXT)")

    return (con, cursor)

def getCipher():
    key = "F:NnQw}c(06BdclrX8_mJbGq]i#m5&hw"
    iv = "lA%u]-hF&GRx{P`s"
    cipher = AESCipher(key, iv)

    return cipher


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.current_screen.name == "add_account_screen":
                self.transition.direction = "right"
                self.current = "main_screen"
                return True # do not exit the app

            if self.current_screen.name == "register_screen":
                return False # exit the app from this page

            if self.current_screen.name == "login_screen":
                return False

            if self.current_screen.name == "main_screen":
                return False


class BaseScreen(Screen, MDApp):
    pass

class RegisterScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)

        self.sm = sm

        self.con, self.cursor = connectDatabase()

        self.cipher = getCipher()

    def register(self):
        password_field = self.ids.reg_pass_input
        confirm_password_field = self.ids.reg_confirm_pass_input

        if password_field.text == "":
            toast("Password required")

        elif password_field.text == confirm_password_field.text:
            encrypted = self.cipher.encrypt(password_field.text)

            self.cursor.execute("INSERT INTO password VALUES(?)",(encrypted,))
            self.con.commit()

            self.sm.current = "main_screen"

        else:
            toast("Passwords not match")

    def showPassword(self):
        button = self.ids.reg_show_password
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


class LoginScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)

        self.sm = sm

        self.con, self.cursor = connectDatabase()

        self.cipher = getCipher()

        # self.check_input_schedule = Clock.schedule_interval(self.checkInput, 0)

    def login(self):
        self.cursor.execute("SELECT password FROM password")
        encrypted = self.cursor.fetchall()[0][0]
        self.password = self.cipher.decrypt(encrypted)

        if self.password == self.ids.login_pass_input.text:
            self.ids.login_pass_input.error = False
            self.sm.current = "main_screen"

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
    def showPassword(self):
        button = self.ids.login_show_password
        input = self.ids.login_pass_input

        if button.icon == "eye-outline":
            input.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input.password = True
            button.icon = "eye-outline"


class CustomThreeLineIconListItem(ThreeLineIconListItem):
    icon = StringProperty()

class ContentCustomBottomSheet(MDBoxLayout):
    def __init__(self, site, email, username, **kwargs):
        super().__init__(**kwargs)

        self.con, self.cursor = connectDatabase()

        self.cipher = getCipher()

        if email == " ":
            email = ""

        if username == " ":
            username = ""

        self.site = site
        self.email = email
        self.username = username

        self.ids.sheet_toolbar.title = self.site
        self.ids.sheet_site_input.text = self.site
        self.ids.sheet_email_input.text = self.email
        self.ids.sheet_username_input.text = self.username

    def copyPassword(self):
        self.cursor.execute("SELECT password FROM accounts WHERE site=? AND email=?",(self.site, self.email,))
        encrypted = self.cursor.fetchall()[0][0]

        password = self.cipher.decrypt(encrypted)
        Clipboard.copy(password)

        toast(f"{self.site} password copied")

        #print(self.ids.keys())

    def updateAccount(self):
        new_site = self.ids.sheet_site_input.text
        new_email = self.ids.sheet_email_input.text
        new_username = self.ids.sheet_username_input.text

        new_password = self.ids.sheet_pass_input.text
        confirm_new_password = self.ids.sheet_confirm_pass_input.text

        ### Update Site
        if new_site == "":
            toast("Site is required")

        elif new_site == self.site:
            pass

        else:
            self.cursor.execute("UPDATE accounts SET site=? WHERE site=? AND email=?",(new_site, self.site, self.email))
            self.con.commit()

            self.site = new_site

            toast(f"{self.site} successfully changed")
        ###

        if not (new_email == self.email):
            self.cursor.execute("UPDATE accounts SET email=? WHERE site=? AND email=?",(new_email, self.site, self.email))
            self.con.commit()

            self.email = new_email

            toast("Email successfully changed")

        if not (new_username == self.username):
            self.cursor.execute("UPDATE accounts SET username=? WHERE site=? AND email=?",(new_username, self.site, self.email))
            self.con.commit()

            self.username = new_username

            toast("Username successfully changed")

        if not (new_password == ""):
            if new_password == confirm_new_password:
                encrypted = self.cipher.encrypt(new_password)

                self.cursor.execute("UPDATE accounts SET password=? WHERE site=? AND email=?",(encrypted, self.site, self.email))
                self.con.commit()

                toast("Password successfully changed")

            else:
                #self.ids.sheet_pass_input.error = True # Not working well
                #self.ids.sheet_confirm_pass_input.error = True
                toast("Passwords not match")

        main_screen.setAccounts() # refresh main screen

    def deleteAccountDialog(self):
        self.dialog = MDDialog(
            title=f"Delete {self.site}",
            size_hint=(0.8, 0.22),
            text=f"\nYou will delete [b]{self.site}[/b]. Are you sure?",
            buttons=[
                MDFlatButton(
                    text="Yes", on_press=self.deleteAccount
                ),
                MDFlatButton(
                    text="No", on_press=self.closeDialog
                )]
        )
        self.dialog.ids.text.text_color = ""
        self.dialog.open()

    def deleteAccount(self, button):
        self.cursor.execute("DELETE FROM accounts WHERE site=? AND email=?", (self.site, self.email))
        self.con.commit()

        toast(f"{self.site} successfully deleted")

        self.dialog.dismiss()
        main_screen.bottom_sheet.dismiss()

        main_screen.setAccounts() # refresh main screen

    def showPassword(self):
        self.cursor.execute("SELECT password FROM accounts WHERE site=? AND email=?",(self.site, self.email,))
        encrypted = self.cursor.fetchall()[0][0]

        password = self.cipher.decrypt(encrypted)

        self.dialog = MDDialog(
            title=f"{self.site} Password",
            size_hint=(0.8, 0.22),
            text=f"\n[b]{password}[/b]",
            buttons=[
                MDRaisedButton(text="Close", on_press=self.closeDialog)
            ]
        )
        self.dialog.ids.text.text_color = ""
        self.dialog.open()

    def closeDialog(self, button):
        self.dialog.dismiss()

    def showNewPassword(self):
        button = self.ids.sheet_show_password
        input_1 = self.ids.sheet_pass_input
        input_2 = self.ids.sheet_confirm_pass_input

        if button.icon == "eye-outline":
            input_1.password = False
            input_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            input_1.password = True
            input_2.password = True
            button.icon = "eye-outline"


class MainScreen(Screen):
    btn_data = {
            "key": "Suggest Password",
            'account-plus': 'Add Account',
            "clipboard": "Clear Clipboard"
    }

    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)

        self.sm = sm

        self.con, self.cursor = connectDatabase()

        self.cipher = getCipher()

        self.chars = string.ascii_letters + string.digits + string.punctuation

    def getAccounts(self):
        self.cursor.execute("SELECT site,email,username FROM accounts ORDER BY site COLLATE NOCASE ASC")
        self.accounts = self.cursor.fetchall()

    def setAccounts(self):
        self.getAccounts()

        search= False
        search_text = self.ids.search_field.text
        if search_text:
            search = True

        def addAccountsToRecycleView(site, email, username):
            # Set icon
            icon = "-".join(site.lower().split())

            if icon == "github":
                icon = "github-circle"

            if icon not in md_icons.keys():
                icon = ""
            ###

            # Set email and username
            if email == "":
                email = " "

            if username == "":
                username = " "
            ###

            self.ids.rv.data.append(
                {
                    "viewclass": "CustomThreeLineIconListItem",
                    "icon": icon,
                    "text": site,
                    "secondary_text": email,
                    "tertiary_text": username,
                    "on_press": lambda site=site, email=email, username=username: self.openBottomSheet(site, email, username),
                }
            )

        self.ids.rv.data = []
        for account in self.accounts:
            site = account[0]
            email = account[1]
            username = account[2]

            if search:
                if search_text.lower() in site.lower():
                    addAccountsToRecycleView(site, email, username)
            else:
                addAccountsToRecycleView(site, email, username)

    def actionBtn(self, button):
        if button.icon == "key":
            password = "".join([random.choice(self.chars) for i in range(0, 15)])
            Clipboard.copy(password)
            toast(f"{password} copied")

        if button.icon == "clipboard":
            Clipboard.copy(" ")
            toast("Clipboard Cleaned")

        if button.icon == "account-plus":
            self.sm.transition.direction = "left"
            self.sm.current = "add_account_screen"

    def openBottomSheet(self, site, email, username):
        self.bottom_sheet = MDCustomBottomSheet(screen=ContentCustomBottomSheet(site, email, username))
        self.bottom_sheet.open()


class AddAccountScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)

        self.sm = sm

        self.cipher = getCipher()

        self.conn, self.cursor = connectDatabase()

    def clearTextField(self, text_field):
        self.ids[text_field].focus = True
        self.ids[text_field].text = ""
        self.ids[text_field].focus = False

    def addAccount(self):
        site = self.ids.add_acc_site_input.text
        email = self.ids.add_acc_email_input.text
        username = self.ids.add_acc_username_input.text

        password = self.ids.add_acc_pass_input.text
        confirm_password = self.ids.add_acc_conf_pass_input.text

        if password == confirm_password:
            if site == "":
                toast("Site is required")
                return

            if password == "" or confirm_password == "":
                toast("Password is required")
                return

            encrypted = self.cipher.encrypt(password)

            self.cursor.execute("INSERT INTO accounts VALUES(?,?,?,?)",(site, email, username, encrypted))
            self.conn.commit()

            toast(f"{site} account added")

            self.sm.transition.direction = "right"
            self.sm.current = "main_screen"

            for text_field in self.ids.keys(): # clear text fields
                self.clearTextField(text_field)

            main_screen.setAccounts() # refresh main screen

        else:
            toast("Passwords not match")
            return

    def showPassword(self):
        button = self.ids.add_acc_show_password
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


sm = MyScreenManager(transition=NoTransition()) # FadeTransition removed because give error when on_pause method run

### Change Startup Screen
con, cursor = connectDatabase()
cipher = getCipher()

cursor.execute("SELECT password FROM password")
exists = cursor.fetchall()

if exists:
    login_screen = LoginScreen(name="login_screen", sm=sm)
    sm.add_widget(login_screen)
else:
    sm.add_widget(RegisterScreen(name="register_screen", sm=sm))

    login_screen = LoginScreen(name="login_screen", sm=sm) # for on_pause method
    sm.add_widget(login_screen)
###

main_screen = MainScreen(name="main_screen", sm=sm) # for refresh main screen
sm.add_widget(main_screen)
sm.add_widget(AddAccountScreen(name="add_account_screen", sm=sm))


class PassbankApp(MDApp):
    def on_pause(self):
        if sm.current == "main_screen":
            try:
                main_screen.bottom_sheet.dismiss()
                main_screen.bottom_sheet.screen.dialog.dismiss()
            except:
                pass

            login_screen.ids.login_show_password.icon = "eye-outline"
            login_screen.ids.login_pass_input.password = True

            login_screen.ids.login_pass_input.focus = True
            login_screen.ids.login_pass_input.text = ""
            login_screen.ids.login_pass_input.focus = False

            sm.current = "login_screen"

        else:
            pass

        return True

    def build(self):
        return sm

if __name__ == "__main__":
    PassbankApp().run()
