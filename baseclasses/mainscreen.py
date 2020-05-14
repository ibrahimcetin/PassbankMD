from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty
from kivy.animation import Animation

from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast

import string
import random


class CustomThreeLineIconListItem(ThreeLineIconListItem):
    icon = StringProperty()


class ContentCustomBottomSheet(MDBoxLayout):
    def __init__(self, main_screen, con, cursor, cipher, site, email, username, **kwargs):
        super().__init__(**kwargs)

        self.main_screen = main_screen # for refresh screen after account delete or update

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

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
        if not new_site:
            instance = self.ids.sheet_site_input
            self.initFieldError(instance)

        elif new_site == self.site:
            pass

        else:
            self.cursor.execute("UPDATE accounts SET site=? WHERE site=? AND email=?",(new_site, self.site, self.email))
            self.con.commit()

            self.site = new_site

            toast(f"{self.site} Successfully Changed")
        ###

        if not (new_email == self.email):
            self.cursor.execute("UPDATE accounts SET email=? WHERE site=? AND email=?",(new_email, self.site, self.email))
            self.con.commit()

            self.email = new_email

            toast("Email Successfully Changed")

        if not (new_username == self.username):
            self.cursor.execute("UPDATE accounts SET username=? WHERE site=? AND email=?",(new_username, self.site, self.email))
            self.con.commit()

            self.username = new_username

            toast("Username Successfully Changed")

        if new_password:
            if new_password == confirm_new_password:
                encrypted = self.cipher.encrypt(new_password)

                self.cursor.execute("UPDATE accounts SET password=? WHERE site=? AND email=?",(encrypted, self.site, self.email))
                self.con.commit()

                toast("Password Successfully Changed")

            else:
                instance = self.ids.sheet_confirm_pass_input
                self.initFieldError(instance)

        else:
            pass

        self.main_screen.initUI() # refresh main screen

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
        self.main_screen.bottom_sheet.dismiss()

        self.main_screen.initUI() # refresh main screen

    def showPasswordBtn(self):
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

    def showNewPasswordBtn(self):
        button = self.ids.sheet_show_new_password_btn
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

    def checkSiteField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkConfirmField(self, instance, text):
        if not text:
            return

        if text != self.ids.sheet_pass_input.text:
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


class MainScreen(Screen):
    btn_data = {
            "key": "Suggest Password",
            'account-plus': 'Add Account',
            "clipboard": "Clear Clipboard"
    }

    def __init__(self, con, cursor, cipher, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.con = con
        self.cursor = cursor

        self.cipher = cipher

        self.chars = string.ascii_letters + string.digits + string.punctuation

    def getAccounts(self):
        self.cursor.execute("SELECT site,email,username FROM accounts ORDER BY site COLLATE NOCASE ASC")
        self.accounts = self.cursor.fetchall()

    def initUI(self):
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
            self.manager.setAddAccountScreen()

    def openBottomSheet(self, site, email, username):
        self.bottom_sheet = MDCustomBottomSheet(screen=ContentCustomBottomSheet(self, self.con, self.cursor, self.cipher, site, email, username))
        self.bottom_sheet.open()
