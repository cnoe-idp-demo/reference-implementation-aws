"""
Utility functions for AWS Secrets Manager integration.
"""
import json
import boto3
from botocore.exceptions import ClientError
from typing import Any, Optional


class SecretsManager:
    """Simple wrapper for AWS Secrets Manager operations."""
    
    def __init__(self, region_name: str = "us-west-2"):
        """
        Initialize the Secrets Manager client.
        
        Args:
            region_name: AWS region name (default: us-west-2)
        """
        self.client = boto3.client('secretsmanager', region_name=region_name)
    
    def get_secret(self, secret_key: str) -> Any:
        """
        Retrieve a secret from AWS Secrets Manager.
        
        Args:
            secret_key: The name or ARN of the secret
            
        Returns:
            The secret value (parsed as JSON if applicable, otherwise raw string)
            
        Raises:
            Exception: If secret retrieval fails
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_key)
            
            # Secrets can be stored as either SecretString or SecretBinary
            if 'SecretString' in response:
                secret = response['SecretString']
                # Try to parse as JSON, return as-is if not valid JSON
                try:
                    return json.loads(secret)
                except json.JSONDecodeError:
                    return secret
            else:
                # Binary secrets are returned as-is
                return response['SecretBinary']
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Secret '{secret_key}' not found")
            elif error_code == 'InvalidRequestException':
                raise Exception(f"Invalid request for secret '{secret_key}'")
            elif error_code == 'InvalidParameterException':
                raise Exception(f"Invalid parameter for secret '{secret_key}'")
            elif error_code == 'DecryptionFailure':
                raise Exception(f"Failed to decrypt secret '{secret_key}'")
            elif error_code == 'InternalServiceError':
                raise Exception(f"AWS service error retrieving secret '{secret_key}'")
            else:
                raise Exception(f"Error retrieving secret '{secret_key}': {str(e)}")
    
    def get_secret_field(self, secret_key: str, field: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a specific field from a JSON secret.
        
        Args:
            secret_key: The name or ARN of the secret
            field: The field name to extract from the JSON secret
            default: Default value if field doesn't exist
            
        Returns:
            The field value or default if not found
        """
        secret = self.get_secret(secret_key)
        if isinstance(secret, dict):
            return secret.get(field, default)
        raise Exception(f"Secret '{secret_key}' is not a JSON object")


# Convenience function for quick access
def get_secret(secret_key: str, region_name: str = "us-west-2") -> Any:
    """
    Quick helper to get a secret value.
    
    Args:
        secret_key: The name or ARN of the secret
        region_name: AWS region name (default: us-west-2)
        
    Returns:
        The secret value
    """
    sm = SecretsManager(region_name=region_name)
    return sm.get_secret(secret_key)


def get_secret_field(secret_key: str, field: str, default: Optional[Any] = None, region_name: str = "us-west-2") -> Any:
    """
    Quick helper to get a specific field from a JSON secret.
    
    Args:
        secret_key: The name or ARN of the secret
        field: The field name to extract
        default: Default value if field doesn't exist
        region_name: AWS region name (default: us-west-2)
        
    Returns:
        The field value or default
    """
    sm = SecretsManager(region_name=region_name)
    return sm.get_secret_field(secret_key, field, default)
