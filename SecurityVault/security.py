import bcrypt
from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    """Генерирует ключ шифрования и сохраняет его в файл."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Загружает ключ шифрования."""
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_data(data, key):
    """Шифрует строку."""
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8'))

def decrypt_data(token, key):
    """Расшифровывает строку."""
    f = Fernet(key)
    return f.decrypt(token).decode('utf-8')

def hash_password(password):
    """Хеширует пароль для БД (bcrypt)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password, hashed):
    """Проверяет пароль против хеша."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)