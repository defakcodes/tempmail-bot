#!/usr/bin/env python3
"""
Integration example: How to use in your own projects
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tempmail_otp import TempMailGenerator
import time

class RegistrationAutomation:
    """Example class for automated registration"""
    
    def __init__(self):
        self.email_gen = TempMailGenerator(provider='auto')
        self.current_email = None
        
    def register_account(self, website_name="Example Site"):
        """Simulate account registration flow"""
        print(f"\n🚀 Automating registration for: {website_name}")
        print("=" * 50)
        
        # Step 1: Generate email
        self.current_email = self.email_gen.generate_random_email()
        print(f"1️⃣ Email generated: {self.current_email}")
        
        # Step 2: Simulate form filling
        print(f"2️⃣ Filling registration form...")
        time.sleep(1)  # Simulate form filling
        print("   ✅ Form submitted with email")
        
        # Step 3: Wait for OTP
        print("3️⃣ Waiting for OTP email...")
        otp = self.email_gen.wait_for_otp(timeout=120, check_interval=3)
        
        if otp:
            print(f"4️⃣ OTP received: {otp}")
            
            # Step 4: Submit OTP
            print(f"5️⃣ Submitting OTP...")
            time.sleep(1)  # Simulate OTP submission
            print("   ✅ OTP verified!")
            
            # Step 5: Complete registration
            print("6️⃣ Registration completed successfully!")
            return True
        else:
            print("❌ OTP not received - Registration failed")
            return False
    
    def get_all_messages(self):
        """Get all messages for current email"""
        if not self.current_email:
            print("❌ No active email session")
            return []
        
        messages = self.email_gen.check_inbox()
        detailed = []
        
        for msg in messages:
            msg_details = self.email_gen.get_message_content(msg.get('id'))
            if msg_details:
                detailed.append(msg_details)
        
        return detailed


class BatchRegistration:
    """Example: Register multiple accounts"""
    
    def __init__(self):
        self.accounts = []
    
    def register_batch(self, count=3):
        """Register multiple accounts"""
        print(f"\n🔄 Batch Registration: {count} accounts")
        print("=" * 50)
        
        for i in range(count):
            print(f"\n📌 Account {i+1}/{count}")
            print("-" * 30)
            
            automation = RegistrationAutomation()
            success = automation.register_account(f"Site-{i+1}")
            
            if success:
                self.accounts.append({
                    'email': automation.current_email,
                    'site': f"Site-{i+1}",
                    'status': 'active'
                })
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 BATCH REGISTRATION SUMMARY")
        print("=" * 50)
        print(f"Total attempts: {count}")
        print(f"Successful: {len(self.accounts)}")
        print(f"Failed: {count - len(self.accounts)}")
        
        if self.accounts:
            print("\n✅ Registered Accounts:")
            for acc in self.accounts:
                print(f"  - {acc['site']}: {acc['email']}")


def example_with_retry():
    """Example with retry logic"""
    print("\n🔄 Example with Retry Logic")
    print("=" * 50)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            gen = TempMailGenerator(provider='auto')
            email = gen.generate_random_email()
            print(f"✅ Attempt {retry_count + 1}: Email created: {email}")
            
            # Simulate OTP wait
            print("⏳ Waiting for OTP...")
            otp = gen.wait_for_otp(timeout=30)
            
            if otp:
                print(f"🎉 Success! OTP: {otp}")
                break
            else:
                print(f"⚠️ No OTP received, retrying...")
                retry_count += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            retry_count += 1
            time.sleep(2)
    
    if retry_count >= max_retries:
        print("❌ Max retries reached. Operation failed.")


if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRATION EXAMPLES")
    print("=" * 60)
    
    # Example 1: Single registration
    print("\n1️⃣ SINGLE REGISTRATION EXAMPLE")
    automation = RegistrationAutomation()
    automation.register_account("MyWebsite")
    
    # Example 2: Batch registration
    print("\n2️⃣ BATCH REGISTRATION EXAMPLE")
    batch = BatchRegistration()
    batch.register_batch(2)
    
    # Example 3: With retry logic
    print("\n3️⃣ RETRY LOGIC EXAMPLE")
    example_with_retry()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
