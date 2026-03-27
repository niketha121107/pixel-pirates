"""
Seed sample quiz data for the Learning Progress Graph demo.

This script adds sample quiz completions from the past 7 days,
showing how the engagement graph populates with real user scores.
"""

import json
from datetime import datetime, timedelta
from pymongo import MongoClient

# Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Sample user ID - replace with test user ID
SAMPLE_USER_ID = "test-user-001"

# Quiz data for the past 7 days with various scores
sample_quizzes = [
    # Friday - Low score
    (6, "variables_basics", 25, 40, "15% score - Low engagement"),
    # Saturday - Medium score
    (5, "loops_iteration", 30, 50, "60% score - High engagement"),
    # Sunday - No quiz
    # Monday - High score + Medium score (2 quizzes)
    (3, "functions_definition", 38, 50, "76% score - Full engagement"),
    (3, "data_structures", 20, 40, "50% score - Medium engagement"),
    # Tuesday - Perfect score
    (2, "oop_basics", 40, 40, "100% score - Full engagement"),
    # Wednesday - Low score
    (1, "error_handling", 10, 40, "25% score - Low engagement"),
    # Thursday - No quiz
]

def seed_quiz_data():
    """Insert sample quiz completion records."""
    
    today = datetime.now().date()
    inserted_count = 0
    
    for days_ago, topic_id, score, total, description in sample_quizzes:
        # Calculate the date
        quiz_date = today - timedelta(days=days_ago)
        
        # Create timestamp (put quizzes at different times for variety)
        time_offset = (inserted_count % 3) * 4  # 0, 4, or 8 hours
        quiz_datetime = datetime.combine(
            quiz_date,
            datetime.min.time()
        ).replace(hour=time_offset + 10)
        
        # Calculate percentage
        percentage = (score / total * 100) if total > 0 else 0
        
        # Prepare the record
        record = {
            "user_id": SAMPLE_USER_ID,
            "topic_id": topic_id,
            "quiz_score": score,
            "quiz_total": total,
            "attempts": 1,
            "status": "completed",
            "time_spent": 1800,  # 30 minutes per quiz
            "updated_at": quiz_datetime.isoformat(),
            "created_at": quiz_datetime.isoformat(),
        }
        
        # Insert or update
        db.user_progress.update_one(
            {"user_id": SAMPLE_USER_ID, "topic_id": topic_id},
            {"$set": record},
            upsert=True
        )
        
        inserted_count += 1
        print(f"[{inserted_count}] {quiz_date.strftime('%A, %b %d')} - {topic_id}")
        print(f"    Score: {score}/{total} ({percentage:.0f}%) - {description}")
    
    print(f"\nSuccessfully seeded {inserted_count} quiz records for user {SAMPLE_USER_ID}")
    print("\nEngagement Levels:")
    print("  Friday   (6 days ago): 25% score = 0.25 engagement (Low)")
    print("  Saturday (5 days ago): 60% score = 0.75 engagement (High)")
    print("  Monday   (3 days ago): 76% + 50% = 1.0 + 0.5 = 1.5 engagement (Peak)")
    print("  Tuesday  (2 days ago): 100% score = 1.0 engagement (Full)")
    print("  Wednesday (1 day ago): 25% score = 0.25 engagement (Low)")
    print("\nExpected Graph Result:")
    print("  Peak: 150% (Monday with 2 quizzes)")
    print("  Average: ~0.7 (across active days)")
    print("  Active Days: 5/7")


if __name__ == "__main__":
    try:
        seed_quiz_data()
        print("\n✓ Data seeding complete!")
        print("\nTo view the graph:")
        print(f"1. Log in with user ID: {SAMPLE_USER_ID}")
        print("2. Navigate to Progress page")
        print("3. The Learning Progress Graph should now show engagement levels")
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
