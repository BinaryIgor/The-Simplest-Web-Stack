import base64
import getpass
import json
import os
import secrets
import string
from os import path
from datetime import datetime

from . import meta

from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature

KEY_BYTES_LENGTH = 32
PASSWORD_LENGTH = 48
PASSWORD_CHARACTERS = f'{string.ascii_letters}{string.digits}'

META_KEY = "__meta__"


def random_key():
    return base64.b64encode(os.urandom(KEY_BYTES_LENGTH)).decode("ascii")


def random_password(length=PASSWORD_LENGTH):
    characters = list(PASSWORD_CHARACTERS)
    return ''.join(secrets.choice(characters) for _ in range(length))


def modify_secret(key, value=None, encryption_password=None):
    s_file_path = secrets_file_path()
    if path.exists(s_file_path):
        secrets_file =  meta.file_content(s_file_path)
        decrypted_file = json.loads(decrypted_data(secrets_file, encryption_password))
    else:
        decrypted_file = {}

    decrypted_file[META_KEY] =  { "modified_at": datetime.now().isoformat() }
        
    if value is None:
        decrypted_file.pop(key, None)
    else:
        decrypted_file[key] = value

    new_secrets_to_encrypt = json.dumps(decrypted_file).encode("utf8")
    encrypted_file = encrypted_data(new_secrets_to_encrypt, encryption_password)

    meta.write_binary_to_file(secrets_file_path(), encrypted_file)


def secrets_file():
    s_file_path = secrets_file_path()
    if path.exists(s_file_path):
        return meta.file_content(s_file_path)
    return None


def secrets_file_path():
    return path.join(meta.root_dir(), "config", f"secrets_{meta.current_env()}")


def secret_input(prompt):
    return getpass.getpass(prompt)


def encrypted_data(data, password):
    key = _password_to_fernet_key(password)
    return Fernet(key).encrypt(data)


def _password_to_fernet_key(password):
    key = password
    lacking_key_chars = 32 - len(key)
    for i in range(lacking_key_chars):
        key += '0'

    return base64.urlsafe_b64encode(key.encode('utf8'))


def decrypted_data(data, password=None):
    password = _given_or_from_input_password(password)
    key = _password_to_fernet_key(password)
    try:
        return Fernet(key).decrypt(data)
    except (InvalidSignature, InvalidToken):
        raise Exception("Invalid decrypt password!")


def decrypted_secrets(show_meta=False):
    decrypted = decrypted_data(meta.file_content(secrets_file_path()))
    
    decrypted_json = json.loads(decrypted)
    
    if not show_meta:
        decrypted_json.pop(META_KEY, None)

    return decrypted_json


def reencrypt_secrets(old_password, new_password):
    decrypted = decrypted_data(meta.file_content(secrets_file_path()), old_password)
    
    encrypted = encrypted_data(decrypted, new_password)

    meta.write_binary_to_file(secrets_file_path(), encrypted)


def _given_or_from_input_password(password):
    if password is None:
        password = secret_input("Secrets password: ")
    return password