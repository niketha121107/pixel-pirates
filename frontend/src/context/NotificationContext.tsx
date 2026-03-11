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
const CACHE_VERSION_KEY = 'edutwin-notifications-v';
const CURRENT_VERSION = '2'; // bump to invalidate stale mock data

function loadNotifications(): Notification[] {
    try {
        // Invalidate stale cached mock data from older versions
        if (localStorage.getItem(CACHE_VERSION_KEY) !== CURRENT_VERSION) {
            localStorage.removeItem(STORAGE_KEY);
            localStorage.setItem(CACHE_VERSION_KEY, CURRENT_VERSION);
            return [];
        }
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
    } catch { /* ignore */ }
    return [];
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
