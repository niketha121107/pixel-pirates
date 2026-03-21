#!/usr/bin/env python3
"""Check available mock users"""

import sys
sys.path.insert(0, ".")

from app.data import MOCK_USERS, get_mock_data

print("Available Test Users")
print("=" * 60)

get_mock_data()

if MOCK_USERS:
    print(f"\nFound {len(MOCK_USERS)} users:\n")
    for user in MOCK_USERS[:5]:
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Password: {user.get('originalPassword', 'N/A')}")
        print()
else:
    print("No mock users found!")

print("=" * 60)
