import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class AESCipher():
    def __init__(self, key, iv):
        self.cipher = Cipher(algorithms.AES(key.encode("utf-8")), modes.CBC(iv.encode("utf-8")), backend=default_backend())

    def encrypt(self, raw):
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(128).padder()

        raw = padder.update(raw.encode("utf-8")) + padder.finalize()
        encrypted = encryptor.update(raw) + encryptor.finalize()
        encoded = base64.b64encode(encrypted).decode("utf-8")

        return encoded

    def decrypt(self, encoded):
        decryptor = self.cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()

        decrypted = base64.b64decode(encoded)
        raw = decryptor.update(decrypted) + decryptor.finalize()
        raw = (unpadder.update(raw) + unpadder.finalize()).decode("utf-8")

        return raw


if __name__ == "__main__":
    key = "Ahx+hxC=sKb9gw2Dvy2e^ALWF4gnYqj$"
    iv = "y%sL3CtWtRVdaL!?"
    cipher = AESCipher(key, iv)

    plaintext = input("text : ")
    encrypted = cipher.encrypt(plaintext)
    print('Encrypted:', encrypted)
    decrypted = cipher.decrypt(encrypted)
    print('Decrypted:', decrypted)
