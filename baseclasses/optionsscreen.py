import os
import shutil
from functools import partial

from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from kivymd.uix.list import OneLineIconListItem, TwoLineListItem, IRightBodyTouch, ContainerSupport
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.toast import toast
from .filemanager import MDFileManager


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

        if text == "Database":
            self.manager.setDatabaseOptionsScreen()


class CustomTwoLineListItem(ContainerSupport, TwoLineListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        self.setOptions()
        self.initUI()

    def setOptions(self):
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
                    self.autoBackupFunction(None, [True, True], button.active)
                else:
                    self.databaseFunctions(None, [True, True], button.text)
            else:
                if isinstance(button, MDSwitch):
                    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], partial(self.autoBackupFunction, active=button.active))
                else:
                    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], partial(self.databaseFunctions, text=button.text))

        else:
            if isinstance(button, MDSwitch):
                self.autoBackupFunction(None, [True, True], button.active)
            else:
                self.databaseFunctions(None, [True, True], button.text)

    def autoBackupFunction(self, permissions, grant_result, active):
        if not grant_result == [True, True]:
            toast("Please, Allow Storage Permission")
            return

        if active:
            new_status = 0 # False
        else:
            new_status = 1 # True

        self.cursor.execute("UPDATE options SET auto_backup = ?", (new_status,))
        self.con.commit()

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

    def databaseFunctions(self, permissions, grant_result, text):
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
