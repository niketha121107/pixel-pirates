<<<<<<< HEAD
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
=======
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
>>>>>>> fff541230f2ea326096f9f7bf3bb0b31c06d86a8
