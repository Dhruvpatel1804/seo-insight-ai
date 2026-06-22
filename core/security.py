from cryptography.fernet import Fernet
from functools import lru_cache
from passlib.context import CryptContext
import base64
import hashlib
from core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# This functionality is used to encrypt or decrypt to store/get from database
class TokenEncryption:
    def __init__(self, secret_key: str):
        # Derive a proper Fernet key from your secret
        key = hashlib.sha256(secret_key.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, token: str) -> str:
        """Encrypt a token and return base64 encoded string"""
        if not token:
            return None
        encrypted = self.fernet.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token from base64 encoded string"""
        if not encrypted_token:
            return None
        decoded = base64.urlsafe_b64decode(encrypted_token.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()


@lru_cache()
def get_token_encryptor() -> TokenEncryption:
    """Singleton instance of token encryptor"""
    return TokenEncryption(settings.FERNET_SECRET_KEY)