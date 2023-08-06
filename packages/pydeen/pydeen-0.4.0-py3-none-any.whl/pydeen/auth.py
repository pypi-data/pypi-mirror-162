#from aiohttp import BasicAuth
#from sympy import im

from pydeen.types import Auth
from pydeen.menu import MenuSelection, UserInput
from pydeen.utils import CryptUtil
from base64 import b64encode
import requests

class AuthBasic(Auth):

    MENU_SET_AUTH_NAME  = "set_auth_name"
    MENU_SET_AUTH_PATH  = "set_auth_path"
    MENU_SET_BASIC_AUTH = "set_basic_auth"
    MENU_RESET_AUTH     = "reset_auth"
    MENU_LOAD_AUTH      = "load_auth"
    MENU_SAVE_AUTH      = "save_auth"



    def __init__(self):
        super().__init__()
        self.type = "pydeeen.AuthBasic"
        self.menu_name = "default"
        self.menu_path = None
        
    def is_basic_auth_available(self) -> bool:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            return True
        else:
            return False    

    def set_basic_auth(self, user:str, password:str) -> bool:
        enc_pw = CryptUtil.get_engine().encode(password)  
        self._properties = {}
        self.set_property(Auth.AUTH_PROP_TYPE, Auth.AUTH_TYPE_BASIC)
        self.set_property(Auth.AUTH_PROP_USER, user)
        self.set_property(Auth.AUTH_PROP_PASS, enc_pw)
        return True

    def init_from_config(self, type, config) -> bool:
        if type == Auth.AUTH_TYPE_BASIC:
            self._properties = {}
            self.set_property(Auth.AUTH_PROP_TYPE, Auth.AUTH_TYPE_BASIC)
            self.set_property(Auth.AUTH_PROP_USER, config[Auth.AUTH_PROP_USER])
            self.set_property(Auth.AUTH_PROP_PASS, config[Auth.AUTH_PROP_PASS])
            return True
        else:
            return False      

    def get_username(self) -> str:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            return self.get_property(Auth.AUTH_PROP_USER)
        else:
            return None

    def get_password(self) -> str:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            return self.get_property(Auth.AUTH_PROP_PASS)
        else:
            return None

    def get_auth_for_request(self):
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            username = self.get_property(Auth.AUTH_PROP_USER)
            password = self.get_property(Auth.AUTH_PROP_PASS)
            
            if len(username) == 0 or len(password) == 0:
                return None 
            
            return (username,password)
        else:
            return None    

    def get_auth_for_requests_session(self):
        self.trace("set basic auth info as requests session")
        s = requests.Session()
        s.auth = (self.get_username(), self.get_password())
        return s


    def get_auth_headers(self) -> dict:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            username = self.get_property(Auth.AUTH_PROP_USER)
            password = self.get_property(Auth.AUTH_PROP_PASS)
            
            if len(username) == 0 or len(password) == 0:
                return None 
            
            user_pass = f'{username}:{password}'
            basic_credentials = b64encode(user_pass.encode()).decode()
            return {'Authorization': f'Basic {basic_credentials}'}
        else:
            return None    

    def menu(self):        
        valid = True
        while valid == True:           
           
         # build main menu    
            entries = {}
            entries[AuthBasic.MENU_SET_AUTH_PATH] = f"Set path for auth info ({self.menu_path})"
            entries[AuthBasic.MENU_SET_AUTH_NAME] = f"Set name auth info ({self.menu_name})"
            
            if self.is_basic_auth_available() == True:
                entries[AuthBasic.MENU_SAVE_AUTH] = "Save current auth info"
                entries[AuthBasic.MENU_RESET_AUTH] = "Reset auth info"
            else:
                entries[AuthBasic.MENU_LOAD_AUTH] = "Load auth info"
                entries[AuthBasic.MENU_SET_BASIC_AUTH] = "Set user password"

            # show menu            
            action = MenuSelection("Basic Authentification - Menu", entries, True, False).show_menu()
            if action.is_quit_entered():
                valid = False
            else:
                selected = action.get_selection()
                if selected == AuthBasic.MENU_RESET_AUTH:
                    self._properties = {}
                    print("authentification cleared")
                elif selected == AuthBasic.MENU_SET_AUTH_NAME:
                    self.menu_name = UserInput("Enter name", self.menu_name).get_input()
                    print(f"use name {self.menu_name} for auth")
                elif selected == AuthBasic.MENU_SET_AUTH_PATH:
                    self.menu_path = UserInput("Enter save path for auth info", self.menu_path).get_input(empty_allowed=True)
                    print(f"use path {self.menu_name} for auth storage")
                elif selected == AuthBasic.MENU_SET_BASIC_AUTH:
                    user = UserInput("Enter username", self.get_username()).get_input()
                    pw = UserInput("Enter password", None).get_password(empty_allowed=True)
                    if pw == None:
                        print("Set auth info skipped")
                    else:
                        self.set_basic_auth(user, pw)
                        print("auth info set")    
                    print(f"use name {self.menu_name} for auth")
                elif selected == AuthBasic.MENU_SAVE_AUTH:
                    if self.menu_path != None:
                        filename = f"{self.menu_path}/{self.menu_name}.auth"
                    else:
                        filename = f"{self.menu_name}.auth"    
                    
                    filename = UserInput("Enter filename for save auth info", filename).get_input(empty_allowed=True)
                    if filename == None:
                        print("save auth info skipped")
                    else:
                        if self.save_config(filename) == True:
                            print(f"current auth info saved to file {filename}")
                        else:
                            print(f"Error while saving current auth info to {filename}")       
                elif selected == AuthBasic.MENU_LOAD_AUTH:
                    if self.menu_path != None:
                        filename = f"{self.menu_path}/{self.menu_name}.auth"
                    else:
                        filename = f"{self.menu_name}.auth"    
                    
                    filename = UserInput("Enter filename for load auth info", filename).get_input(empty_allowed=True)
                    if filename == None:
                        print("load auth info skipped")
                    else:
                        if self.load_config(filename) == True:
                            print(f"current auth info loaded from file {filename}")
                        else:
                            print(f"Error while loading current auth info from {filename}")       
                else:
                    print("unknown menu action")

