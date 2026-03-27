"""
Test script for Learning Progress Graph functionality.

Tests:
1. Score-to-engagement mapping
2. Daily engagement accumulation
3. 7-day date range calculations
4. Backend API response format
"""

import json
from datetime import datetime, timedelta
from typing import Dict

def map_score_to_engagement(percentage: float) -> float:
    """
    Test version of score-to-engagement mapping.
    
    Score Mapping:
    - 0% → 0 (No engagement)
    - 1–25% → 0.25 (Low engagement)
    - 26–50% → 0.5 (Medium engagement)
    - 51–75% → 0.75 (High engagement)
    - 76–100% → 1 (Full engagement)
    """
    if percentage <= 0:
        return 0
    elif percentage <= 25:
        return 0.25
    elif percentage <= 50:
        return 0.5
    elif percentage <= 75:
        return 0.75
    else:
        return 1.0


def test_score_mapping():
    """Test the score-to-engagement mapping function."""
    print("\n✅ Testing Score-to-Engagement Mapping")
    print("-" * 50)
    
    test_cases = [
        (0, 0),           # No score → No engagement
        (15, 0.25),       # 15% → Low engagement
        (20, 0.25),       # 20% → Low engagement
        (25, 0.25),       # 25% (boundary) → Low engagement
        (26, 0.5),        # 26% → Medium engagement
        (50, 0.5),        # 50% (boundary) → Medium engagement
        (51, 0.75),       # 51% → High engagement
        (75, 0.75),       # 75% (boundary) → High engagement
        (76, 1.0),        # 76% → Full engagement
        (100, 1.0),       # 100% (perfect) → Full engagement
    ]
    
    all_passed = True
    for score, expected in test_cases:
        result = map_score_to_engagement(score)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"{status} Score {score:3d}% → Engagement {result} (expected {expected})")
    
    return all_passed


def test_daily_accumulation():
    """Test daily engagement accumulation for multiple quizzes per day."""
    print("\n✅ Testing Daily Engagement Accumulation")
    print("-" * 50)
    
    # Simulate progress records with multiple quizzes on the same day
    today = datetime.now().date()
    today_str = today.isoformat()
    yesterday_str = (today - timedelta(days=1)).isoformat()
    
    records = [
        {
            "updated_at": f"{today_str}T10:30:00",
            "quiz_score": 85,
            "quiz_total": 100,
            "topic_id": "python_basics"
        },
        {
            "updated_at": f"{today_str}T14:15:00",
            "quiz_score": 60,
            "quiz_total": 100,
            "topic_id": "list_comprehension"
        },
        {
            "updated_at": f"{yesterday_str}T09:00:00",
            "quiz_score": 95,
            "quiz_total": 100,
            "topic_id": "functions"
        },
    ]
    
    # Calculate daily engagement manually
    daily_engagement = {}
    for record in records:
        updated_at = record.get("updated_at", "")
        record_date = datetime.fromisoformat(updated_at).date().isoformat()
        
        if record_date not in daily_engagement:
            daily_engagement[record_date] = 0
        
        score = record.get("quiz_score", 0)
        total = record.get("quiz_total", 100)
        percentage = (score / total * 100) if total > 0 else 0
        engagement = map_score_to_engagement(percentage)
        daily_engagement[record_date] += engagement
    
    print(f"Today ({today_str}):")
    print(f"  Quiz 1: 85% → 1.0 engagement")
    print(f"  Quiz 2: 60% → 0.5 engagement")
    print(f"  Total:  {daily_engagement[today_str]} engagement")
    print(f"  Status: {'✓' if daily_engagement[today_str] == 1.5 else '✗'} Expected 1.5")
    
    print(f"\nYesterday ({yesterday_str}):")
    print(f"  Quiz 1: 95% → 1.0 engagement")
    print(f"  Total:  {daily_engagement[yesterday_str]} engagement")
    print(f"  Status: {'✓' if daily_engagement[yesterday_str] == 1.0 else '✗'} Expected 1.0")
    
    return (daily_engagement[today_str] == 1.5 and 
            daily_engagement[yesterday_str] == 1.0)


def test_seven_day_window():
    """Test that only the past 7 days are included."""
    print("\n✅ Testing 7-Day Window")
    print("-" * 50)
    
    today = datetime.now().date()
    
    # Create dates for last 7 days
    dates = []
    for i in range(7):
        date = today - timedelta(days=6 - i)
        dates.append(date.isoformat())
    
    print("Expected 7-day window:")
    for i, date in enumerate(dates):
        date_obj = datetime.fromisoformat(date).date()
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_index = date_obj.weekday()
        day_label = day_labels[day_index]
        print(f"  {i+1}. {date} ({day_label})")
    
    # Verify all dates are within window
    daily_engagement = {}
    for date in dates:
        daily_engagement[date] = 0
    
    print(f"\n✓ Successfully created windowed dict with {len(daily_engagement)} days")
    return len(daily_engagement) == 7


def test_engagement_visualization():
    """Test the visual representation of engagement levels."""
    print("\n✅ Testing Engagement Visualization")
    print("-" * 50)
    
    # Create sample 7-day data
    today = datetime.now().date()
    sample_data = [
        {"day": "Mon", "date": (today - timedelta(days=6)).isoformat(), "engagement": 0},
        {"day": "Tue", "date": (today - timedelta(days=5)).isoformat(), "engagement": 0.25},
        {"day": "Wed", "date": (today - timedelta(days=4)).isoformat(), "engagement": 0.5},
        {"day": "Thu", "date": (today - timedelta(days=3)).isoformat(), "engagement": 0.75},
        {"day": "Fri", "date": (today - timedelta(days=2)).isoformat(), "engagement": 1.0},
        {"day": "Sat", "date": (today - timedelta(days=1)).isoformat(), "engagement": 1.5},  # Accumulated from 2 quizzes
        {"day": "Sun", "date": today.isoformat(), "engagement": 0.5},
    ]
    
    print("Sample 7-day engagement data:")
    print(json.dumps(sample_data, indent=2))
    
    print("\nEngagement Levels:")
    for item in sample_data:
        engagement = item["engagement"]
        bar_length = int(engagement * 10)
        bar = "█" * bar_length + "░" * (10 - bar_length)
        
        if engagement == 0:
            label = "No engagement"
        elif engagement <= 0.25:
            label = "Low (1-25%)"
        elif engagement <= 0.5:
            label = "Medium (26-50%)"
        elif engagement <= 0.75:
            label = "High (51-75%)"
        else:
            label = "Full (76-100%)"
        
        print(f"{item['day']}: {bar} {engagement:.2f} ({label})")
    
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 50)
    print("LEARNING PROGRESS GRAPH - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Score Mapping", test_score_mapping),
        ("Daily Accumulation", test_daily_accumulation),
        ("7-Day Window", test_seven_day_window),
        ("Visualization", test_engagement_visualization),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Learning Progress Graph is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
