import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import { AuthProvider } from './context/AuthContext.tsx';
import { UserPreferencesProvider } from './context/UserPreferencesContext.tsx';
import { NotificationProvider } from './context/NotificationContext.tsx';
import { UnderstandingProvider } from './context/UnderstandingContext.tsx';
import { AntiCheatProvider } from './context/AntiCheatContext.tsx';
import { LearningTimerProvider } from './context/LearningTimerContext.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <UserPreferencesProvider>
        <NotificationProvider>
          <UnderstandingProvider>
            <AntiCheatProvider>
              <LearningTimerProvider>
                <App />
              </LearningTimerProvider>
            </AntiCheatProvider>
          </UnderstandingProvider>
        </NotificationProvider>
      </UserPreferencesProvider>
    </AuthProvider>
  </StrictMode>,
);
