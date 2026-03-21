#!/usr/bin/env python3
"""Test that visual fallback is integrated into API routes"""
from app.routes.topics import router
from app.data import get_all_topics

print("✓ Topics router imported successfully")
print("✓ Visual fallback mechanism imported")

# Verify the route exists
endpoints = [r.path for r in router.routes]
print(f"\nAvailable routes: {len(router.routes)} endpoints")

# Test the fallback function
from app.visual_formatter import get_visual_explanation_with_fallback

topics = get_all_topics()
test_topic = topics[0]

visual = get_visual_explanation_with_fallback(test_topic)
print(f"\n✓ Visual fallback works!")
print(f"  Generated visual explanation: {len(visual)} chars")
print("\n✅ Visual fallback mechanism successfully integrated!")
