"""
Encryption Utilities
Encrypt sensitive data for secure storage and transmission.
"""
from cryptography.fernet import Fernet
import os
import base64
from typing import Optional


class DataEncryption:
    """
    Simple encryption wrapper using Fernet (symmetric encryption).
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption with key.
        
        Args:
            key: Encryption key (32 bytes, base64-encoded). 
                 If None, generates new key or uses ENCRYPTION_KEY env var.
        """
        if key:
            self.key = key
        else:
            # Try to get key from environment
            env_key = os.getenv('ENCRYPTION_KEY')
            if env_key:
                self.key = env_key.encode()
            else:
                # Generate new key (should be stored securely in production)
                self.key = Fernet.generate_key()
                print(f"WARNING: Generated new encryption key. Store this securely: {self.key.decode()}")
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data.
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted string (base64-encoded)
        """
        if not data:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt string data.
        
        Args:
            encrypted_data: Encrypted string (base64-encoded)
            
        Returns:
            Decrypted string
        """
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt fields in
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encrypt(str(encrypted[field]))
        return encrypted
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to decrypt fields in
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = self.decrypt(decrypted[field])
                except:
                    # If decryption fails, keep original (might not be encrypted)
                    pass
        return decrypted


# Global encryption instance
_encryption_instance = None


def get_encryption() -> DataEncryption:
    """
    Get or create encryption instance.
    
    Returns:
        DataEncryption instance
    """
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = DataEncryption()
    return _encryption_instance


# Sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    'password_hash',
    'email',
    'phone',
    'credit_card',
    'ssn',
    'api_key',
    'secret'
]

