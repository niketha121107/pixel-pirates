import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { SignIn } from './pages/SignIn';
import { SignUp } from './pages/SignUp';
import { TopicView } from './pages/TopicView';
import { QuizPage } from './pages/QuizPage';
import { Analytics } from './pages/Analytics';
import { Progress } from './pages/Progress';
import { UserProfile } from './pages/UserProfile';
import { VideoRecommendations } from './pages/VideoRecommendations';
import { MockTest } from './pages/MockTest';
import { AIChat } from './pages/AIChat';
import { Notes } from './pages/Notes';
import { PDFViewer } from './pages/PDFViewer';
import { StudyMaterial } from './pages/StudyMaterial';
import ProtectedRoute from './components/ProtectedRoute';

function AppRoutes() {
  const location = useLocation();

  useEffect(() => {
    const allowSelectionPaths = ['/study-material', '/pdf-viewer'];
    const shouldAllowSelection = allowSelectionPaths.some((p) => location.pathname.startsWith(p));

    if (shouldAllowSelection) {
      document.body.classList.remove('app-lock-selection');
    } else {
      document.body.classList.add('app-lock-selection');
    }

    return () => {
      document.body.classList.remove('app-lock-selection');
    };
  }, [location.pathname]);

  return (
    <Routes>
      <Route path="/signin" element={<SignIn />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
      <Route path="/topic" element={<ProtectedRoute><TopicView /></ProtectedRoute>} />
      <Route path="/quiz" element={<ProtectedRoute><QuizPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
      <Route path="/notes" element={<ProtectedRoute><Notes /></ProtectedRoute>} />
      <Route path="/videos" element={<ProtectedRoute><VideoRecommendations /></ProtectedRoute>} />
      <Route path="/mock-test" element={<ProtectedRoute><MockTest /></ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute><AIChat /></ProtectedRoute>} />
      <Route path="/pdf-viewer" element={<ProtectedRoute><PDFViewer /></ProtectedRoute>} />
      <Route path="/study-material" element={<ProtectedRoute><StudyMaterial /></ProtectedRoute>} />

      {/* Default: authenticated users go to profile, others to signin */}
      <Route path="*" element={<Navigate to="/signin" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
