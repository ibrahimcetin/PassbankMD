import os
import shutil
from functools import partial

from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from kivymd.uix.list import OneLineIconListItem, TwoLineListItem, OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch, ContainerSupport
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from .filemanager import MDFileManager
from kivymd.toast import toast



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

    def goBackBtn(self):
        self.manager.setMainScreen()

    def optionBtn(self, button):
        text = button.text

        if text == "Appearance":
            self.manager.setAppearanceOptionsScreen()

        elif text == "Database":
            self.manager.setDatabaseOptionsScreen()


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
                    text="Cancel", on_press=self.closeDialog
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
                    text="Cancel", on_press=self.closeDialog
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

    def goBackBtn(self):
        self.manager.setOptionsScreen()

    def closeDialog(self, button=None):
        self.dialog.dismiss()


class TwoLineListItemWithSwitch(ContainerSupport, TwoLineListItem):
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
        self.initUI()

    def getOptions(self):
        self.cursor.execute("SELECT auto_backup, auto_backup_location FROM options")
        options = self.cursor.fetchall()[0]

        self.ids.switch.active = options[0]
        self.ids.location_list_item.secondary_text = options[1]

    def initUI(self):
        data = [("Backup Database", "Backup encrypted database"), ("Restore Database", "Restore encrypted database")]

        for text, second in data:
            self.ids.database_container.add_widget(TwoLineListItem(text=text, secondary_text=second, on_press=self.checkPlatform))

    def goBackBtn(self):
        self.manager.setOptionsScreen()

    def checkPlatform(self, button):
        if platform == "android":
            from android.permissions import check_permission, request_permissions, Permission

            if check_permission('android.permission.WRITE_EXTERNAL_STORAGE'):
                if isinstance(button, MDSwitch):
                    self.autoBackupFunction(active=button.active)
                else:
                    self.databaseFunctions(button.text)
            else:
                if isinstance(button, MDSwitch):
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
            toast("Please, Allow Storage Permission")
            return

        if active:
            new_status = 0 # False
        else:
            new_status = 1 # True

        self.cursor.execute("UPDATE options SET auto_backup = ?", (new_status,))
        self.con.commit()

        if new_status == 1:
            path = self.ids.location_list_item.secondary_text
            shutil.copy2("pass.db", path)

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

            self.ids.location_list_item.secondary_text = path

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
