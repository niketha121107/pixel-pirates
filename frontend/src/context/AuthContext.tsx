import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User } from '../types';
import { authAPI } from '../services/api';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
    backendError: boolean;
    login: (email: string, password: string) => Promise<true | string>;
    signup: (name: string, email: string, password: string) => Promise<boolean | string>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [backendError, setBackendError] = useState(false);

    const buildSuspensionMessage = (detail: unknown) => {
        if (!detail || typeof detail !== 'object') {
            return 'Your account is temporarily suspended because of repeated mock test violations.';
        }

        const suspensionDetail = detail as { message?: string; suspendedUntil?: string };
        const baseMessage = suspensionDetail.message || 'Your account is temporarily suspended because of repeated mock test violations.';

        if (!suspensionDetail.suspendedUntil) {
            return baseMessage;
        }

        return `${baseMessage} Try again after ${new Date(suspensionDetail.suspendedUntil).toLocaleString()}.`;
    };

    // Auto-login from stored token on mount
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            authAPI.me()
                .then(res => { setUser(res.data as User); setBackendError(false); })
                .catch((err) => {
                    localStorage.removeItem('token');
                    if (err?.isNetworkError || err?.code === 'ERR_NETWORK') {
                        setBackendError(true);
                    }
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email: string, password: string): Promise<true | string> => {
        try {
            const res = await authAPI.login(email, password);
            const { access_token, user: userData } = res.data;
            localStorage.setItem('token', access_token);
            setUser(userData as User);
            setBackendError(false);
            return true;
        } catch (err: unknown) {
            const error = err as { isNetworkError?: boolean; code?: string; response?: { status?: number; data?: { detail?: unknown } } };
            if (error?.isNetworkError || error?.code === 'ERR_NETWORK') {
                setBackendError(true);
                return 'Cannot connect to server. Please make sure the backend is running (cd backend && python main.py)';
            }
            if (error?.response?.status === 423) {
                return buildSuspensionMessage(error.response.data?.detail);
            }
            return 'Invalid email or password';
        }
    };

    const signup = async (name: string, email: string, password: string): Promise<boolean | string> => {
        try {
            const res = await authAPI.signup(name, email, password);
            const { access_token, user: userData } = res.data;
            localStorage.setItem('token', access_token);
            setUser(userData as User);
            setBackendError(false);
            return true;
        } catch (err: unknown) {
            const error = err as { isNetworkError?: boolean; code?: string; response?: { status?: number } };
            if (error?.isNetworkError || error?.code === 'ERR_NETWORK') {
                setBackendError(true);
            }
            if (error?.response?.status === 409) {
                return 'email_exists';
            }
            return false;
        }
    };

    const logout = () => {
        authAPI.logout().catch(() => {});
        localStorage.removeItem('token');
        setUser(null);
    };

    const refreshUser = async () => {
        try {
            const res = await authAPI.me();
            setUser(res.data as User);
        } catch (err) {
            // Silently fail - user data remains unchanged
        }
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, backendError, login, signup, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
