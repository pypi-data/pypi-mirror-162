import base64
import hashlib
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class TfEncrypt:

    @classmethod
    def generate_key(cls, password, salt=None):
        salt = salt or b'_SaLt_#'
        if not isinstance(password, bytes):
            password = str(password).encode('utf-8')
        if not isinstance(salt, bytes):
            salt = str(salt).encode('utf-8')
        return hashlib.pbkdf2_hmac(hash_name='sha256', password=password, salt=salt, iterations=10000)

    def __init__(self, password, salt=None):
        self.enc_key = self.generate_key(password, salt)
        self.block_size = 16
        self.aes = AES.new(self.enc_key, AES.MODE_ECB)

    def encrypt(self, data):
        data = pickle.dumps(data)
        data = pad(data, self.block_size)
        return base64.b64encode(self.aes.encrypt(data))

    def decrypt(self, data):
        data = self.aes.decrypt(base64.b64decode(data))
        data = unpad(data, self.block_size)
        return pickle.loads(data)
