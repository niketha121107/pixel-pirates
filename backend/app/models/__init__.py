from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, date
from enum import Enum

# User Models
class User(BaseModel):
    id: str
    name: str
    email: str
    password: Optional[str] = None  # Don't include in responses
    completed_topics: List[str] = Field(default_factory=list, alias="completedTopics")
    pending_topics: List[str] = Field(default_factory=list, alias="pendingTopics")
    in_progress_topics: List[str] = Field(default_factory=list, alias="inProgressTopics")
    videos_watched: List["WatchedVideo"] = Field(default_factory=list, alias="videosWatched")
    total_score: int = Field(default=0, alias="totalScore")
    rank: int = Field(default=0)
    preferred_style: str = Field(default="visual", alias="preferredStyle")
    confusion_count: int = Field(default=0, alias="confusionCount")
    created_at: Optional[str] = Field(default=None, alias="createdAt")
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")
    
    class Config:
        populate_by_name = True

class UserResponse(BaseModel):
    """User model for API responses (without password)"""
    id: str
    name: str
    email: str
    completed_topics: List[str] = Field(alias="completedTopics")
    pending_topics: List[str] = Field(alias="pendingTopics")
    in_progress_topics: List[str] = Field(alias="inProgressTopics")
    videos_watched: List["WatchedVideo"] = Field(alias="videosWatched")
    total_score: int = Field(alias="totalScore")
    rank: int
    preferred_style: str = Field(alias="preferredStyle")
    confusion_count: int = Field(alias="confusionCount")
    created_at: Optional[str] = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")
    
    class Config:
        populate_by_name = True

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    preferred_style: Optional[str] = None

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse

# Topic Models
class ExplanationStyle(str, Enum):
    visual = "visual"
    simplified = "simplified"
    logical = "logical"
    analogy = "analogy"

class TopicStatus(str, Enum):
    completed = "completed"
    pending = "pending"
    in_progress = "in-progress"

class Explanation(BaseModel):
    style: ExplanationStyle
    title: str
    content: str
    icon: str

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int = Field(alias="correctAnswer")
    
    class Config:
        populate_by_name = True

class Video(BaseModel):
    id: str
    title: str
    language: str
    youtube_id: str = Field(alias="youtubeId")
    thumbnail: str
    duration: str
    
    class Config:
        populate_by_name = True

class WatchedVideo(Video):
    watched_at: str = Field(alias="watchedAt")
    time_watched: str = Field(alias="timeWatched")
    
    class Config:
        populate_by_name = True

class Topic(BaseModel):
    id: str
    language: str
    topic_name: str = Field(alias="topicName")
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]
    overview: str
    explanations: List[Explanation]
    quiz: List[QuizQuestion]
    recommended_videos: List[Video] = Field(alias="recommendedVideos")
    
    class Config:
        populate_by_name = True

class TopicProgress(BaseModel):
    topic_id: str
    status: TopicStatus
    score: Optional[int] = None
    total_possible: Optional[int] = None
    date_completed: Optional[str] = None

# Quiz Models
class QuizAnswer(BaseModel):
    question_id: str
    selected_answer: int

class QuizSubmission(BaseModel):
    topic_id: str
    answers: List[QuizAnswer]
    time_taken: Optional[int] = None  # seconds

class QuizResult(BaseModel):
    topic_id: str
    score: int
    total_questions: int
    correct_answers: List[str]
    incorrect_answers: List[str]
    percentage: float
    time_taken: Optional[int] = None

# Leaderboard Models
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str = Field(alias="userId")
    name: str
    score: int
    topics_completed: int = Field(alias="topicsCompleted")
    avatar: str
    
    class Config:
        populate_by_name = True

# Analytics Models
class UserStats(BaseModel):
    topics_completed: int = Field(alias="topicsCompleted")
    total_topics: int = Field(alias="totalTopics")
    quizzes_taken: int = Field(alias="quizzesTaken")
    avg_score: float = Field(alias="avgScore")
    streak: int
    total_hours: int = Field(alias="totalHours")
    join_date: str = Field(alias="joinDate")
    rank: int
    badges: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    
    class Config:
        populate_by_name = True

# Search Models
class SearchQuery(BaseModel):
    query: str
    
class SearchResult(BaseModel):
    query: str
    timestamp: datetime
    
class RecentSearch(BaseModel):
    query: str
    time: str

# Response Models
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None