import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SignIn } from './pages/SignIn';
import { SignUp } from './pages/SignUp';
import { Dashboard } from './pages/Dashboard';
import { TopicView } from './pages/TopicView';
import { QuizPage } from './pages/QuizPage';
import { Analytics } from './pages/Analytics';
import { Leaderboard } from './pages/Leaderboard';
import { Progress } from './pages/Progress';
import { UserProfile } from './pages/UserProfile';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/topic" element={<TopicView />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/progress" element={<Progress />} />
        <Route path="/profile" element={<UserProfile />} />

        {/* Default fallback */}
        <Route path="*" element={<Navigate to="/signin" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
