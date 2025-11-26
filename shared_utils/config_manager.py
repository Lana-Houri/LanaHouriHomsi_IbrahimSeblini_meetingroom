"""
Secure Configuration Management
Manages sensitive configuration with support for AWS Secrets Manager.
"""
import os
from typing import Optional, Dict
import json


class ConfigManager:
    """
    Manages application configuration securely.
    Supports:
    - Environment variables (default)
    - AWS Secrets Manager (optional)
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self._secrets_cache = {}
        self._use_aws_secrets = os.getenv('USE_AWS_SECRETS', 'false').lower() == 'true'
        
        if self._use_aws_secrets:
            try:
                import boto3
                self.secrets_client = boto3.client('secretsmanager', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            except ImportError:
                print("WARNING: boto3 not installed. AWS Secrets Manager disabled.")
                self._use_aws_secrets = False
                self.secrets_client = None
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value from environment or AWS Secrets Manager.
        
        Args:
            key: Secret key name
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        # First try environment variable
        value = os.getenv(key, default)
        if value:
            return value
        
        # Try AWS Secrets Manager if enabled
        if self._use_aws_secrets and self.secrets_client:
            return self._get_aws_secret(key, default)
        
        return default
    
    def _get_aws_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of secret in AWS Secrets Manager
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        try:
            # Check cache first
            if secret_name in self._secrets_cache:
                return self._secrets_cache[secret_name]
            
            # Get secret from AWS
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            
            # Try to parse as JSON (AWS Secrets Manager stores as JSON)
            try:
                secret_dict = json.loads(secret)
                # If it's a dict, try to get the key
                if isinstance(secret_dict, dict):
                    # Use the secret_name as key, or first key if not found
                    value = secret_dict.get(secret_name, secret_dict.get(list(secret_dict.keys())[0]))
                else:
                    value = secret
            except:
                value = secret
            
            # Cache it
            self._secrets_cache[secret_name] = value
            return value
            
        except Exception as e:
            print(f"WARNING: Failed to get secret from AWS: {str(e)}")
            return default
    
    def get_db_config(self) -> Dict[str, str]:
        """
        Get database configuration securely.
        
        Returns:
            Dictionary with db_host, db_name, db_user, db_password
        """
        return {
            'host': self.get_secret('DB_HOST', 'db'),
            'database': self.get_secret('DB_NAME', 'meetingroom'),
            'user': self.get_secret('DB_USER', 'admin'),
            'password': self.get_secret('DB_PASSWORD', 'password'),
        }
    
    def get_encryption_key(self) -> Optional[str]:
        """
        Get encryption key securely.
        
        Returns:
            Encryption key or None
        """
        return self.get_secret('ENCRYPTION_KEY')
    
    def get_api_keys(self) -> Dict[str, str]:
        """
        Get API keys for external services.
        
        Returns:
            Dictionary of API keys
        """
        return {
            'service_api_key': self.get_secret('SERVICE_API_KEY'),
        }


# Global config manager instance
config_manager = ConfigManager()

