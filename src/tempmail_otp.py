import requests
import time
import re
import random
import string
import json
from typing import Optional, List, Dict, Tuple
from datetime import datetime


class MailTmGenerator:
    """Class untuk generate tempmail menggunakan Mail.tm API"""
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = 10
    
    def __init__(self):
        """Initialize Mail.tm Generator"""
        self.base_url = "https://api.mail.tm"
        self.email = None
        self.password = None
        self.token = None
        self.account_id = None
        self.session = requests.Session()
        self.session.timeout = self.REQUEST_TIMEOUT
        
    def generate_random_email(self) -> str:
        """Generate random temporary email address"""
        # Get available domains
        domains = self._get_available_domains()
        if not domains:
            raise Exception("Tidak dapat mendapatkan domain email")
        
        # Generate random login
        login_length = random.randint(8, 12)
        login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=login_length))
        
        # Choose first active domain
        domain = domains[0]
        
        # Create email and password
        self.email = f"{login}@{domain}"
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # Register account
        if self._create_account():
            print(f"✅ Email berhasil dibuat: {self.email}")
            return self.email
        else:
            raise Exception("Gagal membuat account email")
    
    def _get_available_domains(self) -> List[str]:
        """Get list of available email domains from Mail.tm"""
        try:
            response = self.session.get(f"{self.base_url}/domains", timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            # Extract domain names
            domains = []
            if 'hydra:member' in data:
                for domain_obj in data['hydra:member']:
                    if domain_obj.get('isActive', False):
                        domains.append(domain_obj['domain'])
            
            return domains
        except Exception as e:
            print(f"❌ Error mendapatkan domain Mail.tm: {e}")
            return []
    
    def _create_account(self) -> bool:
        """Create account on Mail.tm"""
        try:
            # Register account
            register_data = {
                "address": self.email,
                "password": self.password
            }
            
            response = self.session.post(
                f"{self.base_url}/accounts",
                json=register_data,
                timeout=self.REQUEST_TIMEOUT
            )
            
            if response.status_code in [200, 201]:
                account_data = response.json()
                self.account_id = account_data.get('id')
                
                # Login to get token
                login_response = self.session.post(
                    f"{self.base_url}/token",
                    json=register_data,
                    timeout=self.REQUEST_TIMEOUT
                )
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.token = token_data.get('token')
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error creating Mail.tm account: {e}")
            return False
    
    def check_inbox(self) -> List[Dict]:
        """Check inbox for new messages"""
        if not self.token:
            raise Exception("Email belum di-generate atau login gagal")
        
        try:
            response = self.session.get(f"{self.base_url}/messages", timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            messages = []
            if 'hydra:member' in data:
                for msg in data['hydra:member']:
                    messages.append({
                        'id': msg.get('id'),
                        'from': msg.get('from', {}).get('address', 'Unknown'),
                        'subject': msg.get('subject', 'No subject'),
                        'date': msg.get('createdAt', 'Unknown'),
                        'intro': msg.get('intro', '')
                    })
            
            return messages
        except Exception as e:
            print(f"❌ Error checking Mail.tm inbox: {e}")
            return []
    
    def get_message_content(self, message_id: str) -> Dict:
        """Get full content of a specific message"""
        if not self.token:
            raise Exception("Email belum di-generate atau login gagal")
        
        try:
            response = self.session.get(f"{self.base_url}/messages/{message_id}", timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            msg = response.json()
            
            return {
                'body': msg.get('text', ''),
                'htmlBody': ''.join(msg.get('html', [])) if msg.get('html') else '',
                'subject': msg.get('subject', ''),
                'from': msg.get('from', {}).get('address', 'Unknown')
            }
        except Exception as e:
            print(f"❌ Error membaca pesan Mail.tm: {e}")
            return {}


class GuerrillaMailGenerator:
    """Class untuk generate tempmail menggunakan Guerrilla Mail API"""
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = 10
    
    def __init__(self):
        """Initialize Guerrilla Mail Generator"""
        self.base_url = "http://api.guerrillamail.com/ajax.php"
        self.email = None
        self.sid_token = None
        self.session = requests.Session()
        
    def generate_random_email(self) -> str:
        """Generate random temporary email address"""
        try:
            # Get email address from GuerrillaMail
            params = {
                'f': 'get_email_address',
                'ip': '127.0.0.1',
                'agent': 'Mozilla/5.0',
                'lang': 'en'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            self.email = data.get('email_addr')
            self.sid_token = data.get('sid_token', '')
            
            # Store session cookie if present
            if 'PHPSESSID' in response.cookies:
                self.session.cookies.update({'PHPSESSID': response.cookies['PHPSESSID']})
            
            if self.email:
                print(f"✅ Email berhasil dibuat: {self.email}")
                return self.email
            else:
                raise Exception("Tidak dapat membuat email")
                
        except Exception as e:
            print(f"❌ Error generating GuerrillaMail: {e}")
            raise e
    
    def check_inbox(self) -> List[Dict]:
        """Check inbox for new messages"""
        if not self.email:
            raise Exception("Email belum di-generate")
        
        try:
            params = {
                'f': 'get_email_list',
                'ip': '127.0.0.1',
                'agent': 'Mozilla/5.0',
                'offset': '0'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            messages = []
            if 'list' in data:
                for msg in data['list']:
                    messages.append({
                        'id': msg.get('mail_id'),
                        'from': msg.get('mail_from', 'Unknown'),
                        'subject': msg.get('mail_subject', 'No subject'),
                        'date': msg.get('mail_date', 'Unknown'),
                        'excerpt': msg.get('mail_excerpt', '')
                    })
            
            return messages
        except Exception as e:
            print(f"❌ Error checking GuerrillaMail inbox: {e}")
            return []
    
    def get_message_content(self, message_id: str) -> Dict:
        """Get full content of a specific message"""
        if not self.email:
            raise Exception("Email belum di-generate")
        
        try:
            params = {
                'f': 'fetch_email',
                'ip': '127.0.0.1', 
                'agent': 'Mozilla/5.0',
                'email_id': message_id
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            msg = response.json()
            
            return {
                'body': msg.get('mail_body_text', ''),
                'htmlBody': msg.get('mail_body', ''),
                'subject': msg.get('mail_subject', ''),
                'from': msg.get('mail_from', 'Unknown')
            }
        except Exception as e:
            print(f"❌ Error membaca pesan GuerrillaMail: {e}")
            return {}


class TempMailGenerator:
    """Main class yang menggunakan multiple API providers"""
    
    def __init__(self, provider='auto'):
        """Initialize TempMail Generator
        
        Args:
            provider: 'mailtm', 'guerrilla', or 'auto' (tries all)
        """
        self.provider = provider
        self.generator = None
        self.email = None
        
    def generate_random_email(self) -> str:
        """Generate random temporary email address"""
        if self.provider == 'auto':
            # Try Mail.tm first
            try:
                print("📧 Mencoba Mail.tm API...")
                self.generator = MailTmGenerator()
                self.email = self.generator.generate_random_email()
                return self.email
            except Exception as e1:
                print(f"⚠️ Mail.tm gagal: {e1}")
                
                # Try GuerrillaMail
                try:
                    print("📧 Mencoba GuerrillaMail API...")
                    self.generator = GuerrillaMailGenerator()
                    self.email = self.generator.generate_random_email()
                    return self.email
                except Exception as e2:
                    print(f"⚠️ GuerrillaMail gagal: {e2}")
                    raise Exception("Semua provider email gagal")
                    
        elif self.provider == 'mailtm':
            self.generator = MailTmGenerator()
            self.email = self.generator.generate_random_email()
            return self.email
            
        elif self.provider == 'guerrilla':
            self.generator = GuerrillaMailGenerator()
            self.email = self.generator.generate_random_email()
            return self.email
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def check_inbox(self) -> List[Dict]:
        """Check inbox for new messages"""
        if not self.generator:
            raise Exception("Email belum di-generate")
        return self.generator.check_inbox()
    
    def get_message_content(self, message_id) -> Dict:
        """Get full content of a specific message"""
        if not self.generator:
            raise Exception("Email belum di-generate")
        return self.generator.get_message_content(message_id)
    
    def extract_otp(self, text: str, otp_length: int = 6) -> Optional[str]:
        """Extract OTP code from text using various patterns"""
        # Common OTP patterns
        patterns = [
            r'\b(\d{' + str(otp_length) + r'})\b',  # Exact digit length
            r'code[:\s]+(\d{4,8})',  # "code: 123456"
            r'OTP[:\s]+(\d{4,8})',  # "OTP: 123456"
            r'verification code[:\s]+(\d{4,8})',  # "verification code: 123456"
            r'código[:\s]+(\d{4,8})',  # Spanish
            r'kode[:\s]+(\d{4,8})',  # Indonesian
            r':\s*(\d{4,8})\s*',  # Any number after colon
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def wait_for_otp(self, timeout: int = 120, check_interval: int = 5, otp_length: int = 6) -> Optional[str]:
        """Wait for OTP in inbox with timeout"""
        if not self.email:
            raise Exception("Email belum di-generate")
        
        print(f"⏳ Menunggu OTP di {self.email}...")
        print(f"   Timeout: {timeout} detik, Check interval: {check_interval} detik")
        
        start_time = time.time()
        checked_messages = set()
        
        while time.time() - start_time < timeout:
            messages = self.check_inbox()
            
            for msg in messages:
                msg_id = msg.get('id')
                
                # Skip if already checked
                if msg_id in checked_messages:
                    continue
                
                checked_messages.add(msg_id)
                
                # Get full message content
                full_msg = self.get_message_content(msg_id)
                
                if full_msg:
                    print(f"\n📧 Pesan baru dari: {msg.get('from', 'Unknown')}")
                    print(f"   Subject: {msg.get('subject', 'No subject')}")
                    print(f"   Time: {msg.get('date', 'Unknown')}")
                    
                    # Try to extract OTP from subject
                    subject = msg.get('subject', '')
                    otp = self.extract_otp(subject, otp_length)
                    
                    # If not found in subject, check body
                    if not otp:
                        body = full_msg.get('body', '')
                        otp = self.extract_otp(body, otp_length)
                    
                    # If not found in text body, check HTML body
                    if not otp:
                        html_body = full_msg.get('htmlBody', '')
                        # Remove HTML tags
                        clean_text = re.sub('<.*?>', ' ', html_body)
                        otp = self.extract_otp(clean_text, otp_length)
                    
                    if otp:
                        print(f"\n🎉 OTP ditemukan: {otp}")
                        return otp
                    else:
                        print("   ⚠️ OTP tidak ditemukan dalam pesan ini")
            
            # Wait before next check
            time.sleep(check_interval)
            elapsed = int(time.time() - start_time)
            print(f"   Checking... ({elapsed}/{timeout} detik)", end='\r')
        
        print(f"\n⏱️ Timeout! Tidak ada OTP dalam {timeout} detik")
        return None
    
    def get_all_messages_details(self) -> List[Dict]:
        """Get all messages with full details"""
        messages = self.check_inbox()
        detailed_messages = []
        
        for msg in messages:
            msg_id = msg.get('id')
            full_msg = self.get_message_content(msg_id)
            if full_msg:
                detailed_messages.append({
                    'from': msg.get('from'),
                    'subject': msg.get('subject'),
                    'date': msg.get('date'),
                    'body': full_msg.get('body', ''),
                    'html': full_msg.get('htmlBody', '')
                })
        
        return detailed_messages



def main():
    """Main function untuk demo"""
    print("=" * 60)
    print("TEMPMAIL OTP RECEIVER - AUTO MODE")
    print("=" * 60)
    
    # Initialize generator
    generator = TempMailGenerator()
    
    # Generate new email
    email = generator.generate_random_email()
    print(f"\n📧 Gunakan email ini untuk registrasi: {email}")
    print("=" * 60)
    
    # AUTO WAIT FOR OTP
    print("\n🔄 Mode Auto: Langsung menunggu OTP...")
    otp = generator.wait_for_otp(timeout=180, check_interval=3)  # 3 menit timeout
    
    if otp:
        print(f"\n✅ OTP BERHASIL DITERIMA: {otp}")
        print("=" * 60)
        print(f"Email: {email}")
        print(f"OTP Code: {otp}")
        print("=" * 60)
    else:
        print("\n❌ Timeout! OTP tidak diterima dalam 3 menit")
    
    # Ask if user wants to continue with menu
    continue_choice = input("\n💡 Lanjut ke menu interaktif? (y/n): ").strip().lower()
    
    if continue_choice != 'y':
        print("\n👋 Program selesai!")
        return
    
    # Menu
    while True:
        print("\n📋 MENU:")
        print("1. Generate email baru + Auto wait OTP")
        print("2. Check inbox manual")
        print("3. Wait untuk OTP lagi")
        print("4. Lihat semua pesan detail")
        print("5. Custom OTP wait (input timeout)")
        print("6. Keluar")
        
        choice = input("\nPilih opsi (1-6): ").strip()
        
        if choice == "1":
            email = generator.generate_random_email()
            print(f"\n📧 Email baru: {email}")
            # Auto wait OTP after generate
            otp = generator.wait_for_otp(timeout=180, check_interval=3)
            if otp:
                print(f"\n✅ OTP berhasil diterima: {otp}")
            else:
                print("\n❌ OTP tidak diterima")
            
        elif choice == "2":
            print("\n📬 Checking inbox...")
            messages = generator.check_inbox()
            if messages:
                print(f"📨 Ditemukan {len(messages)} pesan:")
                for msg in messages:
                    print(f"   - From: {msg.get('from', 'Unknown')}")
                    print(f"     Subject: {msg.get('subject', 'No subject')}")
                    print(f"     Date: {msg.get('date', 'Unknown')}")
            else:
                print("📭 Inbox kosong")
                
        elif choice == "3":
            otp = generator.wait_for_otp(timeout=180, check_interval=3)
            if otp:
                print(f"\n✅ OTP berhasil diterima: {otp}")
            else:
                print("\n❌ OTP tidak diterima")
                
        elif choice == "4":
            print("\n📚 Mendapatkan detail semua pesan...")
            messages = generator.get_all_messages_details()
            if messages:
                for i, msg in enumerate(messages, 1):
                    print(f"\n--- Pesan {i} ---")
                    print(f"From: {msg['from']}")
                    print(f"Subject: {msg['subject']}")
                    print(f"Date: {msg['date']}")
                    print(f"Body: {msg['body'][:200]}..." if len(msg['body']) > 200 else f"Body: {msg['body']}")
            else:
                print("📭 Tidak ada pesan")
                
        elif choice == "5":
            try:
                timeout = int(input("Masukkan timeout (detik): "))
                otp_len = int(input("Masukkan panjang OTP (default 6): ") or "6")
                otp = generator.wait_for_otp(timeout=timeout, otp_length=otp_len)
                if otp:
                    print(f"\n✅ OTP berhasil diterima: {otp}")
                else:
                    print("\n❌ OTP tidak diterima")
            except ValueError:
                print("❌ Input tidak valid")
                
        elif choice == "6":
            print("\n👋 Terima kasih! Goodbye!")
            break
            
        else:
            print("❌ Pilihan tidak valid")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
