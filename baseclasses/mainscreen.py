import string
import random
import shutil

from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.animation import Animation

from kivymd.uix.list import OneLineIconListItem, TwoLineIconListItem, ThreeLineIconListItem
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast


class RVOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()

class RVTwoLineIconListItem(TwoLineIconListItem):
    icon = StringProperty()

class RVThreeLineIconListItem(ThreeLineIconListItem):
    icon = StringProperty()


class MyMDCustomBottomSheet(MDCustomBottomSheet):
    def on_open(self):
        Window.softinput_mode = "pan"

        return super().on_open()

    def on_pre_dismiss(self):
        if self.animation:
            Animation(height=0, d=self.duration_opening).start(self.layout)
            Animation(height=0, d=self.duration_opening).start(self.content)

    def on_dismiss(self):
        Window.softinput_mode = ""

        return super().on_dismiss()

    def resize_content_layout(self, content, layout, interval=0):
        height = layout.height

        if self.animation:
            self.content = content
            self.layout = layout

            Animation(height=height, d=self.duration_opening).start(self.layout)
            Animation(height=height, d=self.duration_opening).start(self.content)
        else:
            # For a reason I don't understand, bottom sheet height is short.
            # I will try to fix this problem.
            layout.height = height
            content.height = height


class ContentCustomBottomSheet(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__()

        self.main_screen = kwargs.get("main_screen") # for refresh screen after account delete or update

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

        self.site = kwargs.get("site")
        self.email = kwargs.get("email")
        self.username = kwargs.get("username")

        if self.email == " ":
            self.email = ""

        if self.username == " ":
            self.username = ""

        self.ids.toolbar.title = self.site
        self.ids.site_field.text = self.site
        self.ids.email_field.text = self.email
        self.ids.username_field.text = self.username

        self.auto_backup = kwargs.get("auto_backup")
        self.auto_backup_location = kwargs.get("auto_backup_location")

    def copyPassword(self):
        self.cursor.execute("SELECT password FROM accounts WHERE site=? AND email=?",(self.site, self.email,))
        encrypted = self.cursor.fetchall()[0][0]

        password = self.cipher.decrypt(encrypted)
        Clipboard.copy(password)

        toast(f"{self.site} Password Copied")

    def updateAccount(self, site_field, confirm_new_password_field):
        new_site = site_field.text
        new_email = self.ids.email_field.text
        new_username = self.ids.username_field.text

        new_password = self.ids.new_password_field.text
        confirm_new_password = confirm_new_password_field.text

        changed = []

        ### Update Site
        if not new_site:
            self.initFieldError(site_field)

        elif new_site == self.site:
            pass

        else:
            self.cursor.execute("UPDATE accounts SET site=? WHERE site=? AND email=?",(new_site, self.site, self.email))
            self.con.commit()

            self.site = new_site

            changed.append("Site")
        ###

        if not (new_email == self.email):
            self.cursor.execute("UPDATE accounts SET email=? WHERE site=? AND email=?",(new_email, self.site, self.email))
            self.con.commit()

            self.email = new_email

            changed.append("Email")

        if not (new_username == self.username):
            self.cursor.execute("UPDATE accounts SET username=? WHERE site=? AND email=?",(new_username, self.site, self.email))
            self.con.commit()

            self.username = new_username

            changed.append("Username")

        if new_password:
            if new_password == confirm_new_password:
                encrypted = self.cipher.encrypt(new_password)

                self.cursor.execute("UPDATE accounts SET password=? WHERE site=? AND email=?",(encrypted, self.site, self.email))
                self.con.commit()

                #TODO clear new password fields after password changed

                changed.append("Password")

            else:
                self.initFieldError(confirm_new_password_field)

        if len(changed) > 0:
            output = ", ".join(changed)
            toast(f"{output} Successfully Changed")

        if self.auto_backup and len(changed) > 0: # auto backup
            shutil.copy2("pass.db", self.auto_backup_location)

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
        self.dialog.ids.text.text_color = [0,0,0]
        self.dialog.open()

    def deleteAccount(self, button):
        self.cursor.execute("DELETE FROM accounts WHERE site=? AND email=?", (self.site, self.email))
        self.con.commit()

        toast(f"{self.site} Successfully Deleted")

        self.dialog.dismiss()
        self.main_screen.bottom_sheet.dismiss()

        if self.auto_backup:
            shutil.copy2("pass.db", self.auto_backup_location)

        self.main_screen.initUI() # refresh main screen

    def showPassword(self):
        self.cursor.execute("SELECT password FROM accounts WHERE site=? AND email=?",(self.site, self.email,))
        encrypted = self.cursor.fetchall()[0][0]

        password = self.cipher.decrypt(encrypted)

        self.dialog = MDDialog(
            title=f"{self.site} Password",
            size_hint=(0.8, 0.22),
            text=f"\n[font=fonts/JetBrainsMono-Bold.ttf]{password}[/font]",
            buttons=[
                MDRaisedButton(text="Close", on_press=self.closeDialog)
            ]
        )
        self.dialog.ids.text.text_color = [0,0,0]
        self.dialog.open()

    def showNewPasswordButton(self, button, field_1, field_2):
        if button.icon == "eye-outline":
            field_1.password = False
            field_2.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field_1.password = True
            field_2.password = True
            button.icon = "eye-outline"

    def checkSiteField(self, instance, text):
        if not text:
            return

        else:
            self.closeFieldError(instance)

    def checkConfirmField(self, instance, text):
        if not text:
            return

        if text != self.ids.new_password_field.text:
            self.initFieldError(instance)

        else:
            self.closeFieldError(instance)

    def closeDialog(self, button):
        self.dialog.dismiss()

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
    button_data = {
            "key": "Suggest Password",
            'account-plus': 'Add Account',
            "clipboard": "Clear Clipboard"
    }

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

        self.initUI()

    def getOptions(self):
        self.cursor.execute("SELECT sort_by, list_subtitles, animation_options, auto_backup, auto_backup_location, password_length, password_suggestion_options FROM options")
        options = self.cursor.fetchall()[0]

        self.sort_by = options[0]
        self.list_subtitles_options = [bool(int(o)) for o in options[1].split(",")]
        self.bottomsheet_animation = bool(int(options[2][2]))

        self.auto_backup = True if options[3] == 1 else False
        self.auto_backup_location = options[4]

        self.password_length = options[5]
        self.password_suggestion_options = [bool(int(o)) for o in options[6].split(',')]

    def getAccounts(self):
        if self.sort_by == "a_to_z":
            option = "ORDER BY site COLLATE NOCASE ASC"
        elif self.sort_by == "z_to_a":
            option = "ORDER BY site COLLATE NOCASE DESC"
        else:
            option = ""

        self.cursor.execute(f"SELECT site,email,username FROM accounts {option}")
        self.accounts = self.cursor.fetchall()

        if self.sort_by == "last_to_first":
            self.accounts.reverse()

    def initUI(self):
        self.getOptions()
        self.getAccounts()

        search = False
        search_text = self.ids.search_field.text
        if search_text:
            search = True

        def add_accounts_to_recycle_view(site, email, username):
            # Set icon
            icon = "-".join(site.lower().split())

            if icon not in md_icons.keys():
                icon = "account-circle-outline"
            ###

            # Set email and username
            if email == "":
                email = " "

            if username == "":
                username = " "
            ###

            # Set options
            base = {
                    "icon": icon,
                    "text": site,
                    "on_press": lambda site=site, email=email, username=username: self.openBottomSheet(site, email, username),
                    }

            if all(self.list_subtitles_options):
                base["viewclass"] = "RVThreeLineIconListItem"
                base["secondary_text"] = email
                base["tertiary_text"] = username

            elif self.list_subtitles_options[0]:
                base["viewclass"] = "RVTwoLineIconListItem"
                base["secondary_text"] = email

            elif self.list_subtitles_options[1]:
                base["viewclass"] = "RVTwoLineIconListItem"
                base["secondary_text"] = username

            else:
                base["viewclass"] = "RVOneLineIconListItem"
            ###

            self.ids.recycle_view.data.append(
                base
            )

        self.ids.recycle_view.data = []
        for account in self.accounts:
            site = account[0]
            email = account[1]
            username = account[2]

            if search:
                if search_text.lower() in site.lower():
                    add_accounts_to_recycle_view(site, email, username)
            else:
                add_accounts_to_recycle_view(site, email, username)

    def actionButton(self, button):
        if button.icon == "key":
            options = self.password_suggestion_options

            chars = ""

            if options[0]:
                chars += string.ascii_lowercase
            if options[1]:
                chars += string.ascii_uppercase
            if options[2]:
                chars += string.digits
            if options[3]:
                chars += string.punctuation

            password = "".join(random.choices(chars, k=self.password_length))
            Clipboard.copy(password)
            toast(f"{password} Copied")

        if button.icon == "clipboard":
            Clipboard.copy(" ")
            toast("Clipboard Cleaned")

        if button.icon == "account-plus":
            self.manager.setAddAccountScreen()

    def openBottomSheet(self, site, email, username):
        self.bottom_sheet = MyMDCustomBottomSheet(screen=ContentCustomBottomSheet(main_screen=self, con=self.con, cursor=self.cursor, cipher=self.cipher, site=site, email=email, username=username, auto_backup=self.auto_backup, auto_backup_location=self.auto_backup_location), animation=self.bottomsheet_animation, duration_opening=0.1)
        self.bottom_sheet.open()

