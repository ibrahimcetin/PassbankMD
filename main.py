from kivy.uix.screenmanager import FadeTransition, NoTransition

from kivymd.app import MDApp

from baseclasses.manager import Manager


class Passbank(MDApp):
    def build(self):
        self.manager = Manager(transition=FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark))

        return self.manager

    """
    def on_start(self):
        self.fps_monitor_start()
    """

    def on_pause(self):
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

        try:
            if self.manager.current_screen.name == "main_screen":
                self.manager.setLoginScreen()
        except:
            pass

        self.manager.transition = FadeTransition(duration=0.2, clearcolor=self.theme_cls.bg_dark)


Passbank().run()
