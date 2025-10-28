"""
Monkey patch for bcrypt to automatically handle the 72-byte limit.
This patch ensures passwords longer than 72 bytes are properly truncated
before being passed to bcrypt.
"""

import passlib.hash
from passlib.hash import bcrypt

# Store the original bcrypt function
original_bcrypt = bcrypt

def patched_bcrypt(password, *args, **kwargs):
    """
    Patched version of passlib's bcrypt that handles the 72-byte limit
    by truncating passwords automatically.
    """
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes
            truncated_bytes = password_bytes[:72]
            
            # Make sure we end at a valid UTF-8 character boundary
            while truncated_bytes and truncated_bytes[-1] & 0x80 and not truncated_bytes[-1] & 0x40:
                truncated_bytes = truncated_bytes[:-1]
                
            # Decode back to string
            password = truncated_bytes.decode('utf-8', errors='replace')
    
    # Call the original bcrypt with the truncated password
    return original_bcrypt(password, *args, **kwargs)

# Apply the patch
passlib.hash.bcrypt = patched_bcrypt

def apply_patch():
    """
    Apply the bcrypt patch if not already applied.
    This function is called during application startup.
    """
    # The patch is already applied when this module is imported
    return True
