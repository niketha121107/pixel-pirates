import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

export type NotificationType = 'reminder' | 'congrats' | 'info';

export interface Notification {
    id: string;
    type: NotificationType;
    title: string;
    message: string;
    timestamp: number;
    read: boolean;
    topicId?: number;
}

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    addNotification: (n: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
    markAsRead: (id: string) => void;
    markAllAsRead: () => void;
    clearAll: () => void;
}

const STORAGE_KEY = 'edutwin-notifications';

// ─── Pending topics (mirrors Dashboard mock data) ────────────────
const PENDING_TOPICS = [
    { id: 6, title: 'Advanced Iterators & Generators', lang: 'Python' },
    { id: 7, title: 'Red-Black Trees', lang: 'Java' },
    { id: 8, title: 'Memory Management', lang: 'C' },
    { id: 9, title: 'Async/Await Patterns', lang: 'JavaScript' },
    { id: 10, title: 'Graph Algorithms', lang: 'Python' },
    { id: 11, title: 'Dynamic Programming', lang: 'C++' },
    { id: 12, title: 'REST API Design', lang: 'JSON' },
];

const COMPLETED_TOPICS = [
    { id: 1, title: 'Python Functions & Scope', lang: 'Python' },
    { id: 2, title: 'Java OOP Basics', lang: 'Java' },
    { id: 3, title: 'C Pointers Introduction', lang: 'C' },
    { id: 4, title: 'Data Structures Overview', lang: 'Python' },
    { id: 5, title: 'SQL Fundamentals', lang: 'SQL' },
];

function generateDefaultNotifications(): Notification[] {
    const now = Date.now();
    const notifications: Notification[] = [];

    // Reminder notifications for pending topics
    PENDING_TOPICS.forEach((topic, i) => {
        notifications.push({
            id: `reminder-${topic.id}`,
            type: 'reminder',
            title: 'Pending: Complete this topic',
            message: `You haven't completed "${topic.title}" (${topic.lang}) yet. Continue learning to stay on track!`,
            timestamp: now - (i + 1) * 3600_000, // staggered by 1h each
            read: false,
            topicId: topic.id,
        });
    });

    // Congrats notifications for completed topics
    COMPLETED_TOPICS.forEach((topic, i) => {
        notifications.push({
            id: `congrats-${topic.id}`,
            type: 'congrats',
            title: 'Congratulations! Topic completed 🎉',
            message: `Great job finishing "${topic.title}"! Keep up the awesome work.`,
            timestamp: now - (i + 8) * 3600_000,
            read: true,
            topicId: topic.id,
        });
    });

    return notifications.sort((a, b) => b.timestamp - a.timestamp);
}

function loadNotifications(): Notification[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
    } catch { /* ignore */ }
    const defaults = generateDefaultNotifications();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaults));
    return defaults;
}

function persist(notifications: Notification[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications));
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
    const [notifications, setNotifications] = useState<Notification[]>(loadNotifications);

    const unreadCount = notifications.filter(n => !n.read).length;

    const addNotification = useCallback((n: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
        setNotifications(prev => {
            const next: Notification[] = [
                { ...n, id: `${n.type}-${Date.now()}`, timestamp: Date.now(), read: false },
                ...prev,
            ];
            persist(next);
            return next;
        });
    }, []);

    const markAsRead = useCallback((id: string) => {
        setNotifications(prev => {
            const next = prev.map(n => n.id === id ? { ...n, read: true } : n);
            persist(next);
            return next;
        });
    }, []);

    const markAllAsRead = useCallback(() => {
        setNotifications(prev => {
            const next = prev.map(n => ({ ...n, read: true }));
            persist(next);
            return next;
        });
    }, []);

    const clearAll = useCallback(() => {
        setNotifications([]);
        persist([]);
    }, []);

    return (
        <NotificationContext.Provider value={{ notifications, unreadCount, addNotification, markAsRead, markAllAsRead, clearAll }}>
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotifications = (): NotificationContextType => {
    const ctx = useContext(NotificationContext);
    if (!ctx) throw new Error('useNotifications must be used within NotificationProvider');
    return ctx;
};
