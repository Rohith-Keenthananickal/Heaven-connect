"""
Direct implementation of bcrypt password hashing without using passlib.
This avoids the 72-byte limitation error by handling truncation directly.
"""

import bcrypt
import base64
import os

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt, handling the 72-byte limit automatically.
    
    Args:
        password: The password to hash
        
    Returns:
        Hashed password string in bcrypt format
    """
    # Convert to bytes for proper handling
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Truncate to 72 bytes if necessary
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        truncated_bytes = password_bytes[:72]
        # Ensure valid UTF-8 boundary
        while truncated_bytes and (truncated_bytes[-1] & 0x80) and not (truncated_bytes[-1] & 0x40):
            truncated_bytes = truncated_bytes[:-1]
        password_bytes = truncated_bytes
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return the hashed password as a string
    return hashed.decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash, handling the 72-byte limit.
    
    Args:
        password: The password to check
        stored_hash: The stored hash to verify against
        
    Returns:
        True if the password matches, False otherwise
    """
    # Convert inputs to bytes
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
        
    if isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode('utf-8')
    else:
        stored_hash_bytes = stored_hash
    
    # Truncate password to 72 bytes if necessary
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        truncated_bytes = password_bytes[:72]
        # Ensure valid UTF-8 boundary
        while truncated_bytes and (truncated_bytes[-1] & 0x80) and not (truncated_bytes[-1] & 0x40):
            truncated_bytes = truncated_bytes[:-1]
        password_bytes = truncated_bytes
    
    # Use bcrypt's checkpw to verify
    try:
        return bcrypt.checkpw(password_bytes, stored_hash_bytes)
    except Exception:
        # Any error means verification failed
        return False
