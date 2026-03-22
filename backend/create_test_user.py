#!/usr/bin/env python3
"""
Create a test user for development and testing
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.auth import auth_utils
from app.data import create_user, get_user_by_email, initialize_data

# Initialize data first
print("🔄 Initializing database...")
initialize_data()

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"
TEST_NAME = "Test User"

# Check if user already exists
existing_user = get_user_by_email(TEST_EMAIL)
if existing_user:
    print(f"✅ Test user already exists: {TEST_EMAIL}")
    print(f"   User ID: {existing_user.get('id')}")
    print(f"   Name: {existing_user.get('name')}")
else:
    # Create test user
    print(f"👤 Creating test user...")
    hashed_password = auth_utils.get_password_hash(TEST_PASSWORD)
    user_id = create_user(TEST_EMAIL, TEST_NAME, hashed_password)
    print(f"✅ Test user created successfully!")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Password: {TEST_PASSWORD}")
    print(f"   User ID: {user_id}")

print("\n🎯 You can now log in with:")
print(f"   Email: {TEST_EMAIL}")
print(f"   Password: {TEST_PASSWORD}")
