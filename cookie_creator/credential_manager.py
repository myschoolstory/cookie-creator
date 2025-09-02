"""
Credential Manager for secure storage and retrieval of user credentials.

This module provides a CredentialManager class that handles secure storage
and retrieval of user credentials for different sites. It uses python-keyring
as the primary storage backend with a fallback to encrypted JSON file storage.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


logger = logging.getLogger(__name__)


class CredentialManagerError(Exception):
    """Base exception for credential manager errors."""
    pass


class CredentialStorageError(CredentialManagerError):
    """Exception raised when credential storage operations fail."""
    pass


class CredentialRetrievalError(CredentialManagerError):
    """Exception raised when credential retrieval operations fail."""
    pass


class CredentialValidationError(CredentialManagerError):
    """Exception raised when credential validation fails."""
    pass


class CredentialManager:
    """
    Manages secure storage and retrieval of user credentials for different sites.
    
    Uses python-keyring as the primary storage backend with a fallback to
    encrypted JSON file storage when keyring is unavailable.
    """
    
    SERVICE_PREFIX = "cookie-creator"
    ENCRYPTED_FILE_NAME = "credentials.enc"
    KEY_FILE_NAME = "credential_key.key"
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the CredentialManager.
        
        Args:
            storage_dir: Directory for fallback encrypted file storage.
                        Defaults to ~/.cookie-creator/
        """
        self.use_keyring = KEYRING_AVAILABLE
        self.use_encryption = CRYPTOGRAPHY_AVAILABLE
        
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.cookie-creator")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.encrypted_file_path = self.storage_dir / self.ENCRYPTED_FILE_NAME
        self.key_file_path = self.storage_dir / self.KEY_FILE_NAME
        
        # Initialize encryption key if using file storage
        if not self.use_keyring and self.use_encryption:
            self._ensure_encryption_key()
        
        logger.info(f"CredentialManager initialized with keyring={self.use_keyring}, "
                   f"encryption={self.use_encryption}")
    
    def _validate_site(self, site: str) -> str:
        """
        Validate and normalize site name.
        
        Args:
            site: Site identifier to validate
            
        Returns:
            Normalized site name
            
        Raises:
            CredentialValidationError: If site name is invalid
        """
        if not site or not isinstance(site, str):
            raise CredentialValidationError("Site name must be a non-empty string")
        
        # Normalize site name: lowercase, alphanumeric and common separators only
        site = site.lower().strip()
        if not re.match(r'^[a-z0-9._-]+$', site):
            raise CredentialValidationError(
                "Site name can only contain lowercase letters, numbers, dots, "
                "underscores, and hyphens"
            )
        
        return site
    
    def _validate_credentials(self, username: str, password: str) -> Tuple[str, str]:
        """
        Validate username and password.
        
        Args:
            username: Username to validate
            password: Password to validate
            
        Returns:
            Tuple of (username, password)
            
        Raises:
            CredentialValidationError: If credentials are invalid
        """
        if not username or not isinstance(username, str):
            raise CredentialValidationError("Username must be a non-empty string")
        
        if not password or not isinstance(password, str):
            raise CredentialValidationError("Password must be a non-empty string")
        
        username = username.strip()
        if not username:
            raise CredentialValidationError("Username cannot be empty or whitespace only")
        
        return username, password
    
    def _get_service_name(self, site: str) -> str:
        """Get the service name for keyring storage."""
        return f"{self.SERVICE_PREFIX}:{site}"
    
    def _ensure_encryption_key(self) -> None:
        """Ensure encryption key exists for file storage."""
        if not self.key_file_path.exists():
            key = Fernet.generate_key()
            try:
                with open(self.key_file_path, 'wb') as key_file:
                    key_file.write(key)
                # Set restrictive permissions on the key file
                os.chmod(self.key_file_path, 0o600)
                logger.info("Generated new encryption key for credential storage")
            except OSError as e:
                raise CredentialStorageError(f"Failed to create encryption key: {e}")
    
    def _get_encryption_key(self) -> bytes:
        """Get the encryption key for file storage."""
        try:
            with open(self.key_file_path, 'rb') as key_file:
                return key_file.read()
        except OSError as e:
            raise CredentialRetrievalError(f"Failed to read encryption key: {e}")
    
    def _load_encrypted_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load credentials from encrypted file storage."""
        if not self.encrypted_file_path.exists():
            return {}
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            with open(self.encrypted_file_path, 'rb') as enc_file:
                encrypted_data = enc_file.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        
        except Exception as e:
            raise CredentialRetrievalError(f"Failed to load encrypted credentials: {e}")
    
    def _save_encrypted_credentials(self, credentials: Dict[str, Dict[str, str]]) -> None:
        """Save credentials to encrypted file storage."""
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            json_data = json.dumps(credentials).encode()
            encrypted_data = fernet.encrypt(json_data)
            
            with open(self.encrypted_file_path, 'wb') as enc_file:
                enc_file.write(encrypted_data)
            
            # Set restrictive permissions on the credentials file
            os.chmod(self.encrypted_file_path, 0o600)
            
        except Exception as e:
            raise CredentialStorageError(f"Failed to save encrypted credentials: {e}")
    
    def save_credential(self, site: str, username: str, password: str) -> None:
        """
        Store credentials for a specific site.
        
        Args:
            site: Site identifier (e.g., 'youtube', 'github')
            username: Username for the site
            password: Password for the site
            
        Raises:
            CredentialValidationError: If site name or credentials are invalid
            CredentialStorageError: If storage operation fails
        """
        site = self._validate_site(site)
        username, password = self._validate_credentials(username, password)
        
        if self.use_keyring:
            try:
                service_name = self._get_service_name(site)
                keyring.set_password(service_name, username, password)
                logger.info(f"Stored credentials for {site} using keyring")
                return
            except Exception as e:
                logger.warning(f"Keyring storage failed for {site}: {e}")
                # Fall through to file storage
        
        if self.use_encryption:
            try:
                credentials = self._load_encrypted_credentials()
                credentials[site] = {"username": username, "password": password}
                self._save_encrypted_credentials(credentials)
                logger.info(f"Stored credentials for {site} using encrypted file storage")
                return
            except Exception as e:
                logger.error(f"Encrypted file storage failed for {site}: {e}")
                raise CredentialStorageError(f"Failed to store credentials for {site}: {e}")
        
        raise CredentialStorageError(
            "No secure storage backend available. Please install 'keyring' or 'cryptography'"
        )
    
    def get_credential(self, site: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve stored credentials for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            Tuple of (username, password) if found, None otherwise
            
        Raises:
            CredentialValidationError: If site name is invalid
            CredentialRetrievalError: If retrieval operation fails
        """
        site = self._validate_site(site)
        
        if self.use_keyring:
            try:
                service_name = self._get_service_name(site)
                # Try to find any stored credentials for this service
                # We need to get the username first, which requires checking stored credentials
                if self.use_encryption:
                    # Check file storage for username if available
                    try:
                        credentials = self._load_encrypted_credentials()
                        if site in credentials:
                            username = credentials[site]["username"]
                            # Try keyring first with this username
                            password = keyring.get_password(service_name, username)
                            if password:
                                logger.info(f"Retrieved credentials for {site} from keyring")
                                return username, password
                    except Exception:
                        pass
                
                # If we can't get username from file storage, we can't use keyring effectively
                # Fall through to file storage
                
            except Exception as e:
                logger.warning(f"Keyring retrieval failed for {site}: {e}")
                # Fall through to file storage
        
        if self.use_encryption:
            try:
                credentials = self._load_encrypted_credentials()
                if site in credentials:
                    cred = credentials[site]
                    logger.info(f"Retrieved credentials for {site} from encrypted file storage")
                    return cred["username"], cred["password"]
            except Exception as e:
                logger.error(f"Encrypted file retrieval failed for {site}: {e}")
                raise CredentialRetrievalError(f"Failed to retrieve credentials for {site}: {e}")
        
        return None
    
    def list_sites(self) -> List[str]:
        """
        List all sites with stored credentials.
        
        Returns:
            List of site identifiers
            
        Raises:
            CredentialRetrievalError: If listing operation fails
        """
        sites = set()
        
        # Get sites from encrypted file storage
        if self.use_encryption:
            try:
                credentials = self._load_encrypted_credentials()
                sites.update(credentials.keys())
            except Exception as e:
                logger.warning(f"Failed to list sites from encrypted storage: {e}")
        
        # Note: Keyring doesn't provide a direct way to list all stored credentials
        # We rely on the encrypted file storage to maintain the list of sites
        
        return sorted(list(sites))
    
    def delete_credential(self, site: str) -> bool:
        """
        Remove credentials for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            True if credentials were deleted, False if not found
            
        Raises:
            CredentialValidationError: If site name is invalid
            CredentialStorageError: If deletion operation fails
        """
        site = self._validate_site(site)
        deleted = False
        
        # Delete from keyring if available
        if self.use_keyring:
            try:
                # First get the username from file storage if available
                username = None
                if self.use_encryption:
                    try:
                        credentials = self._load_encrypted_credentials()
                        if site in credentials:
                            username = credentials[site]["username"]
                    except Exception:
                        pass
                
                if username:
                    service_name = self._get_service_name(site)
                    keyring.delete_password(service_name, username)
                    deleted = True
                    logger.info(f"Deleted credentials for {site} from keyring")
                    
            except Exception as e:
                logger.warning(f"Keyring deletion failed for {site}: {e}")
        
        # Delete from encrypted file storage
        if self.use_encryption:
            try:
                credentials = self._load_encrypted_credentials()
                if site in credentials:
                    del credentials[site]
                    self._save_encrypted_credentials(credentials)
                    deleted = True
                    logger.info(f"Deleted credentials for {site} from encrypted file storage")
            except Exception as e:
                logger.error(f"Encrypted file deletion failed for {site}: {e}")
                raise CredentialStorageError(f"Failed to delete credentials for {site}: {e}")
        
        return deleted
    
    def has_credential(self, site: str) -> bool:
        """
        Check if credentials exist for a site.
        
        Args:
            site: Site identifier
            
        Returns:
            True if credentials exist, False otherwise
            
        Raises:
            CredentialValidationError: If site name is invalid
        """
        try:
            return self.get_credential(site) is not None
        except CredentialRetrievalError:
            return False
    
    def get_storage_info(self) -> Dict[str, any]:
        """
        Get information about the storage backend being used.
        
        Returns:
            Dictionary with storage backend information
        """
        return {
            "keyring_available": KEYRING_AVAILABLE,
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
            "using_keyring": self.use_keyring,
            "using_encryption": self.use_encryption,
            "storage_dir": str(self.storage_dir),
            "encrypted_file_exists": self.encrypted_file_path.exists() if self.use_encryption else False,
            "key_file_exists": self.key_file_path.exists() if self.use_encryption else False
        }