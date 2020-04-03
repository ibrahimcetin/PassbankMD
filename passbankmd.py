from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.icon_definitions import md_icons
from kivymd.uix.dialog import MDDialog
from toast import toast

import sqlite3
import random
from pyaes import AESCipher


kv_string = """
<BaseScreen>

    MDToolbar:
        title: "Passbank"
        elevation: 10
        pos_hint: {"top": 1}

<RegisterScreen>

    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .65

        MDLabel:
            text: "Welcome to Passbank"
            halign: "center"
            pos_hint: {"center_x": .5}
            font_style: "Button"
            
        Widget:

        MDTextField:
            id: reg_pass_input
            hint_text: "Password"
            helper_text_mode: "on_error"
            password: True
        
        MDTextField:
            id: reg_confirm_pass_input
            hint_text: "Confirm Password"
            helper_text_mode: "on_error"
            password: True
        
        MDRaisedButton:
            text: "Register"
            pos_hint: {"center_x": .5}
            on_press: root.registerBtn()


<LoginScreen>

    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .65

        MDLabel:
            text: "Welcome to Passbank"
            halign: "center"
            pos_hint: {"center_x": .5}
            font_style: "Button"
            
        Widget:

        MDTextField:
            id: login_pass_input
            hint_text: "Password"
            password: True
            helper_text: "Password not correct"
            helper_text_mode: "on_error"

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": .5}
            on_press: root.loginBtn()


<CustomThreeLineIconListItem>
    IconLeftWidget:
        icon: root.icon
   

<MainScreen>
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: [0, 55, 0, 0]

        MDBoxLayout:
            size_hint_y: None
            height: self.minimum_height
            #md_bg_color: app.theme_cls.primary_color

            MDIconButton:
                icon: 'magnify'

            MDTextField:
                id: search_field
                hint_text: 'Search Account'
                on_text: root.setAccounts()

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                default_size: None, 250
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
    
    MDFloatingActionButtonSpeedDial:
        data: root.btn_data
        rotation_root_button: True
        callback: root.actionBtn

<ContentCustomBottomSheet>:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"
    
    MDToolbar:
        id: sheet_toolbar
        #title: "Edit"
        elevation: 10
        pos_hint: {"top": 1}
        right_action_items: [["trash-can-outline", lambda button: root.deleteAccountDialog()], ["content-copy", lambda button: root.copyPassword()], ["content-save", lambda button: root.updateAccount()]]
        
    MDBoxLayout:
        adaptive_height: True
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint_x: .65

        MDTextField:
            id: sheet_site_input
            hint_text: "Site"
            required: True
            helper_text_mode: "on_error"
            
        MDTextField:
            id: sheet_email_input
            hint_text: "EMail"
            
        MDTextField:
            id: sheet_username_input
            hint_text: "Username"
            
        MDSeparator:
        	
        MDTextField:
            id: sheet_pass_input
            hint_text: "New Password"
            password: True
            
        MDTextField:
            id: sheet_confirm_pass_input
            hint_text: "New Password Confirm"
            password: True
        
        Widget:
            size_hint_y: None
            pos_hint: {"center_x": .5}
            height: dp(40)
            

<AddAccountScreen>
   
    MDBoxLayout:
        padding: dp(10)
        spacing: dp(10)
        orientation: "vertical"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: .65
        
        MDLabel:
            text: "Add New Account"
            halign: "center"
            pos_hint: {"center_x": .5}

        MDTextField:
            id: add_acc_site_input
            hint_text: "Site"
            required: True
            helper_text_mode: "on_error"
        
        MDTextField:
            id: add_acc_email_input
            hint_text: "EMail"
        
        MDTextField:
            id: add_acc_username_input
            hint_text: "Username"

        MDTextField:
            id: add_acc_pass_input
            hint_text: "Password"
            password: True
            required: True
            helper_text_mode: "on_error"

        MDTextField:
            id: add_acc_conf_pass_input
            hint_text: "Confirm Password"
            password: True
            required: True
            helper_text_mode: "on_error"

        MDRaisedButton:
            text: "Add Account"
            pos_hint: {"center_x": .5}
            on_press: root.addAccountBtn()

"""

Builder.load_string(kv_string)


def connectDatabase():
    con = sqlite3.connect("pass.db")
    cursor = con.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS accounts (site TEXT, email TEXT, username TEXT, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS password (password TEXT)")

    return (con, cursor)

def getCipher():
    key = "F:NnQw}c(06BdclrX8_mJbGq]i#m5&hw"
    iv = "lA%u]-hF&GRx{P`s"
    cipher = AESCipher(key, iv)

    return cipher


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        Window.bind(on_keyboard=self.on_key)
    
    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.current_screen.name == "add_account_screen":
                self.transition.direction = "right"
                self.current = "main_screen"
                return True # do not exit the app
            
            if self.current_screen.name == "register_screen":
                return False # exit the app from this page
            
            if self.current_screen.name == "login_screen":
                return False
            
            if self.current_screen.name == "main_screen":
                return False
    

class BaseScreen(Screen, MDApp):
    pass

class RegisterScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        
        self.sm = sm
        
        self.con, self.cursor = connectDatabase()
        
        self.cipher = getCipher()
        
        
    def registerBtn(self):
        password = self.ids.reg_pass_input.text
        confirm_password = self.ids.reg_confirm_pass_input.text
        
        if password == "":
            self.ids.reg_pass_input.helper_text = "Password required"
            self.ids.reg_pass_input.error = True
        
        elif confirm_password == "":
            self.ids.reg_confirm_pass_input.helper_text = "Password required"
            self.ids.reg_confirm_pass_input.error = True
        
        elif password == confirm_password:
            encrypted = self.cipher.encrypt(password)
            
            self.cursor.execute("INSERT INTO password VALUES(?)",(encrypted,))
            self.con.commit()
            
            self.sm.current = "main_screen"
            
        else:
            self.ids.reg_pass_input.helper_text = "Passwords not match"
            self.ids.reg_confirm_pass_input.helper_text = "Passwords not match"
            
            self.ids.reg_pass_input.error = True
            self.ids.reg_confirm_pass_input.error = True
            
 
class LoginScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        
        self.sm = sm

        self.con, self.cursor = connectDatabase()
        
        self.cipher = getCipher()
    
    def loginBtn(self):
        self.cursor.execute("SELECT password FROM password")
        encrypted = self.cursor.fetchall()[0][0]

        self.password = self.cipher.decrypt(encrypted)
        
        if self.password == self.ids.login_pass_input.text:
            self.ids.login_pass_input.error = False
            self.sm.current = "main_screen"

        else:
            self.ids.login_pass_input.error = True
        
 
 
class CustomThreeLineIconListItem(ThreeLineIconListItem):
    icon = StringProperty()

class ContentCustomBottomSheet(MDBoxLayout):
    def __init__(self, site, email, username, **kwargs):
        super().__init__(**kwargs)
        
        self.con, self.cursor = connectDatabase()
        
        self.cipher = getCipher()
        
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
        if new_site == "":
            pass
            
        elif new_site == self.site:
            pass
        
        else:
            self.cursor.execute("UPDATE accounts SET site=? WHERE site=? AND email=?",(new_site, self.site, self.email))
            self.con.commit()
            
            self.site = new_site
            
            toast(f"{self.site} successfully changed")
        ###
        
        if not (new_email == self.email):
            self.cursor.execute("UPDATE accounts SET email=? WHERE site=? AND email=?",(new_email, self.site, self.email))
            self.con.commit()
            
            self.email = new_email
            
            toast("Email successfully changed")
        
        if not (new_username == self.username):
            self.cursor.execute("UPDATE accounts SET username=? WHERE site=? AND email=?",(new_username, self.site, self.email))
            self.con.commit()
            
            self.username = new_username
            
            toast("Username successfully changed")
        
        if not (new_password == ""):
            if new_password == confirm_new_password:
                encrypted = self.cipher.encrypt(new_password)
                
                self.cursor.execute("UPDATE accounts SET password=? WHERE site=? AND email=?",(encrypted, self.site, self.email))
                self.con.commit()
                
                toast("Password successfully changed")
            
            else:
                toast("Passwords not match")
        
    def deleteAccountDialog(self):
        dialog = MDDialog(
            title="Delete",
            size_hint=(0.7, 0.2),
            text_button_ok="Yes",
            text=f"Delete [b]{self.site}[/b]?",
            text_button_cancel="Cancel",
            events_callback=self.deleteAccount,
        )
        dialog.open()
        
    def deleteAccount(self, *args):
        if args[0] == "Yes":
            self.cursor.execute("DELETE FROM accounts WHERE site=? AND email=?", (self.site, self.email))
            self.con.commit()
            
            toast(f"{self.site} successfully deleted")
        

class MainScreen(Screen):
    custom_sheet = None
    
    btn_data = {
            "key": "Suggest Password",
            'account-plus': 'Add Account',
            "clipboard": "Clear Clipboard"
    }
    
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        
        self.sm = sm

        self.con, self.cursor = connectDatabase()
        
        self.cipher = getCipher()
        
        self.chars = ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m","1","2","3","4","5","6","7","8","9","0","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M","!","?","&","#","(",")","_","-","@","$",".","+","*", "/"]
    
        Clock.schedule_interval(self.updateScreen, 3)
    
    def updateScreen(self, *args):
        if self.sm.current == "main_screen":
            self.setAccounts()
        
    def getAccounts(self):
        self.cursor.execute("SELECT site,email,username FROM accounts ORDER BY site")
        self.accounts = self.cursor.fetchall()
       
    def setAccounts(self):
        self.getAccounts()
        
        search= False
        search_text = self.ids.search_field.text
        if search_text: 
            search = True
    	
        def addAccounts(site, email, username):
            icon = "-".join(site.lower().split())
            if icon not in md_icons.keys():
                icon = ""
            
            if email == "":
                email = " "
            
            if username == "":
                username = " "
                
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
                    addAccounts(site, email, username)
            else:
                addAccounts(site, email, username)

    def actionBtn(self, button):
        if button.icon == "key":
            password = "".join([random.choice(self.chars) for i in range(0, 15)])
            Clipboard.copy(password)
            toast(f"{password} copied")

        if button.icon == "clipboard":
            Clipboard.copy(" ")
            toast("Clipboard Cleaned")

        if button.icon == "account-plus":
            self.sm.transition.direction = "left"
            self.sm.current = "add_account_screen"
    
    def openBottomSheet(self, site, email, username):
        self.custom_sheet = MDCustomBottomSheet(screen=ContentCustomBottomSheet(site, email, username))
        self.custom_sheet.open()
    

class AddAccountScreen(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        
        self.sm = sm

        self.cipher = getCipher()
        
        self.conn, self.cursor = connectDatabase()
        
    def restartScreen(self, *args):
        self.ids.add_acc_site_input.text = ""
        self.ids.add_acc_email_input.text = ""
        self.ids.add_acc_username_input.text = ""
        self.ids.add_acc_pass_input.text = ""
        self.ids.add_acc_conf_pass_input.text = ""
        
        self.manager.transition.unbind(on_complete=self.restartScreen)
        
    def addAccountBtn(self):
        
        site = self.ids.add_acc_site_input.text
        email = self.ids.add_acc_email_input.text
        username = self.ids.add_acc_username_input.text
        
        password = self.ids.add_acc_pass_input.text
        confirm_password = self.ids.add_acc_conf_pass_input.text
        
        
        if password == confirm_password:
            if site == "":
                toast("Site is required")
                return

            if password == "" or confirm_password == "":
                toast("Password is required")
                return
            
            encrypted = self.cipher.encrypt(password)
            
            self.cursor.execute("INSERT INTO accounts VALUES(?,?,?,?)",(site, email, username, encrypted))
            self.conn.commit()
            
            toast(f"{site} account added")
            
            self.sm.transition.bind(on_complete=self.restartScreen)
            self.sm.transition.direction = "right"
            self.sm.current = "main_screen"
            
        else:
            toast("Passwords not match")
            return


sm = MyScreenManager()

### Change Startup Screen
con, cursor = connectDatabase()
cipher = getCipher()

cursor.execute("SELECT password FROM password")
password = cursor.fetchall()

if password:
    sm.add_widget(LoginScreen(name="login_screen", sm=sm))
else:
    sm.add_widget(RegisterScreen(name="register_screen", sm=sm))
###

sm.add_widget(MainScreen(name="main_screen", sm=sm))
sm.add_widget(AddAccountScreen(name="add_account_screen", sm=sm))



class PassbankApp(MDApp):
    def build(self):
        return sm

if __name__ == "__main__":
    PassbankApp().run()
