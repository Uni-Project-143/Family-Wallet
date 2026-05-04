import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class EncryptionService:

    _SECRET_KEY_B64 = os.getenv("MONOBANK_ENCRYPTION_KEY")

    @classmethod
    def _get_key(cls) -> bytes:
        if not cls._SECRET_KEY_B64:
            raise ValueError("MONOBANK_ENCRYPTION_KEY is not set in .env")
        return base64.urlsafe_b64decode(cls._SECRET_KEY_B64)

    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        """Шифрує рядок алгоритмом AES-256-GCM."""
        key = cls._get_key()
        aesgcm = AESGCM(key)


        nonce = os.urandom(12)


        encrypted_data = aesgcm.encrypt(nonce, plain_text.encode('utf-8'), None)


        combined_data = nonce + encrypted_data


        return base64.urlsafe_b64encode(combined_data).decode('utf-8')

    @classmethod
    def decrypt(cls, encrypted_text_b64: str) -> str:
        """Розшифровує рядок, зашифрований алгоритмом AES-256-GCM."""
        key = cls._get_key()
        aesgcm = AESGCM(key)


        combined_data = base64.urlsafe_b64decode(encrypted_text_b64.encode('utf-8'))


        nonce = combined_data[:12]
        ciphertext = combined_data[12:]


        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data.decode('utf-8')
