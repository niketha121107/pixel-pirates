import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 15000, // 15s timeout to avoid hanging requests
});

// Request interceptor — attach auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor — handle 401 and connection errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
        }
        // Handle connection refused / network errors
        if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED' || !error.response) {
            console.warn(
                '⚠️ Backend server unreachable. Make sure the backend is running:\n' +
                '   cd backend && python main.py'
            );
            return Promise.reject({
                ...error,
                message: 'Backend server is not running. Please start the backend server first.',
                isNetworkError: true,
            });
        }
        return Promise.reject(error);
    }
);

// ── Auth ─────────────────────────────────────────────────────────────
export const authAPI = {
    login: (email: string, password: string) =>
        api.post('/auth/login', { email, password }),
    signup: (name: string, email: string, password: string) =>
        api.post('/auth/signup', { name, email, password }),
    logout: () => api.post('/auth/logout'),
    me: () => api.get('/auth/me'),
    refresh: () => api.post('/auth/refresh'),
};

// ── Topics ───────────────────────────────────────────────────────────
export const topicsAPI = {
    getAll: (language?: string) =>
        api.get('/topics', { params: language ? { language } : {} }),
    getById: (id: string) => api.get(`/topics/${id}`),
    getExplanation: (id: string, style?: string) =>
        api.get(`/topics/${id}/explanation`, { params: style ? { style } : {} }),
    getQuiz: (id: string, subtopicId?: string) =>
        api.get(`/topics/${id}/quiz`, { params: subtopicId ? { subtopicId } : {} }),
    updateStatus: (id: string, data: object) =>
        api.put(`/topics/${id}/status`, data),
    getFreshVideos: (id: string, maxResults?: number) =>
        api.get(`/topics/${id}/fresh-videos`, { params: maxResults ? { max_results: maxResults } : {} }),
};

// ── Quiz ─────────────────────────────────────────────────────────────
export const quizAPI = {
    submit: (data: object) => api.post('/quiz/submit', data),
    adaptive: (topicId: string, questionCount?: number) =>
        api.post('/quiz/adaptive', null, {
            params: { topic_id: topicId, question_count: questionCount || 5 },
        }),
    mockTest: (data: object) => api.post('/quiz/mock-test', data),
    results: (topicId: string) => api.get(`/quiz/results/${topicId}`),
    performanceAnalysis: () => api.get('/quiz/performance-analysis'),
};

// ── Videos ───────────────────────────────────────────────────────────
export const videosAPI = {
    search: (q: string, language?: string) =>
        api.get('/videos/search', { params: { q, language } }),
    recommendations: () => api.get('/videos/recommendations'),
    watched: () => api.get('/videos/watched'),
    markWatched: (data: object) => api.post('/videos/watch', data),
    trending: (language: string) => api.get(`/videos/trending/${language}`),
};

// ── Leaderboard ──────────────────────────────────────────────────────
export const leaderboardAPI = {
    global: () => api.get('/leaderboard'),
    top: (count: number) => api.get(`/leaderboard/top/${count}`),
    userRank: () => api.get('/leaderboard/user-rank'),
    byLanguage: (language: string) =>
        api.get(`/leaderboard/language/${language}`),
};

// ── Analytics ────────────────────────────────────────────────────────
export const analyticsAPI = {
    dashboard: () => api.get('/analytics/dashboard'),
    progress: (period?: string) =>
        api.get('/analytics/progress', { params: period ? { period } : {} }),
    performance: () => api.get('/analytics/performance'),
    streaks: () => api.get('/analytics/streaks'),
};

// ── Search ───────────────────────────────────────────────────────────
export const searchAPI = {
    recent: () => api.get('/search/recent'),
    search: (query: string) => api.post('/search', { query }),
    suggestions: (q: string) =>
        api.get('/search/suggestions', { params: { q } }),
    global: (q: string, category?: string) =>
        api.get('/search/global', { params: { q, category } }),
    clearRecent: () => api.delete('/search/recent'),
    trending: () => api.get('/search/trending'),
};

// ── Users ────────────────────────────────────────────────────────────
export const usersAPI = {
    profile: () => api.get('/users/profile'),
    updateProfile: (data: object) => api.put('/users/profile', data),
    stats: () => api.get('/users/stats'),
    analytics: (userId: string) => api.get(`/users/${userId}/analytics`),
    getMockTestIntegrity: () => api.get('/users/mock-test-integrity'),
    reportMockTestViolation: (reason: string) => api.post('/users/mock-test-integrity', { reason }),
    recordTopicTime: (topicId: string, topicName: string, durationInSeconds: number) =>
        api.post('/users/record-topic-time', { topicId, topicName, durationInSeconds }),
};
// ── Notes ────────────────────────────────────────────────────────
export const notesAPI = {
    save: (data: { topic_id: string; title?: string; content: string }) =>
        api.post('/notes', data),
    getAll: (topicId?: string) =>
        api.get('/notes', { params: topicId ? { topic_id: topicId } : {} }),
    remove: (topicId: string) => api.delete(`/notes/${topicId}`),
};

// ── Feedback ─────────────────────────────────────────────────────
export const feedbackAPI = {
    submit: (data: { topic_id: string; rating: number; comment?: string }) =>
        api.post('/feedback', data),
    getAll: (topicId?: string) =>
        api.get('/feedback', { params: topicId ? { topic_id: topicId } : {} }),
};

// ── Progress (detailed) ─────────────────────────────────────────
export const progressAPI = {
    saveTopic: (data: object) => api.post('/progress/topic', data),
    getTopic: (topicId?: string) =>
        api.get('/progress/topic', { params: topicId ? { topic_id: topicId } : {} }),
    saveMockResult: (data: object) => api.post('/progress/mock-result', data),
    getMockResults: () => api.get('/progress/mock-results'),
};

// ── Adaptive Learning ────────────────────────────────────────────
export const adaptiveAPI = {
    analyze: (topicId: string) => api.get(`/adaptive/analyze/${topicId}`),
    explanation: (topicId: string) => api.get(`/adaptive/explanation/${topicId}`),
    quiz: (topicId: string) => api.get(`/adaptive/quiz/${topicId}`),
};
export default api;
