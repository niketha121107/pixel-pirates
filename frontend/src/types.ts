export interface User {
    id: string;
    name: string;
    email: string;
    password: string;
    completedTopics: string[];
    pendingTopics: string[];
    inProgressTopics: string[];
    videosWatched: WatchedVideo[];
    totalScore: number;
    rank: number;
    preferredStyle: ExplanationStyle;
    confusionCount: number;
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

export interface LeaderboardEntry {
    rank: number;
    userId: string;
    name: string;
    score: number;
    topicsCompleted: number;
    avatar: string;
}
