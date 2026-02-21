import { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types';
import { mockUser } from '../data/mockData';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => boolean;
    signup: (name: string, email: string, password: string) => boolean;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);

    const login = (email: string, _password: string): boolean => {
        if (email) {
            setUser({ ...mockUser, email });
            return true;
        }
        return false;
    };

    const signup = (name: string, email: string, _password: string): boolean => {
        if (name && email) {
            setUser({ ...mockUser, name, email, completedTopics: [], pendingTopics: ['topic-1', 'topic-2', 'topic-3', 'topic-4', 'topic-5'], inProgressTopics: [], videosWatched: [], totalScore: 0, rank: 5 });
            return true;
        }
        return false;
    };

    const logout = () => setUser(null);

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
