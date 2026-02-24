import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import { UserPreferencesProvider } from './context/UserPreferencesContext.tsx';
import { NotificationProvider } from './context/NotificationContext.tsx';
import { UnderstandingProvider } from './context/UnderstandingContext.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <UserPreferencesProvider>
      <NotificationProvider>
        <UnderstandingProvider>
          <App />
        </UnderstandingProvider>
      </NotificationProvider>
    </UserPreferencesProvider>
  </StrictMode>,
);
