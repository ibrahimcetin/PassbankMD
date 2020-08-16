import os
import shutil
from functools import partial

from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.animation import Animation

from kivymd.uix.list import OneLineIconListItem, OneLineListItem, TwoLineListItem, OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch, ContainerSupport
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from .filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.theming import ThemeManager


class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()

class OptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.initUI()

    def initUI(self):
        data = [("Appearance", "format-paint"), ("Database", "database"), ("Security", "security"), ("About", "information-outline")]

        for text, icon in data:
            self.ids.container.add_widget(CustomOneLineIconListItem(text=text, icon=icon, on_press=self.optionBtn))

    def optionBtn(self, button):
        text = button.text

        if text == "Appearance":
            self.manager.setAppearanceOptionsScreen()

        elif text == "Database":
            self.manager.setDatabaseOptionsScreen()

        elif text == "Security":
            self.manager.setSecurityOptionsScreen()

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
    sort_options = {"a_to_z": "Alphabetically (A to Z)",
                    "z_to_a": "Alphabetically (Z to A)",
                    "first_to_last": "Date (First to Last)",
                    "last_to_first": "Date (Last to First)"}

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.theme_cls = ThemeManager()

        self.getOptions()

    def getOptions(self):
        self.cursor.execute("SELECT sort_by, list_subtitles FROM options")
        options = self.cursor.fetchall()[0]

        self.sort_by = options[0]
        self.ids.sort_by_item.secondary_text = self.sort_options.get(self.sort_by)

        self.list_subtitles_options = [bool(int(o)) for o in options[1].split(",")]
        self.setListSubtitlesText()

    def sortByButton(self):
        def is_current(code):
            return (code == self.sort_by)

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
                    text="Cancel", text_color=self.theme_cls.primary_color, on_press=self.closeDialog
                ),
            ],
        )
        self.dialog.open()

    def setSortByOption(self, text):
        self.sort_by = list(self.sort_options.keys())[list(self.sort_options.values()).index(text)]

        self.cursor.execute("UPDATE options SET sort_by = ?", (self.sort_by,))
        self.con.commit()

        self.ids.sort_by_item.secondary_text = text

        self.closeDialog()

    def listSubtitlesButton(self):
        self.dialog = MDDialog(
            title="List Subtitles",
            type="confirmation",
            items=[
                SubtitlesSelectionItem(text="EMail", active=self.list_subtitles_options[0]),
                SubtitlesSelectionItem(text="Username", active=self.list_subtitles_options[1])
            ],
            buttons=[
                MDFlatButton(
                    text="Cancel", text_color=self.theme_cls.primary_color, on_press=self.closeDialog
                ),
                MDRaisedButton(
                    text="Ok", on_press=self.getChecked
                ),
            ],
        )
        self.dialog.open()

    def getChecked(self, button):
        self.list_subtitles_options = [item.ids.check.active for item in self.dialog.items]
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

    def closeDialog(self, button=None):
        self.dialog.dismiss()

    def goBackBtn(self):
        self.manager.setOptionsScreen()


class TwoLineListItemWithContainer(ContainerSupport, TwoLineListItem):
    def start_ripple(self): # disable ripple behavior
        pass

class RightSwitch(MDSwitch, IRightBodyTouch):
    pass

class DatabaseOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")

        self.file_manager_start_path = os.getenv("EXTERNAL_STORAGE") if platform == "android" else os.path.expanduser("~")

        self.getOptions()
        self.setOptions()
        self.initUI()

    def getOptions(self):
        self.cursor.execute("SELECT auto_backup, auto_backup_location FROM options")
        options = self.cursor.fetchall()[0]

        self.auto_backup = options[0]
        self.auto_backup_location = options[1]

    def setOptions(self):
        self.ids.switch.active = self.auto_backup
        self.ids.location_list_item.secondary_text = self.auto_backup_location

    def initUI(self):
        data = [("Backup Database", "Backup encrypted database"), ("Restore Database", "Restore encrypted database")]

        for text, second in data:
            self.ids.database_container.add_widget(TwoLineListItem(text=text, secondary_text=second, on_press=self.checkPlatform))

    def checkPlatform(self, button):
        if platform == "android":
            from android.permissions import check_permission, request_permissions, Permission

            if check_permission('android.permission.WRITE_EXTERNAL_STORAGE'):
                if isinstance(button, MDSwitch):
                    self.autoBackupFunction(active=button.active)
                else:
                    self.databaseFunctions(text=button.text)
            else:
                if isinstance(button, MDSwitch):
                    if button.active: # request_permissions only run when switch active
                        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], partial(self.autoBackupFunction, active=button.active))
                else:
                    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], partial(self.databaseFunctions, text=button.text))

        else:
            if isinstance(button, MDSwitch):
                self.autoBackupFunction(active=button.active)
            else:
                self.databaseFunctions(text=button.text)

    def autoBackupFunction(self, permissions=None, grant_result=[True, True], active=False):
        if not grant_result == [True, True]:
            self.auto_backup = 0
            self.ids.switch.active = False # this line run switch's on_active method
                                           # that's why if request_permissions is not run only while switch is active,
                                           # request_permissions are run twice

            self.cursor.execute("UPDATE options SET auto_backup = 0")
            self.con.commit()

            toast("Please, Allow Storage Permission")
            return

        status = 1 if active else 0

        self.cursor.execute("UPDATE options SET auto_backup = ?", (status,))
        self.con.commit()

        if status == 1:
            shutil.copy2("pass.db", self.auto_backup_location)

    def autoBackupLocationFunction(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.auto_backup_location_select_path,
        )

        self.file_manager.show(self.file_manager_start_path)
        self.manager.file_manager_open = True

    def auto_backup_location_select_path(self, path):
        if os.path.isdir(path):
            self.exit_manager()

            shutil.copy2("pass.db", path)

            self.cursor.execute("UPDATE options SET auto_backup_location = ?", (path,))
            self.con.commit()

            self.auto_backup_location = path
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
            )

            self.file_manager.show(self.file_manager_start_path)
            self.manager.file_manager_open = True

        elif text == "Restore Database":
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.restore_select_path,
                ext=[".db"]
            )

            self.file_manager.show(self.file_manager_start_path)
            self.manager.file_manager_open = True

    def backup_select_path(self, path):
        if os.path.isdir(path):
            self.exit_manager()

            shutil.copy2("pass.db", path)
            toast("Database Successfully Backed Up")
        else:
            toast("Please Select a Directory")

    def restore_select_path(self, path):
        if os.path.isfile(path):
            self.exit_manager()

            shutil.copy2(path, "pass.db")
            toast("Database Successfully Restored")
        else:
            toast("Please Select a Database")

    def exit_manager(self, *args):
        self.file_manager.close()
        self.manager.file_manager_open = False

    def goBackBtn(self):
        self.manager.setOptionsScreen()


class OneLineListItemWithContainer(ContainerSupport, OneLineListItem):
    def start_ripple(self): # disable ripple behavior
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

    def changeMasterPasswordButton(self):
        self.dialog = MDDialog(
            title="Change Master Password?",
            text="By changing the master password you will not be able to restore database backups that were created with the current password.",
            buttons=[
                MDFlatButton(
                    text="Cancel", text_color=self.theme_cls.primary_color, on_press=self.closeDialog
                ),
                MDFlatButton(
                    text="Accept", text_color=self.theme_cls.primary_color, on_press=self.changeMasterPasswordFunction
                ),
            ],
        )
        self.dialog.ids.text.text_color = [0,0,0]
        self.dialog.open()

    def changeMasterPasswordFunction(self, button):
        self.manager.setChangeMasterPasswordScreen()
        self.closeDialog(None)

    def fastLoginFunction(self, active):
        status = 1 if active else 0

        self.cursor.execute("UPDATE options SET fast_login = ?", (status,))
        self.con.commit()

    def autoExitFunction(self, active):
        status = 1 if active else 0

        self.cursor.execute("UPDATE options SET auto_exit = ?", (status,))
        self.con.commit()

    def closeDialog(self, button):
        self.dialog.dismiss()

    def goBackBtn(self):
        self.manager.setOptionsScreen()

class ChangeMasterPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get("name"))

        self.con = kwargs.get("con")
        self.cursor = kwargs.get("cursor")
        self.cipher = kwargs.get("cipher")

        self.password = None
        self.getPasswordFromDB()

    def getPasswordFromDB(self):
        self.cursor.execute("SELECT master_password FROM options")
        encrypted = self.cursor.fetchone()[0]

        self.password = self.cipher.decrypt(encrypted)

    def updateButton(self, current_password, new_password, confirm_new_password):
        if current_password == self.password:
            if self.password == new_password == confirm_new_password:
                toast("Current password and new password cannot be same!")

            elif new_password == confirm_new_password:
                encrypted = self.cipher.encrypt(new_password)

                self.cursor.execute("UPDATE options SET master_password = ?", (encrypted,))
                self.con.commit()

                toast("Master Password Successfully Changed")
                self.manager.setSecurityOptionsScreen()

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
