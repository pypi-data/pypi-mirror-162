from tf_encrypt.tf_encrypt_fernet import TfEncryptFernet


class TfPersistentData:
    def __init__(self, password):
        assert isinstance(password, bytes) or isinstance(password, str)
        self.cipher = TfEncryptFernet(password=password)

    def write(self, data, filename):
        with open(filename, 'wb') as f:
            f.write(self.cipher.encrypt(data))

    def read(self, filename):
        with open(filename, 'rb') as f:
            return self.cipher.decrypt(f.read())
