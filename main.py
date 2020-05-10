from kivymd.app import MDApp

from baseclasses.manager import Manager


class Passbank(MDApp):
    def build(self):
        self.manager = Manager(app=self)

        return self.manager

    """
    def on_start(self):
        self.fps_monitor_start()
    """

    def on_pause(self):
        try:
            self.manager.main_screen.bottom_sheet.dismiss()
            self.manager.main_screen.bottom_sheet.screen.dialog.dismiss()
        except:
            pass

        return True

    def on_resume(self):
        # I used on_resume method instead of on_pause method when change screen to login screen
        # beacuse on_pause method not working well.
        if self.manager.current_screen.name == "main_screen":
            self.manager.setLoginScreen()

Passbank().run()
