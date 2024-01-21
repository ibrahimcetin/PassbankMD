from kivy.lang import Builder
from kivy.uix.screenmanager import FadeTransition, NoTransition

from kivymd.app import MDApp

from libs.baseclass.manager import Manager
from libs.baseclass.utils import find_bundle_dir


working_dir = find_bundle_dir(__file__)

kv_dir = working_dir / "libs" / "kv"
kv_files = kv_dir.iterdir()
for kv_file in kv_files:
    Builder.load_file(kv_file.as_posix())


class Passbank(MDApp):
    manager = None

    transition_animation = None
    auto_exit = None

    def build(self):
        self.icon = "data/icon.png"

        self.manager = Manager(
            transition=FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark)
        )

        return self.manager

    def on_stop(self):
        self.manager.con.close()
        if self.manager.pg_con is not None:
            self.manager.pg_con.close()

    def on_pause(self):
        self.getOptions()

        if self.auto_exit:
            if self.transition_animation:
                self.manager.transition = NoTransition()

            try:
                self.manager.main_screen.bottom_sheet.dismiss()
                self.manager.main_screen.bottom_sheet.screen.dialog.dismiss()
            except:
                pass

        return True

    def on_resume(self):
        # I used on_resume method instead of on_pause method when change screen to login screen
        # beacuse on_pause method not working well.

        if self.auto_exit:
            try:
                if self.manager.current_screen.name == "main_screen":
                    self.manager.setLoginScreen()
            except:
                pass

            if self.transition_animation:
                self.manager.transition = FadeTransition(
                    duration=0.2, clearcolor=self.theme_cls.bg_dark
                )

    def getOptions(self):
        self.manager.cursor.execute("SELECT animation_options, auto_exit FROM options")
        options = self.manager.cursor.fetchone()

        self.transition_animation = bool(int(options[0][0]))
        self.auto_exit = bool(options[1])


if __name__ == "__main__":
    Passbank().run()
