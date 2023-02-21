import os
import shutil
import string
import random
import sqlite3
from functools import partial

from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.core.clipboard import Clipboard

from kivymd.uix.list import (
    OneLineIconListItem,
    OneLineListItem,
    TwoLineListItem,
    OneLineAvatarIconListItem,
    ILeftBodyTouch,
    IRightBodyTouch,
)
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.theming import ThemeManager

from .utils import get_user_directory_path


class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()


class OptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.initUI()

    def initUI(self):
        data = [
            ("Appearance", "format-paint"),
            ("Database", "database"),
            ("Security", "security"),
            ("Password Suggestion", "key"),
            ("About", "information-outline"),
        ]

        for text, icon in data:
            self.ids.container.add_widget(
                CustomOneLineIconListItem(text=text, icon=icon, on_press=self.optionBtn)
            )

    def optionBtn(self, button):
        text = button.text

        if text == "Appearance":
            self.manager.setAppearanceOptionsScreen()

        elif text == "Database":
            self.manager.setDatabaseOptionsScreen()

        elif text == "Security":
            self.manager.setSecurityOptionsScreen()

        elif text == "Password Suggestion":
            self.manager.setPasswordSuggestionOptionsScreen()

        elif text == "About":
            toast("Created by Ibrahim Cetin")

    def goBackBtn(self):
        self.manager.setMainScreen()


class SortSelectionItem(OneLineAvatarIconListItem):
    divider = None

    screen = None

    def __init__(self, **kwargs):
        super().__init__()

        self.text = kwargs.get("text")
        self.ids.check.active = kwargs.get("active")


class LeftCheckbox(MDCheckbox, ILeftBodyTouch):
    pass


class SubtitlesSelectionItem(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        super().__init__()

        self.text = kwargs.get("text")
        self.ids.check.active = kwargs.get("active")


class AppearanceOptionsScreen(Screen):
    sort_options = {
        "a_to_z": "Alphabetically (A to Z)",
        "z_to_a": "Alphabetically (Z to A)",
        "first_to_last": "Date (First to Last)",
        "last_to_first": "Date (Last to First)",
    }

    dialog = None

    sort_by = None
    list_subtitles_options = None

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.theme_cls = ThemeManager()

        self.getOptions()
        self.setOptions()

    def getOptions(self):
        self.cursor.execute(
            "SELECT sort_by, list_subtitles, animation_options FROM options"
        )
        options = self.cursor.fetchall()[0]

        self.sort_by = options[0]
        self.list_subtitles_options = [bool(int(o)) for o in options[1].split(",")]
        self.animation_options = [bool(int(o)) for o in options[2].split(",")]

    def setOptions(self):
        self.ids.sort_by_item.secondary_text = self.sort_options.get(self.sort_by)

        self.setListSubtitlesText()

        self.ids.transition_animation_switch.active = self.animation_options[0]
        self.ids.bottomsheet_animation_switch.active = self.animation_options[1]

    def sortByButton(self):
        def is_current(code):
            return code == self.sort_by

        items = []
        SortSelectionItem.screen = self
        for code, text in self.sort_options.items():
            items.append(SortSelectionItem(text=text, active=is_current(code)))

        self.dialog = MDDialog(
            title="Sort By",
            type="confirmation",
            items=items,
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.closeDialog,
                ),
            ],
        )
        self.dialog.open()

    def setSortByOption(self, text):
        self.sort_by = list(self.sort_options.keys())[
            list(self.sort_options.values()).index(text)
        ]

        self.cursor.execute("UPDATE options SET sort_by = ?", (self.sort_by,))
        self.con.commit()

        self.ids.sort_by_item.secondary_text = text

        self.closeDialog()

    def listSubtitlesButton(self):
        self.dialog = MDDialog(
            title="List Subtitles",
            type="confirmation",
            items=[
                SubtitlesSelectionItem(
                    text="EMail", active=self.list_subtitles_options[0]
                ),
                SubtitlesSelectionItem(
                    text="Username", active=self.list_subtitles_options[1]
                ),
            ],
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.closeDialog,
                ),
                MDRaisedButton(text="Okay", on_press=self.getChecked),
            ],
        )
        self.dialog.open()

    def getChecked(self, button):
        self.list_subtitles_options = [
            item.ids.check.active for item in self.dialog.items
        ]
        new_status = ",".join([str(int(b)) for b in self.list_subtitles_options])

        self.cursor.execute("UPDATE options SET list_subtitles = ?", (new_status,))
        self.con.commit()

        self.setListSubtitlesText()
        self.closeDialog()

    def setListSubtitlesText(self):
        if all(self.list_subtitles_options):
            text = "EMail and Username"
        elif self.list_subtitles_options[0]:
            text = "EMail"
        elif self.list_subtitles_options[1]:
            text = "Username"
        else:
            text = "No"

        self.ids.list_subtitles_item.secondary_text = text

    def animationFunctions(self):
        options = []

        options.append("1" if self.ids.transition_animation_switch.active else "0")
        options.append("1" if self.ids.bottomsheet_animation_switch.active else "0")

        o = ",".join(options)
        self.cursor.execute("UPDATE options SET animation_options = ?", (o,))
        self.con.commit()

    def closeDialog(self, button=None):
        self.dialog.dismiss()

    def goBackBtn(self):
        self.manager.setOptionsScreen()


class TwoLineListItemWithContainer(TwoLineListItem):
    def start_ripple(self):  # disable ripple behavior
        pass


class RightSwitch(MDSwitch, IRightBodyTouch):
    pass


class RemoteDatabaseDialogContent(MDBoxLayout):
    pass


class DatabasePasswordDialogContent(MDBoxLayout):
    hint_text = StringProperty()

    def showPasswordButton(self, button, field):
        if button.icon == "eye-outline":
            field.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field.password = True
            button.icon = "eye-outline"


class DatabaseOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.getOptions()
        self.setOptions()
        self.initUI()

    def getOptions(self):
        self.cursor.execute(
            "SELECT auto_backup, auto_backup_location, remote_database, db_pass, db_user, db_name, db_port, db_host FROM options"
        )
        options = self.cursor.fetchall()[0]

        self.auto_backup = bool(options[0])
        self.auto_backup_location = (
            options[1] if os.path.isdir(options[1]) else get_user_directory_path()
        )
        self.remote_database = bool(options[2])

        self.pg_info = options[3:]

    def setOptions(self):
        self.ids.switch.active = self.auto_backup

        self.ids.location_list_item.secondary_text = self.auto_backup_location
        self.file_manager_start_path = self.auto_backup_location
        self.ids.remote_database_switch.active = self.remote_database

        if all(self.pg_info):
            for list_item, description in zip(
                self.ids.remote_database_list.children, self.pg_info
            ):
                list_item.secondary_text = (
                    description if list_item.text != "Password" else "**********"
                )

    def initUI(self):
        data = [
            ("Backup Database", "Backup encrypted database"),
            ("Restore Database", "Restore encrypted database"),
        ]
        for text, description in data:
            self.ids.database_container.add_widget(
                TwoLineListItem(
                    text=text, secondary_text=description, on_press=self.checkPlatform
                )
            )

    def checkPlatform(self, button):
        if platform == "android":
            from android.permissions import (
                check_permission,
                request_permissions,
                Permission,
            )

            if check_permission("android.permission.WRITE_EXTERNAL_STORAGE"):
                if isinstance(button, MDSwitch):
                    self.autoBackupFunction(active=button.active)
                else:
                    self.databaseFunctions(text=button.text)
            else:
                if isinstance(button, MDSwitch):
                    if button.active:  # request_permissions only run when switch active
                        request_permissions(
                            [
                                Permission.READ_EXTERNAL_STORAGE,
                                Permission.WRITE_EXTERNAL_STORAGE,
                            ],
                            partial(self.autoBackupFunction, active=button.active),
                        )
                else:
                    request_permissions(
                        [
                            Permission.READ_EXTERNAL_STORAGE,
                            Permission.WRITE_EXTERNAL_STORAGE,
                        ],
                        partial(self.databaseFunctions, text=button.text),
                    )

        else:
            if isinstance(button, MDSwitch):
                self.autoBackupFunction(active=button.active)
            else:
                self.databaseFunctions(text=button.text)

    def autoBackupFunction(
        self, permissions=None, grant_result=[True, True], active=False
    ):
        if not grant_result == [True, True]:
            self.auto_backup = 0
            self.ids.switch.active = False  # this line run switch's on_active method
            # that's why if request_permissions is not run only while switch is active,
            # request_permissions are run twice

            self.cursor.execute("UPDATE options SET auto_backup = 0")
            self.con.commit()

            toast("Please, Allow Storage Permission")
            return

        self.auto_backup = 1 if active else 0

        self.cursor.execute(
            "UPDATE options SET auto_backup = ?, auto_backup_location = ?",
            (self.auto_backup, self.auto_backup_location),
        )
        self.con.commit()

        if self.auto_backup == 1 and self.manager is not None:
            database_location = self.manager.getDatabaseLocation()
            shutil.copy2(database_location, self.auto_backup_location)

    def autoBackupLocationFunction(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.auto_backup_location_select_path,
            search="dirs",
        )

        self.file_manager.show(self.file_manager_start_path)
        self.manager.file_manager_open = True

    def auto_backup_location_select_path(self, path):
        if os.path.isdir(path):
            self.exit_manager()

            database_location = self.manager.getDatabaseLocation()
            shutil.copy2(database_location, path)

            self.cursor.execute("UPDATE options SET auto_backup_location = ?", (path,))
            self.con.commit()

            self.getOptions()
            self.setOptions()

        else:
            toast("Please Select a Directory")

    def databaseFunctions(self, permissions=None, grant_result=[True, True], text=None):
        if not grant_result == [True, True]:
            toast("Please, Allow Storage Permission")
            return

        if text == "Backup Database":
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.backup_select_path,
                search="dirs",
            )

            self.file_manager.show(self.file_manager_start_path)
            self.manager.file_manager_open = True

        elif text == "Restore Database":
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.restore_select_path,
                ext=[".db"],
            )

            self.file_manager.show(self.file_manager_start_path)
            self.manager.file_manager_open = True

    def backup_select_path(self, path):
        self.exit_manager()

        database_location = self.manager.getDatabaseLocation()
        shutil.copy2(database_location, path)

        toast("Database Backup was Successfully Created")

    def restore_select_path(self, path):
        self.openRestoreDatabaseDialog(path)

    def openRestoreDatabaseDialog(self, path):
        self.dialog = MDDialog(
            title="Password of the Database Backup",
            type="custom",
            content_cls=DatabasePasswordDialogContent(
                hint_text="Password of the Database Backup"
            ),
            buttons=[
                MDFlatButton(text="Cancel", on_press=self.dismiss_dialog),
                MDFlatButton(
                    text="Okay",
                    on_press=lambda x: self.checkBackupPassword(
                        self.dialog.content_cls.ids.password_field.text, path
                    ),
                ),
            ],
        )
        self.dialog.open()

    def checkBackupPassword(self, password, path):
        backup_con = sqlite3.connect(path)
        backup_cursor = backup_con.cursor()

        backup_cursor.execute("SELECT master_password, salt FROM options")
        encrypted, salt = map(bytes.fromhex, backup_cursor.fetchone())

        cipher = self.manager.createCipher(password, salt)

        try:
            result = cipher.decrypt(encrypted[:16], encrypted[16:], None)
            if result.decode() == password:
                restore = True
        except:
            restore = False

        if restore:
            self.exit_manager()
            self.dismiss_dialog()

            database_location = self.manager.getDatabaseLocation()
            shutil.copy2(path, database_location)

            self.manager.cipher = cipher
            self.getOptions()
            self.setOptions()

            toast("Database Successfully Restored")
        else:
            toast("Wrong Password")

    def remoteDatabaseSwitch(self, switch):
        self.cursor.execute(
            "UPDATE options SET remote_database = ?", (int(switch.active),)
        )
        self.con.commit()

    def remoteDatabaseDialog(self, list_item):
        content = RemoteDatabaseDialogContent()
        content.ids.text_field.hint_text = list_item.text

        self.dialog = MDDialog(
            title=f"{list_item.text}:",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_press=self.dismiss_dialog),
                MDRaisedButton(
                    text="Okay",
                    on_press=lambda btn: self.updateRemoteDatabaseOption(
                        list_item, content.ids.text_field.text
                    ),
                ),
            ],
        )
        self.dialog.open()

    def updateRemoteDatabaseOption(self, list_item, value):
        if value.isspace() or value == "":
            pass
        else:
            list_item.secondary_text = (
                value if list_item.text != "Password" else "**********"
            )

            text = list_item.text
            if text == "Database Name":
                variable_name = "db_name"
            elif text == "Password":
                variable_name = "db_pass"
            else:
                variable_name = f"db_{text.lower()}"

            query = f"UPDATE options SET {variable_name} = '{value}'"
            self.cursor.execute(query)
            self.con.commit()

        self.dialog.dismiss()

    def syncDatabaseButton(self):
        # TODO Fix freezes
        if self.manager.pg_con is None:
            self.cursor.execute(
                "SELECT remote_database, db_name, db_user, db_pass, db_host, db_port FROM options"
            )
            pg_data = self.cursor.fetchone()
            self.manager.connectRemoteDatabase(pg_data)
            # TODO Need to wait to connect database. Always say 'Something went wrong' on first click
        pg_con = self.manager.pg_con
        pg_cursor = self.manager.pg_cursor

        if pg_con is None:
            toast("Something went wrong")
            return

        pg_cursor.execute("SELECT * FROM accounts")
        remote_data = pg_cursor.fetchall()
        self.cursor.execute("SELECT * FROM accounts")
        local_data = self.cursor.fetchall()

        pg_cursor.execute("SELECT master_password, salt FROM options")
        remote_options = pg_cursor.fetchone()
        self.cursor.execute("SELECT master_password, salt FROM options")
        local_options = self.cursor.fetchone()

        if remote_data and local_data:
            toast("Please, Delete 'accounts' table in the PostgreSQL database")
            # TODO user can select remote or local database for sync

        elif local_data:

            def insert_data_to_remote_database():
                pg_cursor.execute("INSERT INTO options VALUES(%s, %s)", local_options)
                for account in local_data:
                    pg_cursor.execute(
                        "INSERT INTO accounts VALUES(%s, %s, %s, %s, %s, %s)", account
                    )
                pg_con.commit()

                toast("Sync Completed")

            toast("Please wait until Sync is Complete")
            Clock.schedule_once(lambda _: insert_data_to_remote_database())

        elif remote_data:

            def syncWithRemoteDatabase(password):
                encrypted, salt = map(bytes.fromhex, remote_options)
                cipher = self.manager.createCipher(password, salt)

                try:
                    result = cipher.decrypt(encrypted[:16], encrypted[16:], None)
                    if result.decode() == password:
                        sync = True
                except:
                    sync = False

                if sync:
                    dialog.dismiss()
                    toast("Please wait until Sync is Complete")

                    self.cursor.execute(
                        "UPDATE options SET master_password = ?, salt = ? WHERE master_password = ? AND salt = ?",
                        (*remote_options, *local_options),
                    )
                    for account in remote_data:
                        self.cursor.execute(
                            "INSERT INTO accounts VALUES(?,?,?,?,?,?)", account
                        )
                    self.con.commit()

                    self.manager.cipher = cipher

                    toast("Sync Completed")
                else:
                    toast("Wrong Password")

            dialog = MDDialog(
                title="Password of the Remote Backup",
                type="custom",
                content_cls=DatabasePasswordDialogContent(
                    hint_text="Password of the Remote Backup"
                ),
                buttons=[
                    MDFlatButton(text="Cancel", on_press=lambda x: dialog.dismiss()),
                    MDFlatButton(
                        text="Okay",
                        on_press=lambda x: syncWithRemoteDatabase(
                            dialog.content_cls.ids.password_field.text
                        ),
                    ),
                ],
            )
            dialog.open()

    def exit_manager(self, *args):
        self.file_manager.close()
        self.manager.file_manager_open = False

    def dismiss_dialog(self, btn=None):
        self.dialog.dismiss()

    def goBackBtn(self):
        self.manager.setOptionsScreen()


class OneLineListItemWithContainer(OneLineListItem):
    def start_ripple(self):  # disable ripple behavior
        pass


class SecurityOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.theme_cls = ThemeManager()

        self.getOptions()
        self.setOptions()

    def getOptions(self):
        self.cursor.execute("SELECT fast_login, auto_exit FROM options")
        options = self.cursor.fetchone()

        self.fast_login = bool(options[0])
        self.auto_exit = bool(options[1])

    def setOptions(self):
        self.ids.fast_login_switch.active = self.fast_login
        self.ids.auto_exit_switch.active = self.auto_exit

    def fastLoginFunction(self, active):
        status = 1 if active else 0

        self.cursor.execute("UPDATE options SET fast_login = ?", (status,))
        self.con.commit()

    def autoExitFunction(self, active):
        status = 1 if active else 0

        self.cursor.execute("UPDATE options SET auto_exit = ?", (status,))
        self.con.commit()

    def goBackBtn(self):
        self.manager.setOptionsScreen()


class ChangeMasterPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

        self.getOptions()

    def getOptions(self):
        self.cursor.execute("SELECT master_password, remote_database FROM options")
        data = self.cursor.fetchone()

        encrypted = bytes.fromhex(data[0])
        self.password = self.cipher.decrypt(
            encrypted[:16], encrypted[16:], None
        ).decode()

        self.remote_database = data[1]

    def initCipher(self, password):
        salt = os.urandom(32)
        cipher = self.manager.createCipher(password, salt)

        nonce = os.urandom(16)
        encrypted = nonce + cipher.encrypt(nonce, password.encode(), None)

        return encrypted, salt

    def recryptPasswords(self):
        old_cipher = self.cipher
        new_cipher = self.manager.cipher

        self.cursor.execute("SELECT id, password FROM accounts")
        accounts = self.cursor.fetchall()

        for account in accounts:
            old_encrypted = bytes.fromhex(account[1])
            password = old_cipher.decrypt(
                old_encrypted[:16], old_encrypted[16:], None
            ).decode()

            nonce = os.urandom(16)
            new_encrypted = nonce + new_cipher.encrypt(nonce, password.encode(), None)

            self.cursor.execute(
                "UPDATE accounts SET password = ? WHERE id = ?",
                (new_encrypted.hex(), account[0]),
            )
        self.con.commit()

        self.cipher = new_cipher

    def updateButton(self, current_password, new_password, confirm_new_password):
        if current_password == self.password:
            if self.password == new_password == confirm_new_password:
                toast("Current password and new password cannot be same!")

            elif new_password == confirm_new_password:
                encrypted, salt = self.initCipher(new_password)

                self.cursor.execute(
                    "UPDATE options SET master_password = ?, salt = ?",
                    (encrypted.hex(), salt.hex()),
                )
                self.con.commit()

                self.manager.createCipher(new_password, salt)
                self.recryptPasswords()

                self.manager.setSecurityOptionsScreen()
                toast("Master Password Successfully Changed")

                if self.remote_database:
                    query = "UPDATE options SET master_password = {}, salt = {}".format(
                        repr(encrypted.hex), repr(salt.hex())
                    )
                    self.manager.runRemoteDatabaseQuery(query)

            else:
                instance = self.ids.confirm_new_password_field
                self.initFieldError(instance)

        else:
            instance = self.ids.current_password_field
            self.initFieldError(instance)

    def showPasswordBtn(self):
        button = self.ids.show_password_button
        field_1 = self.ids.current_password_field
        field_2 = self.ids.new_password_field
        field_3 = self.ids.confirm_new_password_field

        if button.icon == "eye-outline":
            field_1.password = False
            field_2.password = False
            field_3.password = False
            button.icon = "eye-off-outline"

        elif button.icon == "eye-off-outline":
            field_1.password = True
            field_2.password = True
            field_3.password = True
            button.icon = "eye-outline"

    def checkField(self, instance, text):
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

    def goBackBtn(self):
        self.manager.setSecurityOptionsScreen()

    def initFieldError(self, instance):
        instance.error = True

    def closeFieldError(self, instance):
        instance.error = False


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class PasswordSuggestionOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.getOptions()
        self.setOptions()

    def getOptions(self):
        self.cursor.execute(
            "SELECT password_length, password_suggestion_options FROM options"
        )
        options = self.cursor.fetchone()

        self.password_length = options[0]
        self.password_suggestion_options = [bool(int(o)) for o in options[1].split(",")]

    def setOptions(self):
        self.ids.slider.value = self.password_length

        self.ids.lowercase_checkbox.active = self.password_suggestion_options[0]
        self.ids.uppercase_checkbox.active = self.password_suggestion_options[1]
        self.ids.digits_checkbox.active = self.password_suggestion_options[2]
        self.ids.symbols_checkbox.active = self.password_suggestion_options[3]

    def sliderFunction(self, slider):
        value = int(slider.value)

        if value != self.password_length:
            self.password_length = value
            self.cursor.execute("UPDATE options SET password_length = ?", (value,))
            self.con.commit()

    def checkboxFunction(self, checkbox):
        checkbox_status = []

        for widget in self.ids.values():
            if isinstance(widget, RightCheckbox):
                checkbox_status.append(widget.active)

        if any(checkbox_status):
            options = ",".join([str(int(i)) for i in checkbox_status])

            self.cursor.execute(
                "UPDATE options SET password_suggestion_options = ?", (options,)
            )
            self.con.commit()

        else:
            checkbox.active = True
            toast("You must choose at least one!")

    def suggestPasswordButton(self):
        self.getOptions()
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

    def goBackBtn(self):
        self.manager.setOptionsScreen()
