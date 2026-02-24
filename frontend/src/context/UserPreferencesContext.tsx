import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { WallpaperOption } from '../components/profile/WallpaperSettings';
import { WALLPAPERS } from '../components/profile/WallpaperSettings';

interface UserPreferences {
    avatar: string;
    wallpaperId: string;
    wallpaper: WallpaperOption;
}

interface UserPreferencesContextType {
    preferences: UserPreferences;
    savePreferences: (avatar: string, wallpaperId: string) => void;
}

const DEFAULT_AVATAR = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4';
const DEFAULT_WALLPAPER_ID = 'default';

const getWallpaperById = (id: string): WallpaperOption =>
    WALLPAPERS.find(w => w.id === id) || WALLPAPERS[0];

function loadPreferences(): UserPreferences {
    try {
        const raw = localStorage.getItem('edutwin-user-preferences');
        if (raw) {
            const parsed = JSON.parse(raw);
            return {
                avatar: parsed.avatar || DEFAULT_AVATAR,
                wallpaperId: parsed.wallpaperId || DEFAULT_WALLPAPER_ID,
                wallpaper: getWallpaperById(parsed.wallpaperId || DEFAULT_WALLPAPER_ID),
            };
        }
    } catch {
        // ignore
    }
    return {
        avatar: DEFAULT_AVATAR,
        wallpaperId: DEFAULT_WALLPAPER_ID,
        wallpaper: getWallpaperById(DEFAULT_WALLPAPER_ID),
    };
}

const UserPreferencesContext = createContext<UserPreferencesContextType | null>(null);

export const UserPreferencesProvider = ({ children }: { children: ReactNode }) => {
    const [preferences, setPreferences] = useState<UserPreferences>(loadPreferences);

    const savePreferences = (avatar: string, wallpaperId: string) => {
        const wp = getWallpaperById(wallpaperId);
        const newPrefs: UserPreferences = { avatar, wallpaperId, wallpaper: wp };
        setPreferences(newPrefs);
        localStorage.setItem('edutwin-user-preferences', JSON.stringify({ avatar, wallpaperId }));
    };

    return (
        <UserPreferencesContext.Provider value={{ preferences, savePreferences }}>
            {children}
        </UserPreferencesContext.Provider>
    );
};

export const useUserPreferences = (): UserPreferencesContextType => {
    const ctx = useContext(UserPreferencesContext);
    if (!ctx) throw new Error('useUserPreferences must be used within UserPreferencesProvider');
    return ctx;
};
