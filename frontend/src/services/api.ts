import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
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
    getAll: (language?: string, search?: string) =>
        api.get('/topics', { params: { ...(language ? { language } : {}), ...(search ? { search } : {}) } }),
    getById: (id: string) => api.get(`/topics/${id}`),
    getExplanation: (id: string, style?: string) =>
        api.get(`/topics/${id}/explanation`, { params: style ? { style } : {} }),
    getQuiz: (id: string, subtopicId?: string) =>
        api.get(`/topics/${id}/quiz`, { params: subtopicId ? { subtopicId } : {} }),
    updateStatus: (id: string, data: object) =>
        api.put(`/topics/${id}/status`, data),
    getFreshVideos: (id: string, maxResults?: number) =>
        api.get(`/topics/${id}/fresh-videos`, { params: maxResults ? { max_results: maxResults } : {} }),
    getPDF: (id: string) =>
        api.get(`/content/pdf/${id}`),
};

// ── Quiz ─────────────────────────────────────────────────────────────
export const quizAPI = {
    submit: (data: object) => api.post('/quiz/submit', data),
    adaptive: (topicId: string, questionCount?: number) =>
        api.post('/quiz/adaptive', null, {
            params: { topic_id: topicId, question_count: questionCount || 5 },
        }),
    // Generate mock test using Gemini AI with optional answer hiding
    mockTest: (topicId?: string, topicName?: string, questionCount?: number, includeAnswers?: boolean) =>
        api.post('/ai/quiz/test/generate', null, {
            params: {
                ...(topicId && { topic_id: topicId }),
                ...(topicName && { topic_name: topicName }),
                question_count: questionCount || 10,
                include_answers: includeAnswers !== false,
            },
        }),
    // Get mock test for a specific topic using Gemini AI
    mockTestByTopic: (topicId: string, questionCount?: number, includeAnswers?: boolean) =>
        api.get(`/ai/quiz/test/topic/${topicId}`, {
            params: {
                question_count: questionCount || 10,
                include_answers: includeAnswers !== false,
            },
        }),
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

// ── Search ───────────────────────────────────────────────────────
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

// ── AI Content Generation ────────────────────────────────────────
export const aiAPI = {
    // Study Material
    studyMaterial: (topicId: string) =>
        api.get(`/ai/content/study-material/${topicId}`),
    
    // Explanations (all styles or specific ones)
    explanations: (topicId: string, styles?: string) =>
        api.get(`/ai/content/explanations/${topicId}`, { 
            params: styles ? { styles } : {} 
        }),
    
    // Full Content Package
    fullContent: (topicId: string, includeQuiz?: boolean, quizQuestions?: number) =>
        api.get(`/ai/content/full-content/${topicId}`, {
            params: { 
                include_quiz: includeQuiz !== false, 
                quiz_questions: quizQuestions || 4 
            }
        }),
    
    // Quiz endpoints
    testAI: (topicName: string, questionCount?: number) =>
        api.get(`/ai/quiz/test-ai`, {
            params: { topic_name: topicName, question_count: questionCount || 2 }
        }),
    
    quiz: (topicId: string, questionCount?: number, difficulty?: string) =>
        api.get(`/ai/quiz/quiz/${topicId}`, {
            params: { 
                question_count: questionCount || 5,
                difficulty: difficulty || 'mixed'
            }
        }),
    
    generateAdaptive: (topicId: string, questionCount?: number) =>
        api.get(`/ai/quiz/generate-adaptive`, {
            params: { 
                topic_id: topicId,
                question_count: questionCount || 5
            }
        }),
    
    mockTest: (topics: string[], totalQuestions?: number, difficultyEasy?: number, difficultyMedium?: number, difficultyHard?: number) =>
        api.post(`/ai/quiz/mock-test`, null, {
            params: {
                topics: JSON.stringify(topics),
                total_questions: totalQuestions || 10,
                difficulty_easy: difficultyEasy || 4,
                difficulty_medium: difficultyMedium || 4,
                difficulty_hard: difficultyHard || 2
            }
        }),
    
    
    evaluateQuiz: (answers: object) =>
        api.post(`/ai/quiz/evaluate`, answers),
    
    // Custom topic quiz - generate questions for ANY topic (not limited to database)
    customTopicQuiz: (topicName: string, questionCount?: number, difficulty?: string) =>
        api.post(`/ai/quiz/custom-topic`, null, {
            params: {
                topic_name: topicName,
                question_count: questionCount || 5,
                difficulty: difficulty || 'medium'
            }
        }),
};

export default api;
