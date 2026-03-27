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
    # Reload from MongoDB to ensure fresh data after updates
    db = _get_db()
    if db is not None:
        mongo_user = db.users.find_one({"_id": user_id})
        if mongo_user:
            # Convert MongoDB _id to id field and update cache
            mongo_user["id"] = str(mongo_user.pop("_id"))
            MOCK_USERS[user_id] = mongo_user
    
    user = MOCK_USERS.get(user_id)
    if user:
        normalize_mock_test_integrity_state(user, persist=True)
    return user


def get_user_by_email(email: str):
    _ensure_cache_loaded(require_users=True)
    for user in MOCK_USERS.values():
        if user.get("email") == email:
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
    
    # Also save to user_progress collection so dashboard metrics can find it
    db = _get_db()
    if db is not None:
        progress_record = {
            "user_id": user_id,
            "topic_id": topic_id,
            "status": status,
            "quiz_score": score or 0,
            "quiz_total": 100,
            "updated_at": datetime.now().isoformat(),
        }
        db.user_progress.update_one(
            {"user_id": user_id, "topic_id": topic_id},
            {"$set": progress_record, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
            upsert=True,
        )
    
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
    
    logger.info(f"💾 Saving mock result for user {user_id}: {result_data}")
    
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
                logger.info(f"✅ Topic {topic_id} marked as COMPLETED (score: {percentage}%) for user {user_id}")
            else:
                # Topic attempted but not passed - mark as in-progress
                user["inProgressTopics"].append(topic_id)
                logger.info(f"🔄 Topic {topic_id} marked as IN-PROGRESS (score: {percentage}%) for user {user_id}")
        
        logger.info(f"📊 User {user_id} stats updated: {len(user['completedTopics'])} completed, avg={user.get('avgScore'):.1f}%, quizzes={user['quizzesTaken']}")
        _persist_user(user_id)
    else:
        logger.error(f"❌ User {user_id} not found in MOCK_USERS")
    
    record.pop("_id", None)
    return record


def get_mock_results(user_id: str) -> list:
    db = _get_db()
    if db is None:
        return []
    return [_clean_doc(d) for d in db.mock_results.find({"user_id": user_id}).sort("created_at", -1)]


# ── Detailed per-topic progress ────────────────────────────────
def save_topic_progress(user_id: str, topic_id: str, data: dict) -> dict:
    """Save detailed per-topic progress (time_spent, attempts, scores, etc.) and update user's total hours and topic status."""
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
    
    # Update user's total learning hours and topic completion status
    user = MOCK_USERS.get(user_id)
    if user:
        time_spent_seconds = data.get("time_spent", 0)
        if time_spent_seconds > 0:
            # Convert seconds to hours and add to total
            time_hours = time_spent_seconds / 3600
            user["totalHours"] = user.get("totalHours", 0) + time_hours
        
        # Update topic status based on quiz score
        quiz_score = data.get("quiz_score", 0)
        quiz_total = data.get("quiz_total", 100)
        status = data.get("status", "in-progress")
        percentage = (quiz_score / quiz_total * 100) if quiz_total > 0 else 0
        
        # Ensure lists exist
        user.setdefault("completedTopics", [])
        user.setdefault("inProgressTopics", [])
        user.setdefault("pendingTopics", [])
        
        # Remove from other lists if present
        for list_name in ["pendingTopics", "inProgressTopics", "completedTopics"]:
            if topic_id in user[list_name]:
                user[list_name].remove(topic_id)
        
        # Add to appropriate list based on status
        if status == "completed" or percentage >= 70:
            # Topic passed - mark as completed
            user["completedTopics"].append(topic_id)
            # Update quiz scores
            user.setdefault("quizScores", {})[topic_id] = quiz_score
            # Recalculate average score
            all_scores = list(user.get("quizScores", {}).values())
            if all_scores:
                user["avgScore"] = sum(all_scores) / len(all_scores)
        else:
            # Topic attempted but not passed - mark as in-progress
            user["inProgressTopics"].append(topic_id)
        
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


# ── 5. Understanding Feedback ────────────────────────────────────────
def save_understanding_feedback(user_id: str, topic_id: str, data: dict) -> dict:
    """
    Save self-assessed confidence/understanding feedback for a topic.
    
    FEATURE: Understanding Feedback
    Purpose: Integrate student self-assessment of comprehension
    
    Confidence Slider Integration:
    - Range: 0-100% (represents how well student understands the topic)
    - Stored after each quiz completion
    - Optional but recommended for complete metrics
    
    Impact on Metrics:
    - Avg Understanding is average of all confidence values
    - If no feedback recorded, Avg Understanding = 0%
    - Feedback updates are immediate and reflected in next metrics call
    
    API Endpoint: POST /progress/understanding-feedback
    Request: {"topic_id": "data_types", "confidence_level": 85}
    
    Args:
        user_id (str): Student ID (scoped for data isolation)
        topic_id (str): Topic identifier
        data (dict): Contains confidence_level (0-100) and optional notes
    
    Returns:
        dict: Saved feedback record with timestamp
    """
    db = _get_db()
    record = {
        "user_id": user_id,
        "topic_id": topic_id,
        "confidence_level": data.get("confidence_level", 0),
        "notes": data.get("notes", ""),
        "saved_at": datetime.now().isoformat(),
    }
    if db is not None:
        db.understanding_feedback.update_one(
            {"user_id": user_id, "topic_id": topic_id},
            {"$set": record, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
            upsert=True,
        )
    return record


def get_understanding_feedback(user_id: str, topic_id: str = None) -> list:
    """
    Retrieve understanding feedback for one or all topics.
    
    FEATURE: Understanding Feedback
    Purpose: Integrate student self-assessment of comprehension
    
    Retrieves all saved confidence slider values for the student.
    Optional topic_id filter to get feedback for specific topic.
    
    Feedback Integration:
    - Each record contains: topic_id, confidence_level (0-100), saved_at timestamp
    - Used to calculate Avg Understanding metric
    - Supports topic-specific or complete feedback retrieval
    
    DATA INTEGRITY:
    Query scoped to user_id - retrieves only this student's feedback
    Prevents cross-student data access
    
    API Endpoint: GET /progress/understanding-feedback
    Response: {"records": [{topic_id, confidence_level, saved_at}]}
    
    Args:
        user_id (str): Student ID (scoped for data isolation)
        topic_id (str, optional): Specific topic to retrieve. If None, gets all topics.
    
    Returns:
        list: Understanding feedback records for the student
    """
    db = _get_db()
    if db is None:
        return []
    query = {"user_id": user_id}
    if topic_id:
        query["topic_id"] = topic_id
    return [_clean_doc(d) for d in db.understanding_feedback.find(query)]


# ── 1. Learning Progress Graph ────────────────────────────────────────
def map_score_to_engagement(percentage: float) -> float:
    """
    Map quiz score percentage to engagement level for Learning Progress Graph.
    
    Score Mapping:
    - 0% → 0 (No engagement)
    - 1–25% → 0.25 (Low engagement)
    - 26–50% → 0.5 (Medium engagement)
    - 51–75% → 0.75 (High engagement)
    - 76–100% → 1 (Full engagement)
    
    Purpose: Converts quiz scores to engagement values plotted in the learning progress graph.
    Output: Engagement level (0-1) for each completed quiz on a specific date.
    
    Args:
        percentage (float): Quiz score as percentage (0-100)
    
    Returns:
        float: Engagement level (0, 0.25, 0.5, 0.75, or 1.0)
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


# ── 2. Metrics Updates & 3. Pie Chart Completion ────────────────────────────────────────
def calculate_progress_metrics(user_id: str) -> dict:
    """
    Calculate complete dashboard metrics for Student Progress Page.
    
    METRICS CALCULATED:
    1. Topics Done: Count of topics where status="completed" OR score ≥ 70%
    2. Avg Score: Average of all quiz score percentages
    3. Time Learned: Sum of all time_spent values (formatted HH:MM:SS)
    4. Avg Understanding: Average of self-assessed confidence values (0-100%)
    5. Completion %: (Topics Done / Total Topics) × 100
    
    PIE CHART DATA:
    Formula: Completion = (Topics Done / Total Topics) × 100
    Returns: completed count, remaining count, completion percentage
    
    LEARNING PROGRESS GRAPH:
    Plots engagement levels (mapped from scores) against completion dates for past 7 days.
    
    COMPLETED TOPICS:
    Lists each topic with: name, date (DD/MM/YYYY), score, percentage, understanding, time (HH:MM:SS)
    Reattempts update score/date but don't increase Topics Done counter.
    
    DATA INTEGRITY:
    All queries scoped to CURRENT_USER_ID - prevents one student's data from being visible to another.
    
    Returns:
        dict: Complete dashboard data with metrics, graph, pie chart, topics, and feedback
    """
    db = _get_db()
    
    # 1. Get all topic progress records for this user (scoped by user_id)
    progress_records = get_topic_progress(user_id)
    
    # 2. Get all understanding feedback for this user (scoped by user_id)
    understanding_records = get_understanding_feedback(user_id)
    
    # 3. Get mock results
    mock_results = get_mock_results(user_id)
    
    # Count completed topics (where status="completed" or score >= 70%)
    completed_topics = []
    all_scores = []
    total_time_spent = 0  # in seconds
    
    for record in progress_records:
        score = record.get("quiz_score", 0)
        total = record.get("quiz_total", 100)
        # Handle None values for total
        if total is None:
            total = 100
        percentage = (score / total * 100) if total > 0 else 0
        status = record.get("status", "in-progress")
        
        if status == "completed" or percentage >= 70:
            completed_topics.append(record)
        
        if score > 0 and total > 0:
            all_scores.append(percentage)
        
        time_spent = record.get("time_spent", 0)
        if time_spent > 0:
            total_time_spent += time_spent
    
    # Calculate metrics
    topics_done = len(completed_topics)
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Average understanding from confidence slider values
    if understanding_records:
        confidences = [r.get("confidence_level", 0) for r in understanding_records if "confidence_level" in r]
        avg_understanding = sum(confidences) / len(confidences) if confidences else 0
    else:
        avg_understanding = 0
    
    # Get total topics count from user model
    user = MOCK_USERS.get(user_id, {})
    total_topics = len(get_all_topics())  # Get total topics count
    
    # Completion percentage: (Topics Done / Total Topics) × 100
    completion_percentage = (topics_done / total_topics * 100) if total_topics > 0 else 0
    
    # Learning progress graph data (last 7 days)
    learning_progress = get_learning_progress_graph(user_id)
    
    # Completed topics with scores
    completed_topics_data = get_completed_topics_with_scores(user_id)
    
    # Understanding feedback
    has_understanding_feedback = len(understanding_records) > 0
    
    return {
        "metrics": {
            "topics_done": topics_done,
            "total_topics": total_topics,
            "avg_score": round(avg_score, 1),
            "time_learned_seconds": total_time_spent,
            "avg_understanding": round(avg_understanding, 1),
            "completion_percentage": round(completion_percentage, 1),
        },
        "learning_progress_graph": learning_progress,
        "pie_chart": {
            "completed": topics_done,
            "remaining": total_topics - topics_done,
            "completion_percentage": round(completion_percentage, 1),
        },
        "completed_topics": completed_topics_data,
        "understanding_feedback": {
            "has_feedback": has_understanding_feedback,
            "records": understanding_records,
        },
    }


def get_learning_progress_graph(user_id: str) -> list:
    """
    Get learning progress graph data for Student Progress Page - past 7 days.
    
    FEATURE: Learning Progress Graph
    Purpose: Plot engagement levels against completion dates as a line graph
    
    How it works:
    1. Collects all quiz completions from past 7 days
    2. Maps each score to engagement level using score_to_engagement mapping:
       - 0% → 0, 1-25% → 0.25, 26-50% → 0.5, 51-75% → 0.75, 76-100% → 1
    3. Accumulates daily engagement (multiple quizzes per day sum)
    4. Formats for chart display with day label and date
    
    Output: Line graph data showing daily progress with engagement scores
    Each day includes: day (Mon-Sun), date (ISO format), engagement (0-1.0)
    Score mapping: 0%→0, 1-25%→0.25, 26-50%→0.5, 51-75%→0.75, 76-100%→1
    
    Args:
        user_id (str): Student ID (scoped for data isolation)
    
    Returns:
        list: 7-day engagement data formatted for line chart
    """
    progress_records = get_topic_progress(user_id)
    
    # Create daily engagement map for last 7 days
    from datetime import datetime, timedelta
    today = datetime.now().date()
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    daily_engagement = {}
    
    # Initialize last 7 days with 0 engagement
    for i in range(7):
        date = today - timedelta(days=6 - i)  # Oldest to newest
        date_str = date.isoformat()
        daily_engagement[date_str] = 0
    
    # Accumulate engagement scores for each day
    for record in progress_records:
        updated_at = record.get("updated_at", "")
        if updated_at:
            try:
                # Parse the timestamp and convert to date
                if isinstance(updated_at, str):
                    # Handle ISO format with or without timezone
                    record_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).date()
                else:
                    record_date = updated_at if isinstance(updated_at, datetime.date) else datetime.fromisoformat(str(updated_at)).date()
                
                record_date_str = record_date.isoformat()
                
                # Only count if within last 7 days
                if record_date_str in daily_engagement:
                    # Calculate engagement from score using mapping function
                    score = record.get("quiz_score", 0)
                    total = record.get("quiz_total", 100)
                    # Handle None values for total
                    if total is None:
                        total = 100
                    percentage = (score / total * 100) if total > 0 else 0
                    engagement = map_score_to_engagement(percentage)
                    daily_engagement[record_date_str] += engagement
            except Exception as e:
                logger.warning(f"Error parsing date {updated_at}: {e}")
    
    # Format for chart display
    result = []
    for date_str, engagement in sorted(daily_engagement.items()):
        date_obj = datetime.fromisoformat(date_str).date()
        day_index = date_obj.weekday()  # Monday=0, Sunday=6
        day_label = day_labels[day_index]
        
        result.append({
            "day": day_label,
            "date": date_str,
            "engagement": round(engagement, 2),
        })
    
    return result


def get_completed_topics_with_scores(user_id: str) -> list:
    """
    Get list of completed topics for Student Progress Page with comprehensive metrics.
    
    FEATURE: Completed Topics & Scores
    Purpose: Display each completed topic with detailed performance metrics
    
    Data included per topic:
    - topic_name: Display name of the topic
    - date_completed: Date of completion (formatted DD/MM/YYYY)
    - score: Numerical quiz score (e.g., 30/40)
    - percentage: Score as percentage (e.g., 75%)
    - understanding_level: Student's self-assessed confidence (0-100%)
    - time_spent: Time spent on topic (formatted HH:MM:SS)
    - attempts: Number of quiz attempts
    
    Special Rules:
    - Only topics with status="completed" OR score ≥ 70% are included
    - Reattempts update score/date but don't increase Topics Done counter
    - Sorted by date (most recent first)
    - Prevents double-counting when students retake quizzes
    
    Output: CSV file with all topic records and metrics
    
    Args:
        user_id (str): Student ID (scoped for data isolation)
    
    Returns:
        list: Formatted list of completed topics with all metrics
    """
    from datetime import datetime
    
    db = _get_db()
    progress_records = get_topic_progress(user_id)
    understanding_map = {r["topic_id"]: r.get("confidence_level", 0) for r in get_understanding_feedback(user_id)}
    
    # Get topic names from MOCK_TOPICS
    completed_list = []
    
    for record in progress_records:
        score = record.get("quiz_score", 0)
        total = record.get("quiz_total", 100)
        # Handle None values for total
        if total is None:
            total = 100
        percentage = (score / total * 100) if total > 0 else 0
        status = record.get("status", "in-progress")
        
        # Only include completed topics
        if status == "completed" or percentage >= 70:
            topic_id = record.get("topic_id", "")
            topic = MOCK_TOPICS.get(topic_id, {})
            topic_name = topic.get("topicName", topic_id)
            
            updated_at = record.get("updated_at", "")
            try:
                date_obj = datetime.fromisoformat(updated_at)
                formatted_date = date_obj.strftime("%d/%m/%Y")
            except Exception:
                formatted_date = ""
            
            time_spent = record.get("time_spent", 0)
            hours = time_spent // 3600
            minutes = (time_spent % 3600) // 60
            seconds = time_spent % 60
            time_spent_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            understanding_level = understanding_map.get(topic_id, 0)
            
            completed_list.append({
                "topic_name": topic_name,
                "topic_id": topic_id,
                "score": score,
                "total": total,
                "percentage": round(percentage, 1),
                "date_completed": formatted_date,
                "understanding_level": understanding_level,
                "time_spent": time_spent_formatted,
                "time_spent_seconds": time_spent,
                "attempts": record.get("attempts", 1),
            })
    
    # Sort by date descending (most recent first)
    completed_list.sort(key=lambda x: x.get("date_completed", ""), reverse=True)
    
    return completed_list