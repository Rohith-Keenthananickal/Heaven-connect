#!/usr/bin/env python3
"""
Simple Zoho SMTP test without Unicode characters
"""

import smtplib
import ssl

def test_zoho_smtp():
    """Simple Zoho SMTP test"""
    print("Zoho SMTP Test")
    print("=" * 30)
    
    # Configuration
    smtp_server = "smtp.zoho.com"
    smtp_port = 587
    email = "admin@triphavenco.com"
    password = "BDyi01JH5S50"
    
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print()
    
    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        print("SUCCESS: Connected to SMTP server")
        
        print("Starting TLS...")
        server.starttls()
        print("SUCCESS: TLS started")
        
        print("Authenticating...")
        server.login(email, password)
        print("SUCCESS: Authentication successful!")
        
        server.quit()
        print("SUCCESS: All tests passed!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: Authentication failed - {e}")
        print("\nThis means:")
        print("1. Wrong email or password")
        print("2. Account not configured for SMTP")
        print("3. 2FA not enabled")
        print("4. App Password not generated correctly")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_zoho_smtp()

