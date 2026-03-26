export interface User {
    id: string;
    name: string;
    email: string;
    password?: string;
    completedTopics: string[];
    pendingTopics: string[];
    inProgressTopics: string[];
    videosWatched: WatchedVideo[];
    totalScore: number;
    rank: number;
    preferredStyle: ExplanationStyle;
    confusionCount: number;
    antiCheatWarnings?: number;
    suspendedUntil?: string | null;
}

export type TopicStatus = 'completed' | 'pending' | 'in-progress';
export type ExplanationStyle = 'visual' | 'simplified' | 'logical' | 'analogy';

export interface Explanation {
    style: ExplanationStyle;
    title: string;
    content: string;
    icon: string;
}

export interface Topic {
    id: string;
    language: string;
    topicName: string;
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
    overview: string;
    explanations: Explanation[];
    quiz: QuizQuestion[];
    recommendedVideos: Video[];
}

export interface Video {
    id: string;
    title: string;
    language: string;
    youtubeId: string;
    thumbnail: string;
    duration: string;
}

export interface WatchedVideo extends Video {
    watchedAt: string;
    timeWatched: string;
}

export interface QuizQuestion {
    id: string;
    question: string;
    options: string[];
    correctAnswer: number;
}

// ── Notes ──────────────────────────────────────────────────────
export interface UserNote {
    user_id: string;
    topic_id: string;
    title: string;
    content: string;
    created_at?: string;
    updated_at?: string;
}

// ── Feedback ───────────────────────────────────────────────────
export interface UserFeedback {
    user_id: string;
    topic_id: string;
    rating: number;
    comment: string;
    created_at?: string;
}

// ── Detailed Progress ──────────────────────────────────────────
export interface TopicProgressRecord {
    user_id: string;
    topic_id: string;
    time_spent: number;
    quiz_score?: number;
    quiz_total?: number;
    attempts: number;
    status: string;
    updated_at?: string;
}

// ── Mock Test Result ───────────────────────────────────────────
export interface MockTestResult {
    user_id: string;
    topics: string[];
    score: number;
    total_questions: number;
    percentage: number;
    time_taken: number;
    created_at?: string;
}

// ── Adaptive Analysis ──────────────────────────────────────────
export interface AdaptiveAnalysis {
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    nextTopics: string[];
    studyPlan: string;
}
