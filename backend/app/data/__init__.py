"""
Data Access Layer — in-memory cache backed by MongoDB.

On startup, load_from_mongodb() populates the caches.
Every write function also persists the change to MongoDB.
"""

from typing import List, Dict, Any, Optional
import logging, pymongo
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

MAX_MOCK_TEST_WARNINGS = 10
MOCK_TEST_SUSPENSION_HOURS = 2

# ── In-memory caches (populated from MongoDB on startup) ────────
MOCK_USERS: Dict[str, dict] = {}
MOCK_TOPICS: Dict[str, dict] = {}
MOCK_SEARCH_HISTORY: Dict[str, List[dict]] = {}

# ── pymongo sync client (set once) ────────────────────────────
_mongo_client: Optional[pymongo.MongoClient] = None
_db = None


def _get_db():
    """Return the pymongo (sync) database handle."""
    global _mongo_client, _db
    if _db is not None:
        return _db
    try:
        _mongo_client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        _mongo_client.admin.command("ping")
        _db = _mongo_client["pixel_pirates"]
        return _db
    except Exception as e:
        logger.warning(f"pymongo connection failed: {e}")
        return None


def _clean_doc(doc: dict) -> dict:
    """Convert MongoDB _id to id field for in-memory cache."""
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d["_id"])
        d.pop("_id", None)
    return d


# ── Startup loader ─────────────────────────────────────────────
def load_from_mongodb():
    """Load all collections into in-memory dicts. Called once at startup."""
    db = _get_db()
    if db is None:
        logger.warning("MongoDB not available — caches stay empty")
        return

    # Clear caches first so reseeds are reflected exactly.
    MOCK_USERS.clear()
    MOCK_TOPICS.clear()
    MOCK_SEARCH_HISTORY.clear()

    # Users
    for doc in db.users.find():
        user = _clean_doc(doc)
        MOCK_USERS[user["id"]] = user
    logger.info(f"Loaded {len(MOCK_USERS)} users from MongoDB")

    # Topics
    for doc in db.topics.find():
        topic = _clean_doc(doc)
        MOCK_TOPICS[topic["id"]] = topic
    logger.info(f"Loaded {len(MOCK_TOPICS)} topics from MongoDB")

    # Search history  (stored per-user)
    for doc in db.search_history.find():
        uid = doc.get("userId")
        entry = {"query": doc["query"], "time": doc.get("time", "Unknown")}
        MOCK_SEARCH_HISTORY.setdefault(uid, []).append(entry)
    logger.info(f"Loaded search history for {len(MOCK_SEARCH_HISTORY)} users from MongoDB")


def initialize_data():
    """Load data from MongoDB into in-memory caches."""
    load_from_mongodb()


def _ensure_cache_loaded(require_users: bool = False, require_topics: bool = False):
    """Lazily hydrate caches from MongoDB when required caches are empty.

    This prevents endpoints from returning empty data when the process cache
    is stale (for example, reseeding data while the API process stays alive).
    """
    need_users = require_users and not MOCK_USERS
    need_topics = require_topics and not MOCK_TOPICS
    if need_users or need_topics:
        load_from_mongodb()


# ── Read helpers ────────────────────────────────────────────────
def get_mock_data():
    return {
        "users": MOCK_USERS,
        "topics": MOCK_TOPICS,
        "search_history": MOCK_SEARCH_HISTORY,
    }


def get_user_by_id(user_id: str):
    _ensure_cache_loaded(require_users=True)
    user = MOCK_USERS.get(user_id)
    if user:
        normalize_mock_test_integrity_state(user, persist=True)
    return user


def get_user_by_email(email: str):
    _ensure_cache_loaded(require_users=True)
    for user in MOCK_USERS.values():
        if user["email"] == email:
            normalize_mock_test_integrity_state(user, persist=True)
            return user
    return None


def get_topic_by_id(topic_id: str):
    _ensure_cache_loaded(require_topics=True)
    return MOCK_TOPICS.get(topic_id)


def get_all_topics():
    _ensure_cache_loaded(require_topics=True)
    return list(MOCK_TOPICS.values())


def get_user_search_history(user_id: str):
    return MOCK_SEARCH_HISTORY.get(user_id, [])


# ── Write helpers (update cache + persist to MongoDB) ──────────
def _persist_user(user_id: str):
    """Upsert a single user to MongoDB."""
    db = _get_db()
    if db is None:
        return
    user = MOCK_USERS.get(user_id)
    if user:
        db.users.replace_one({"_id": user_id}, user, upsert=True)


def add_search_query(user_id: str, query: str):
    if user_id not in MOCK_SEARCH_HISTORY:
        MOCK_SEARCH_HISTORY[user_id] = []
    entry = {"query": query, "time": "Just now"}
    MOCK_SEARCH_HISTORY[user_id].insert(0, entry)
    MOCK_SEARCH_HISTORY[user_id] = MOCK_SEARCH_HISTORY[user_id][:10]
    # persist
    db = _get_db()
    if db is not None:
        db.search_history.insert_one({"userId": user_id, **entry})


def update_user_topic_progress(user_id: str, topic_id: str, status: str, score: int = None):
    user = MOCK_USERS.get(user_id)
    if not user:
        return False

    for list_name in ["completedTopics", "pendingTopics", "inProgressTopics"]:
        if topic_id in user[list_name]:
            user[list_name].remove(topic_id)

    if status == "completed":
        user["completedTopics"].append(topic_id)
        if score:
            user["totalScore"] = user.get("totalScore", 0) + score
            # Store per-topic quiz score
            user.setdefault("quizScores", {})[topic_id] = score
    elif status == "in-progress":
        user["inProgressTopics"].append(topic_id)
    else:
        user["pendingTopics"].append(topic_id)

    _persist_user(user_id)
    return True


def add_watched_video(user_id: str, video_data: dict):
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    user["videosWatched"].append(video_data)
    _persist_user(user_id)
    return True


def create_user(email: str, name: str, hashed_password: str) -> str:
    """Create a new user with hashed password and persist to MongoDB."""
    import uuid
    user_id = str(uuid.uuid4())

    all_topic_ids = list(MOCK_TOPICS.keys())

    new_user = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": hashed_password,
        "completedTopics": [],
        "pendingTopics": all_topic_ids,
        "inProgressTopics": [],
        "videosWatched": [],
        "totalScore": 0,
        "rank": len(MOCK_USERS) + 1,
        "preferredStyle": "visual",
        "confusionCount": 0,
        "antiCheatWarnings": 0,
        "suspendedUntil": None,
        "createdAt": datetime.now().strftime("%Y-%m-%d"),
        "quizScores": {},
        "streak": 0,
        "totalHours": 0,
        "badges": [
            {"name": "First Quiz", "icon": "🏅", "earned": False},
            {"name": "Week Streak", "icon": "🔥", "earned": False},
            {"name": "Perfect Score", "icon": "⭐", "earned": False},
            {"name": "Night Owl", "icon": "🦉", "earned": False},
            {"name": "Speed Demon", "icon": "⚡", "earned": False},
            {"name": "Completionist", "icon": "🏆", "earned": False},
        ],
        "languages": [],
    }
    MOCK_USERS[user_id] = new_user
    _persist_user(user_id)
    return user_id


def update_user_password(user_id: str, hashed_password: str) -> bool:
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    user["password"] = hashed_password
    _persist_user(user_id)
    return True


def update_user_in_db(user_id: str, updates: dict) -> bool:
    """Update arbitrary user fields in memory and MongoDB."""
    user = MOCK_USERS.get(user_id)
    if not user:
        return False
    for key, value in updates.items():
        user[key] = value
    _persist_user(user_id)
    return True


def normalize_mock_test_integrity_state(user: dict, persist: bool = False) -> dict:
    """Ensure anti-cheat fields exist and clear expired suspensions."""
    changed = False

    if "antiCheatWarnings" not in user:
        user["antiCheatWarnings"] = 0
        changed = True

    if "suspendedUntil" not in user:
        user["suspendedUntil"] = None
        changed = True

    suspended_until = user.get("suspendedUntil")
    if suspended_until:
        try:
            suspended_until_dt = datetime.fromisoformat(suspended_until)
        except ValueError:
            user["suspendedUntil"] = None
            user["antiCheatWarnings"] = 0
            changed = True
        else:
            if suspended_until_dt <= datetime.utcnow():
                user["suspendedUntil"] = None
                user["antiCheatWarnings"] = 0
                changed = True

    if changed and persist:
        _persist_user(user["id"])

    return user


def get_mock_test_integrity_status(user_id: str) -> dict:
    user = get_user_by_id(user_id)
    if not user:
        return {
            "warnings": 0,
            "maxWarnings": MAX_MOCK_TEST_WARNINGS,
            "isSuspended": False,
            "suspendedUntil": None,
        }

    normalize_mock_test_integrity_state(user, persist=True)
    suspended_until = user.get("suspendedUntil")
    return {
        "warnings": int(user.get("antiCheatWarnings", 0)),
        "maxWarnings": MAX_MOCK_TEST_WARNINGS,
        "isSuspended": bool(suspended_until),
        "suspendedUntil": suspended_until,
    }


def register_mock_test_violation(user_id: str, reason: str) -> dict:
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    normalize_mock_test_integrity_state(user, persist=False)

    new_count = int(user.get("antiCheatWarnings", 0)) + 1
    user["antiCheatWarnings"] = new_count

    is_suspended = new_count > MAX_MOCK_TEST_WARNINGS
    suspension_message = None

    if is_suspended:
        suspended_until = (datetime.utcnow() + timedelta(hours=MOCK_TEST_SUSPENSION_HOURS)).replace(microsecond=0)
        user["suspendedUntil"] = suspended_until.isoformat()
        suspension_message = (
            f"Account suspended for {MOCK_TEST_SUSPENSION_HOURS} hours after repeated prohibited actions during the mock test."
        )

    _persist_user(user_id)

    return {
        "warnings": new_count,
        "maxWarnings": MAX_MOCK_TEST_WARNINGS,
        "isSuspended": is_suspended,
        "suspendedUntil": user.get("suspendedUntil"),
        "reason": reason,
        "message": suspension_message or (
            f"Warning {new_count}/{MAX_MOCK_TEST_WARNINGS}: {reason}. "
            f"{MAX_MOCK_TEST_WARNINGS - new_count} warnings remaining before a 2-hour suspension."
        ),
    }


def user_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


# ── Notes CRUD ─────────────────────────────────────────────────
def save_user_note(user_id: str, topic_id: str, content: str, title: str = "") -> dict:
    """Save or update a note for a user on a topic."""
    db = _get_db()
    note = {
        "user_id": user_id,
        "topic_id": topic_id,
        "title": title,
        "content": content,
        "updated_at": datetime.now().isoformat(),
    }
    if db is not None:
        db.user_notes.update_one(
            {"user_id": user_id, "topic_id": topic_id},
            {"$set": note, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
            upsert=True,
        )
    return note


def get_user_notes(user_id: str, topic_id: str = None) -> list:
    """Get notes for a user, optionally filtered by topic."""
    db = _get_db()
    if db is None:
        return []
    query = {"user_id": user_id}
    if topic_id:
        query["topic_id"] = topic_id
    return [_clean_doc(d) for d in db.user_notes.find(query).sort("updated_at", -1)]


def delete_user_note(user_id: str, topic_id: str) -> bool:
    db = _get_db()
    if db is None:
        return False
    result = db.user_notes.delete_one({"user_id": user_id, "topic_id": topic_id})
    return result.deleted_count > 0


# ── Feedback CRUD ──────────────────────────────────────────────
def save_user_feedback(user_id: str, topic_id: str, rating: int, comment: str = "") -> dict:
    """Save feedback for a topic."""
    db = _get_db()
    feedback = {
        "user_id": user_id,
        "topic_id": topic_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.now().isoformat(),
    }
    if db is not None:
        db.user_feedback.update_one(
            {"user_id": user_id, "topic_id": topic_id},
            {"$set": feedback},
            upsert=True,
        )
    return feedback


def get_user_feedback(user_id: str, topic_id: str = None) -> list:
    db = _get_db()
    if db is None:
        return []
    query = {"user_id": user_id}
    if topic_id:
        query["topic_id"] = topic_id
    return [_clean_doc(d) for d in db.user_feedback.find(query).sort("created_at", -1)]


# ── Mock test results CRUD ─────────────────────────────────────
def save_mock_result(user_id: str, result_data: dict) -> dict:
    """Persist a mock test result and update user stats."""
    db = _get_db()
    record = {
        "user_id": user_id,
        **result_data,
        "created_at": datetime.now().isoformat(),
    }
    if db is not None:
        db.mock_results.insert_one(record)
    
    # Update user stats based on mock test result
    user = MOCK_USERS.get(user_id)
    if user:
        # Update quizzes taken count
        user["quizzesTaken"] = user.get("quizzesTaken", 0) + 1
        
        # Update total hours learned (convert seconds to hours)
        time_hours = result_data.get("time_taken", 0) / 3600
        user["totalHours"] = user.get("totalHours", 0) + time_hours
        
        # Update quiz scores and average
        percentage = result_data.get("percentage", 0)
        score = result_data.get("score", 0)
        
        user.setdefault("quizScores", {})[f"mock_test_{record.get('created_at', 'unknown')}"] = percentage
        
        # Calculate new average score from all quiz scores
        all_scores = list(user.get("quizScores", {}).values())
        if all_scores:
            user["avgScore"] = sum(all_scores) / len(all_scores)
        
        # Update topic status based on mock test result
        topics = result_data.get("topics", [])
        for topic_id in topics:
            # Ensure lists exist
            user.setdefault("completedTopics", [])
            user.setdefault("inProgressTopics", [])
            user.setdefault("pendingTopics", [])
            
            # Remove from other lists if present
            for list_name in ["pendingTopics", "inProgressTopics", "completedTopics"]:
                if topic_id in user[list_name]:
                    user[list_name].remove(topic_id)
            
            # Add to appropriate list based on score
            if percentage >= 70:
                # Topic passed - mark as completed
                user["completedTopics"].append(topic_id)
                user["totalScore"] = user.get("totalScore", 0) + score
            else:
                # Topic attempted but not passed - mark as in-progress
                user["inProgressTopics"].append(topic_id)
        
        _persist_user(user_id)
    
    record.pop("_id", None)
    return record


def get_mock_results(user_id: str) -> list:
    db = _get_db()
    if db is None:
        return []
    return [_clean_doc(d) for d in db.mock_results.find({"user_id": user_id}).sort("created_at", -1)]


# ── Detailed per-topic progress ────────────────────────────────
def save_topic_progress(user_id: str, topic_id: str, data: dict) -> dict:
    """Save detailed per-topic progress (time_spent, attempts, scores, etc.) and update user's total hours."""
    db = _get_db()
    record = {
        "user_id": user_id,
        "topic_id": topic_id,
        **data,
        "updated_at": datetime.now().isoformat(),
    }
    if db is not None:
        db.user_progress.update_one(
            {"user_id": user_id, "topic_id": topic_id},
            {"$set": record, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
            upsert=True,
        )
    
    # Update user's total learning hours
    user = MOCK_USERS.get(user_id)
    if user:
        time_spent_seconds = data.get("time_spent", 0)
        if time_spent_seconds > 0:
            # Convert seconds to hours and add to total
            time_hours = time_spent_seconds / 3600
            user["totalHours"] = user.get("totalHours", 0) + time_hours
            _persist_user(user_id)
    
    return record


def get_topic_progress(user_id: str, topic_id: str = None) -> list:
    db = _get_db()
    if db is None:
        return []
    query = {"user_id": user_id}
    if topic_id:
        query["topic_id"] = topic_id
    return [_clean_doc(d) for d in db.user_progress.find(query)]