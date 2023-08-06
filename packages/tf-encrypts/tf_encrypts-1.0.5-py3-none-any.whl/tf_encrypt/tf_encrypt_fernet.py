import base64
import hashlib
import pickle
from fernet import Fernet


class TfEncryptFernet:

    @classmethod
    def generate_fernet_key(cls, password) -> bytes:
        if not isinstance(password, bytes):
            password = str(password).encode()
        hlib = hashlib.md5()
        hlib.update(password)
        return base64.urlsafe_b64encode(hlib.hexdigest().encode())

    def __init__(self, password):
        self.enc_key = self.generate_fernet_key(password)
        self.fernet = Fernet(self.enc_key)

    def encrypt(self, data):
        data = pickle.dumps(data)
        return self.fernet.encrypt(data)

    def decrypt(self, data):
        data = self.fernet.decrypt(data)
        return pickle.loads(data)
