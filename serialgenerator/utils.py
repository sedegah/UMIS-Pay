from django.conf import settings
from cryptography.fernet import Fernet

fernet = Fernet(settings.SERIAL_ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    """Encrypt a string value (serial, pin, etc.)"""
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted string"""
    return fernet.decrypt(encrypted_value.encode()).decode()
