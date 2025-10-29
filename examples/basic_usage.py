#!/usr/bin/env python3
"""
Basic usage example for TempMail OTP
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tempmail_otp import TempMailGenerator

def example_basic():
    """Basic example: Generate email and wait for OTP"""
    print("🔵 Basic Example: Generate and Wait for OTP")
    print("-" * 50)
    
    # Initialize generator
    gen = TempMailGenerator(provider='auto')
    
    # Generate email
    email = gen.generate_random_email()
    print(f"✅ Email generated: {email}")
    print("\n📝 Use this email for registration")
    print("⏳ Waiting for OTP (timeout: 60 seconds)...")
    
    # Wait for OTP
    otp = gen.wait_for_otp(timeout=60, check_interval=3)
    
    if otp:
        print(f"\n🎉 OTP received: {otp}")
    else:
        print("\n❌ No OTP received within timeout")
    
    return email, otp


def example_manual_check():
    """Example: Manual inbox checking"""
    print("\n🔵 Manual Check Example")
    print("-" * 50)
    
    gen = TempMailGenerator()
    email = gen.generate_random_email()
    print(f"✅ Email: {email}")
    
    # Manual check
    print("\n📬 Checking inbox manually...")
    messages = gen.check_inbox()
    
    if messages:
        print(f"📨 Found {len(messages)} messages:")
        for msg in messages:
            print(f"  - From: {msg.get('from', 'Unknown')}")
            print(f"    Subject: {msg.get('subject', 'No subject')}")
    else:
        print("📭 Inbox is empty")
    
    return messages


def example_custom_otp():
    """Example: Custom OTP extraction"""
    print("\n🔵 Custom OTP Extraction Example")
    print("-" * 50)
    
    gen = TempMailGenerator()
    
    # Test texts
    test_texts = [
        "Your verification code is 123456",
        "OTP: 9876",
        "Use code 555444 to verify",
        "PIN: 1234"
    ]
    
    for text in test_texts:
        # Try different OTP lengths
        for length in [4, 6]:
            otp = gen.extract_otp(text, otp_length=length)
            if otp:
                print(f"✅ Text: '{text}' -> OTP: {otp}")
                break
        else:
            print(f"❌ Text: '{text}' -> No OTP found")


if __name__ == "__main__":
    print("=" * 60)
    print("TEMPMAIL OTP - USAGE EXAMPLES")
    print("=" * 60)
    
    # Run examples
    example_basic()
    example_manual_check()
    example_custom_otp()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
