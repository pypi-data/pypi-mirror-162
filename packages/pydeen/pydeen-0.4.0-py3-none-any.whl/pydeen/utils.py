"""
    some utils for pydeen
"""

import pathlib
import hashlib
import base64
from cryptography.fernet import Fernet
import sys


class CryptEngine():
    
    PROP_SALT = "salt"
    PROP_ENGINE  = "engine"
    PROP_ENCODED = "encoded"
    
    def __init__(self, context:bytes=None, salt:bytes=None) -> None:
        self.context:bytes = context
        self.salt:bytes = salt
        self.engine:str = "unknown"  
    
    def encode(self, content:str):
        return content

    def decode(self, content:any):
        return content    

    def set_salt(self, salt:bytes):
        self.salt = salt        

    def set_context(self, context:bytes):
        self.context = context        

class CryptEngineDefault(CryptEngine):
    def __init__(self, context: bytes = None, salt: bytes = None) -> None:
        super().__init__(context, salt)
        self.engine = "default"
    
    def get_key(self) -> bytes:
        if self.context == None:
            self.context = CryptUtil.get_context_key()

        if self.salt == None:
            self.salt = CryptUtil.create_salt_key()  

        lenc = len(self.context)
        if lenc < 16:
            key = self.context + self.salt
        else:
            key = self.context[:16] + self.salt[:16]   

        return base64.urlsafe_b64encode(key) 

    def encode(self, content:str):        
        f = Fernet(self.get_key())
        e = f.encrypt(content.encode())
        result = {}
        result[CryptEngine.PROP_ENGINE] = self.engine
        result[CryptEngine.PROP_SALT] = CryptUtil.byte_to_base64(self.salt)
        result[CryptEngine.PROP_ENCODED] = CryptUtil.byte_to_base64(e)
        return result

    def decode(self, content:dict):
        try:
            engine = content[CryptEngine.PROP_ENGINE]
            if engine != self.engine:
                return content # wrong engine
            else:
                salt_b64 = content[CryptEngine.PROP_SALT]
                encoded_b64 = content[CryptEngine.PROP_ENCODED]
                self.salt = CryptUtil.base64_to_bytes(salt_b64)
                encoded = CryptUtil.base64_to_bytes(encoded_b64)    
                return Fernet(self.get_key()).decrypt(encoded).decode()
        except:
            print("Error", sys.exc_info()[0], "occurred.")
            return content  

class CryptUtil():
    
    @classmethod
    def __init__(cls) -> None:
        cls.engines = {}

    @staticmethod
    def get_context_key() -> bytes:
        context = str(pathlib.Path().resolve())
        context = context.replace("\\","")
        context = context.replace(":","")
        return hashlib.md5(context.encode()).digest()

    @staticmethod
    def create_salt_key() -> bytes:
        return base64.urlsafe_b64decode(Fernet.generate_key())

    @classmethod
    def register_engine(cls, name:str, engine:CryptEngine):
        cls.engines[name] = engine

    @classmethod
    def get_engine(cls, name:str=None, context:bytes=None, salt:bytes=None) -> CryptEngine:
        if name == None or name == "default" or len(name) == 0:
            return CryptEngineDefault(context, salt)
        
        if name in cls.engines.keys():
            return cls.engines[name]         

    @staticmethod
    def byte_to_base64(content:bytes) -> str:
        if content == None:
            return ""
        else:
            return base64.b64encode(content).decode()        

    @staticmethod
    def base64_to_bytes(base64_str:str) -> bytes:
        if base64_str == None or base64_str == "":
            return b""
        else:    
            return base64.b64decode(base64_str)    