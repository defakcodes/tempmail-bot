#!/usr/bin/env python3
"""
Direct runner for CLI mode
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tempmail_otp import main

if __name__ == "__main__":
    print("📧 Starting TempMail OTP CLI...")
    print("-" * 40)
    main()
