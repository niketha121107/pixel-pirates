#!/usr/bin/env python3
"""Find a test user to use for API testing"""
from app.data import get_mock_data, initialize_data

# Ensure data is loaded
initialize_data()

data = get_mock_data()
users = data.get("users", {})
print(f"Total users: {len(users)}")

if users:
    print("\nAvailable users:")
    user_list = list(users.values())
    for user in user_list[:5]:
        email = user.get("email", "N/A")
        name = user.get("name", "N/A")
        print(f"  - {email} ({name})")
else:
    print("No users found in database")

# Also check if we need to register a test user
print("\nNote: May need to register a test user if none exist")
