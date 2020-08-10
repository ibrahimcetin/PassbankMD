import os
import shutil
from functools import partial

from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from kivymd.uix.list import OneLineIconListItem, TwoLineListItem
from kivymd.toast import toast
from .filemanager import MDFileManager


class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()

class OptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

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


class DatabaseOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.manager = None

        self.initUI()

    def initUI(self):
        data = [("Backup Database", "Backup encrypted database"), ("Restore Database", "Restore encrypted database")]

        for text, second in data:
            self.ids.container.add_widget(TwoLineListItem(text=text, secondary_text=second, on_press=self.checkPlatform))

    def goBackBtn(self):
        self.manager.setOptionsScreen()

    def checkPlatform(self, button):
        if platform == "android":
            from android.permissions import check_permission, request_permissions, Permission

            if check_permission('android.permission.WRITE_EXTERNAL_STORAGE'):
                self.optionFunction(None, [True, True], button.text)
            else:
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], partial(self.optionFunction, text=button.text))

        else:
            self.optionFunction(None, [True, True], button.text)

    def optionFunction(self, permissions, grant_result, text):
        print("PERMISSIONS", permissions)
        print("GRANT_RESULT", grant_result)
        print("TEXT", text)

        if not grant_result == [True, True]:
            toast("Please, Allow Storage Permission")
            return

        if text == "Backup Database":
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.backup_select_path,
            )

            self.file_manager.show("/sdcard")
            self.manager.file_manager_open = True

        elif text == "Restore Database":
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.restore_select_path,
                ext=[".db"]
            )

            self.file_manager.show("/sdcard")
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

if __name__ == "__main__":
    from kivy.base import runTouchApp
    from kivy.lang import Builder

    Builder.load_file("../kv/options_screen.kv")
    runTouchApp(OptionsScreen())
