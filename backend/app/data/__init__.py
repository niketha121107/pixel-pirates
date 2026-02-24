from typing import List, Dict, Any
from app.models import *
from app.core.auth import hash_password
import json
from datetime import datetime, date

# Mock database - In production, this would be replaced with actual database calls
MOCK_USERS = {
    "user-1": {
        "id": "user-1",
        "name": "Alex Johnson",
        "email": "alex@edutwin.com",
        "password": "password123",  # Will be hashed on initialization
        "completedTopics": ["topic-1"],
        "pendingTopics": ["topic-3", "topic-4", "topic-5"],
        "inProgressTopics": ["topic-2"],
        "videosWatched": [
            {
                "id": "vid-1",
                "title": "Python Loops Explained",
                "language": "Python",
                "youtubeId": "dQw4w9WgXcQ",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
                "duration": "12:30",
                "watchedAt": "2026-02-20",
                "timeWatched": "10:15"
            }
        ],
        "totalScore": 85,
        "rank": 3,
        "preferredStyle": "visual",
        "confusionCount": 0
    },
    "user-2": {
        "id": "user-2",
        "name": "Sarah Johnson",
        "email": "sarah@edutwin.com",
        "password": "password456",  # Will be hashed on initialization
        "completedTopics": ["topic-1", "topic-2"],
        "pendingTopics": ["topic-5"],
        "inProgressTopics": ["topic-3", "topic-4"],
        "videosWatched": [],
        "totalScore": 95,
        "rank": 1,
        "preferredStyle": "logical",
        "confusionCount": 0
    },
    "user-3": {
        "id": "user-3",
        "name": "Michael Chen",
        "email": "michael@edutwin.com",
        "password": "password789",  # Will be hashed on initialization
        "completedTopics": ["topic-1"],
        "pendingTopics": ["topic-4", "topic-5"],
        "inProgressTopics": ["topic-2", "topic-3"],
        "videosWatched": [],
        "totalScore": 92,
        "rank": 2,
        "preferredStyle": "simplified",
        "confusionCount": 0
    }
}

# Track if passwords have been hashed
_passwords_hashed = False

def initialize_data():
    """Initialize mock data with hashed passwords"""
    global _passwords_hashed
    if not _passwords_hashed:
        for user_id, user in MOCK_USERS.items():
            if not user["password"].startswith("$2b$"):  # Not already hashed
                user["password"] = hash_password(user["password"])
        _passwords_hashed = True
        print("✅ Mock data initialized with hashed passwords")

MOCK_TOPICS = {
    "topic-1": {
        "id": "topic-1",
        "language": "Python",
        "topicName": "Python Loops",
        "difficulty": "Beginner",
        "overview": "Loops are fundamental constructs in Python that allow you to execute a block of code repeatedly.",
        "explanations": [
            {
                "style": "visual",
                "title": "Visual Explanation",
                "icon": "🎨",
                "content": "Imagine a conveyor belt in a factory. Each item on the belt gets the same processing."
            },
            {
                "style": "simplified",
                "title": "Simplified Explanation", 
                "icon": "📝",
                "content": "A loop simply means 'do this thing again and again.'"
            }
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What keyword starts a for loop in Python?",
                "options": ["for", "loop", "repeat", "iterate"],
                "correctAnswer": 0
            },
            {
                "id": "q2",
                "question": "What does range(5) return?",
                "options": ["1 to 5", "0 to 5", "0 to 4", "1 to 4"],
                "correctAnswer": 2
            }
        ],
        "recommendedVideos": [
            {
                "id": "vid-1",
                "title": "Python Loops Explained",
                "language": "Python",
                "youtubeId": "6iF8Xb7Z3wQ",
                "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg",
                "duration": "12:30"
            }
        ]
    },
    "topic-2": {
        "id": "topic-2",
        "language": "Java",
        "topicName": "Java OOP Basics",
        "difficulty": "Intermediate",
        "overview": "Object-oriented programming fundamentals in Java.",
        "explanations": [
            {
                "style": "logical",
                "title": "Logical Explanation",
                "icon": "🧠",
                "content": "OOP organizes code into reusable objects with properties and methods."
            }
        ],
        "quiz": [
            {
                "id": "q3",
                "question": "What is encapsulation?",
                "options": ["Hiding data", "Inheritance", "Polymorphism", "Abstraction"],
                "correctAnswer": 0
            }
        ],
        "recommendedVideos": []
    }
}

MOCK_LEADERBOARD = [
    {"rank": 1, "userId": "user-2", "name": "Sarah Johnson", "score": 95, "topicsCompleted": 8, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"},
    {"rank": 2, "userId": "user-3", "name": "Michael Chen", "score": 92, "topicsCompleted": 7, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Michael"},
    {"rank": 3, "userId": "user-1", "name": "Alex Johnson", "score": 85, "topicsCompleted": 5, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"},
]

MOCK_SEARCH_HISTORY = {
    "user-1": [
        {"query": "Python generators", "time": "2 hours ago"},
        {"query": "Binary search tree", "time": "5 hours ago"},
        {"query": "SQL joins explained", "time": "Yesterday"}
    ]
}

def get_mock_data():
    return {
        "users": MOCK_USERS,
        "topics": MOCK_TOPICS,
        "leaderboard": MOCK_LEADERBOARD,
        "search_history": MOCK_SEARCH_HISTORY
    }

def get_user_by_id(user_id: str):
    return MOCK_USERS.get(user_id)

def get_user_by_email(email: str):
    for user in MOCK_USERS.values():
        if user["email"] == email:
            return user
    return None

def get_topic_by_id(topic_id: str):
    return MOCK_TOPICS.get(topic_id)

def get_all_topics():
    return list(MOCK_TOPICS.values())

def get_leaderboard():
    return MOCK_LEADERBOARD

def get_user_search_history(user_id: str):
    return MOCK_SEARCH_HISTORY.get(user_id, [])

def add_search_query(user_id: str, query: str):
    if user_id not in MOCK_SEARCH_HISTORY:
        MOCK_SEARCH_HISTORY[user_id] = []
    MOCK_SEARCH_HISTORY[user_id].insert(0, {"query": query, "time": "Just now"})
    # Keep only last 10 searches
    MOCK_SEARCH_HISTORY[user_id] = MOCK_SEARCH_HISTORY[user_id][:10]

def update_user_topic_progress(user_id: str, topic_id: str, status: str, score: int = None):
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    
    # Remove from other lists
    lists_to_clean = ["completedTopics", "pendingTopics", "inProgressTopics"]
    for list_name in lists_to_clean:
        if topic_id in user[list_name]:
            user[list_name].remove(topic_id)
    
    # Add to appropriate list
    if status == "completed":
        user["completedTopics"].append(topic_id)
        if score:
            user["totalScore"] += score
    elif status == "in-progress":
        user["inProgressTopics"].append(topic_id)
    else:  # pending
        user["pendingTopics"].append(topic_id)
    
    return True

def add_watched_video(user_id: str, video_data: dict):
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    
    user["videosWatched"].append(video_data)
    return True

def create_user(email: str, name: str, hashed_password: str) -> str:
    """Create a new user with hashed password"""
    user_id = f"user-{len(MOCK_USERS) + 1}"
    MOCK_USERS[user_id] = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": hashed_password,
        "completedTopics": [],
        "pendingTopics": [],
        "inProgressTopics": [],
        "videosWatched": [],
        "totalScore": 0,
        "rank": len(MOCK_USERS) + 1,
        "preferredStyle": "visual",
        "confusionCount": 0
    }
    return user_id

def update_user_password(user_id: str, hashed_password: str) -> bool:
    """Update user password with new hashed password"""
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    user["password"] = hashed_password
    return True

def user_exists(email: str) -> bool:
    """Check if user exists by email"""
    return get_user_by_email(email) is not None