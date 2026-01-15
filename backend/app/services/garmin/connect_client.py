"""Garmin Connect client with OAuth token persistence.

This implementation follows the CLI's successful authentication pattern
using the garth library for OAuth token management.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Callable
import asyncio

import garth
import requests
from garminconnect import Garmin

logger = logging.getLogger(__name__)


class GarminConnectClient:
    """Garmin Connect client with OAuth token persistence.
    
    This implementation matches the CLI's successful authentication pattern.
    """
    
    def __init__(self, token_dir: Optional[str] = None):
        self._client: Optional[Garmin] = None
        
        # Use same token directory hierarchy as CLI
        self._token_dir = Path(
            token_dir
            or os.getenv("GARMINCONNECT_TOKENS")
            or os.getenv("GARTH_HOME") 
            or os.path.expanduser("~/.garminconnect")
        )
        
        # Ensure token directory exists
        self._token_dir.mkdir(parents=True, exist_ok=True)
        
    def _try_resume_tokens(self) -> bool:
        """Attempt to resume existing OAuth tokens."""
        try:
            garth.resume(str(self._token_dir))
            logger.info(f"Resumed existing Garmin OAuth tokens from {self._token_dir}")
            return True
        except Exception as exc:
            logger.info(f"No valid tokens found; need fresh login ({exc})")
            return False
    
    def _fresh_login(self, email: str, password: str, mfa_callback: Optional[Callable[[], str]] = None) -> None:
        """Perform fresh login with optional MFA support."""
        try:
            if mfa_callback is not None:
                code = mfa_callback()
                try:
                    garth.login(email, password, otp=code)
                except TypeError:
                    # Handle different garth API versions
                    garth.login(email, password, otp_callback=lambda: code)
            else:
                garth.login(email, password)
                
            garth.save(str(self._token_dir))
            logger.info(f"Saved Garmin OAuth tokens to {self._token_dir} after fresh login")
            
        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                raise ValueError(f"Invalid Garmin Connect credentials: {http_err}")
            elif http_err.response.status_code == 403:
                raise ValueError(f"Garmin Connect access forbidden. Check if 2FA is enabled: {http_err}")
            else:
                raise ValueError(f"Garmin Connect HTTP error: {http_err}")
        except Exception as exc:
            raise ValueError(f"Garmin Connect login failed: {exc}")
    
    async def connect(self, email: str, password: str, mfa_callback: Optional[Callable[[], str]] = None) -> bool:
        """Connect to Garmin with OAuth token persistence.
        
        Args:
            email: Garmin Connect email
            password: Garmin Connect password  
            mfa_callback: Optional callback for MFA codes
            
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            ValueError: On authentication failure
        """
        
        # Step 1: Try to resume existing tokens
        tokens_resumed = self._try_resume_tokens()
        
        if not tokens_resumed:
            # Step 2: Fresh login if tokens unavailable
            await asyncio.get_event_loop().run_in_executor(
                None, self._fresh_login, email, password, mfa_callback
            )
        
        # Step 3: Create Garmin client with token store
        try:
            self._client = Garmin()
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.login, str(self._token_dir)
            )
            
            logger.info("Successfully connected to Garmin Connect")
            return True
            
        except requests.HTTPError as http_err:
            status = http_err.response.status_code
            if status in (401, 403):
                logger.info(f"Token resume rejected by server ({status}). Performing fresh login")
                
                # Auto-retry with fresh login
                await asyncio.get_event_loop().run_in_executor(
                    None, self._fresh_login, email, password, mfa_callback
                )
                
                # Retry connection
                await asyncio.get_event_loop().run_in_executor(
                    None, self._client.login, str(self._token_dir)
                )
                
                logger.info("Successfully connected after fresh login")
                return True
            else:
                raise ValueError(f"Garmin Connect error ({status}): {http_err}")
                
        except Exception as exc:
            raise ValueError(f"Failed to connect to Garmin: {exc}")
    
    def get_client(self) -> Garmin:
        """Get the authenticated Garmin client."""
        if self._client is None:
            raise RuntimeError("Not connected to Garmin Connect. Call connect() first.")
        return self._client
    
    async def disconnect(self) -> None:
        """Disconnect from Garmin Connect.

        Note: The logout() method is deprecated. We simply clean up the client
        reference and let tokens expire naturally. This matches the recommended
        approach from the garminconnect library.
        """
        if self._client:
            # Simply clear the client reference - tokens will expire naturally
            self._client = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Garmin Connect."""
        return self._client is not None