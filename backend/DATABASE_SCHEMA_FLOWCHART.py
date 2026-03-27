"""
Database Schema for Progress Dashboard
Shows how data flows through the system
"""

# =====================================================
# MONGODB COLLECTIONS SCHEMA
# =====================================================

# Collection: user_progress
# Purpose: Track quiz scores, time spent, and completion status per topic
{
    "_id": ObjectId("..."),
    "user_id": "user_123",
    "topic_id": "data_types",
    "time_spent": 3600,              # seconds (1 hour)
    "quiz_score": 30,                # points earned
    "quiz_total": 40,                # maximum points
    "status": "completed",           # "in-progress" or "completed"
    "attempts": 1,                   # number of times attempted
    "updated_at": "2026-03-25T14:30:00",
    "created_at": "2026-03-25T13:00:00"
}

# Collection: understanding_feedback
# Purpose: Store self-assessed confidence values from slider (0-100%)
{
    "_id": ObjectId("..."),
    "user_id": "user_123",
    "topic_id": "data_types",
    "confidence_level": 85,          # 0-100 from slider
    "notes": "Understood the basics", # optional
    "saved_at": "2026-03-25T14:45:00",
    "created_at": "2026-03-25T14:45:00"
}

# =====================================================
# CALCULATION WORKFLOW
# =====================================================

"""
ENDPOINT: GET /progress/dashboard-metrics

1. FETCH DATA
   ├─ Get all user_progress records for user_id
   ├─ Get all understanding_feedback records for user_id
   └─ Get all mock_results for user_id

2. CALCULATE CORE METRICS
   ├─ Count topics with:
   │  - status = "completed" OR
   │  - score/total ≥ 70%
   │  = TOPICS_DONE
   │
   ├─ Average all quiz percentages
   │  = AVG_SCORE
   │
   ├─ Sum all time_spent values
   │  = TOTAL_TIME (in seconds)
   │  → Format as HH:MM:SS
   │
   └─ Average all confidence_level values
      = AVG_UNDERSTANDING

3. CALCULATE DERIVED METRICS
   ├─ Completion % = (TOPICS_DONE / TOTAL_TOPICS) × 100
   ├─ Pie Chart = {completed: TOPICS_DONE, remaining: TOTAL_TOPICS - TOPICS_DONE}
   └─ Time Learned = Convert TOTAL_TIME in HH:MM:SS

4. GENERATE GRAPH DATA (past 7 days)
   ├─ For each updated_at date in last 7 days:
   │  ├─ Get quiz_score and quiz_total
   │  ├─ Calculate percentage
   │  ├─ Map to engagement level:
   │  │  - 0% → 0
   │  │  - 1-25% → 0.25
   │  │  - 26-50% → 0.5
   │  │  - 51-75% → 0.75
   │  │  - 76-100% → 1.0
   │  └─ Add to daily total
   └─ Result: [{day: "Wed", engagement: 0.75}, ...]

5. FORMAT COMPLETED TOPICS
   ├─ For each completed topic:
   │  ├─ Get topic_name from MOCK_TOPICS
   │  ├─ Extract score/total
   │  ├─ Calculate percentage
   │  ├─ Format date as DD/MM/YYYY
   │  ├─ Get understanding_level from feedback
   │  ├─ Format time_spent as HH:MM:SS
   │  └─ Include attempts count
   └─ Sort by date descending (newest first)

6. INCLUDE UNDERSTANDING FEEDBACK
   ├─ Check if user has any feedback
   ├─ Return feedback records or empty list
   └─ Data available for each topic

7. RETURN COMPLETE PAYLOAD
   {
     "metrics": {
       "topics_done": 2,
       "total_topics": 200,
       "avg_score": 31.7,
       "time_learned_seconds": 374494,
       "avg_understanding": 60.0,
       "completion_percentage": 1.0
     },
     "learning_progress_graph": [
       { "day": "Wed", "date": "2026-03-25", "engagement": 0.75 },
       ...
     ],
     "pie_chart": {
       "completed": 2,
       "remaining": 198,
       "completion_percentage": 1.0
     },
     "completed_topics": [
       {
         "topic_name": "Data Types",
         "score": 30,
         "total": 40,
         "percentage": 75.0,
         "date_completed": "25/03/2026",
         "understanding_level": 85,
         "time_spent": "01:00:00",
         "attempts": 1
       },
       ...
     ],
     "understanding_feedback": {
       "has_feedback": true,
       "records": [...]
     }
   }
"""

# =====================================================
# DATA SECURITY
# =====================================================

"""
USER ISOLATION EXAMPLE:

User A (user_123) queries:
  GET /progress/dashboard-metrics
  ↓
  save_understanding_feedback() called
  ↓
  Query: db.understanding_feedback.find({"user_id": "user_123"})
  ↓
  Only returns User A's feedback

User B (user_456) queries:
  GET /progress/dashboard-metrics
  ↓
  save_understanding_feedback() called
  ↓
  Query: db.understanding_feedback.find({"user_id": "user_456"})
  ↓
  Only returns User B's feedback
  ↓
  User A's data NOT visible

Security enforced at:
1. JWT token extraction (get_current_user_from_token)
2. Database query level (all WHERE user_id = <from JWT>)
3. Function parameters (user_id always from JWT)
4. No cross-user data possible
"""

# =====================================================
# SCORE MAPPING VISUALIZATION
# =====================================================

"""
Quiz Score → Engagement Level Mapping:

Quiz Score %   Engagement Level   Graph Height
─────────────────────────────────────────────
    0%    →        0              (bottom)
    10%   →        0.25           ▌
    25%   →        0.25           ▌
    50%   →        0.5            ██
    75%   →        0.75           ███
    100%  →        1.0            ████ (top)

Example: Student scores 30/40 on quiz
  = 75% → 0.75 engagement
  = Shows on graph as 75% height on that day
"""

# =====================================================
# REATTEMPT HANDLING
# =====================================================

"""
First Attempt:
  Topic Progress: {"topic_id": "data_types", "score": 20, "status": "in-progress"}
  Topics Done: 0 (score only 50%)
  Score: 20/40

Second Attempt (same topic):
  Update: {"topic_id": "data_types", "score": 35, "status": "completed"}
  Topics Done: 1 (score now 87.5%, ≥70%)
  Score: 35/40

Result:
  - Topics Done incremented only ONCE
  - Latest score (35/40) displayed
  - Latest date displayed (attempt 2)
  - Highest date-based entry used
  - Old attempt data overwritten (upsert)
"""

# =====================================================
# TIME ACCUMULATION EXAMPLE
# =====================================================

"""
Data Types:      1 hour = 3600 seconds
Syntax & Vars:   30 mins = 1800 seconds
Control Structs: 2 hours = 7200 seconds
─────────────────────────────────────
Total:           150 mins = 9000 seconds
               = 2 hours 30 minutes
               = 02:30:00 formatted
"""

# =====================================================
# UNDERSTANDING FEEDBACK FLOW
# =====================================================

"""
Topic Page:
  User completes quiz → Score: 75%
  ↓
  Confidence slider appears → User sets to 85%
  ↓
  "Save Feedback" clicked
  ↓
  POST /progress/understanding-feedback
  ├─ Body: {"topic_id": "data_types", "confidence_level": 85}
  ↓
  save_understanding_feedback(user_id, topic_id, data)
  ├─ MongoDB: understanding_feedback.upsert()
  ├─ Result: Record saved with timestamp
  ↓
Dashboard:
  GET /progress/dashboard-metrics
  ↓
  get_understanding_feedback(user_id) called
  ├─ All feedback records fetched
  ├─ Confidence values extracted
  ├─ Average calculated: (85 + 75 + 60) / 3 = 73.3%
  ↓
  Returned in response:
  ├─ Avg Understanding: 73.3%
  ├─ Per-topic understanding values shown
"""

# =====================================================
# INFERENCE: TOTAL TOPICS COUNT
# =====================================================

"""
How total topics determined:
  Option 1: Count all topics in MOCK_TOPICS cache
  Option 2: Query topics collection in MongoDB
  Option 3: User preference setting

Current Implementation:
  Used: len(get_all_topics())
  
  This gets ALL topics available in the system,
  not just topics the user has started.
  
  Alternative (if you want "topics available to user"):
    len([t for t in MOCK_TOPICS.values() if t.get('class') == user['class']])
"""
