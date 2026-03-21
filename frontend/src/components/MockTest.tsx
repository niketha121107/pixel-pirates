import { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, AlertTriangle, Send, ChevronLeft, ChevronRight, BookOpen, Flag } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { MockTestResults } from './MockTestResults';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct_option: number;
  explanation?: string;
  topic_id?: string;
}

interface MockTestProps {
  testId: string;
  duration: number; // in minutes
  questionCount: number;
  topic?: string;
}

export const MockTest = ({
  testId,
  duration: initialDuration,
  questionCount,
  topic,
}: MockTestProps) => {
  const { token } = useAuth();
  const navigate = useNavigate();

  // State
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, number | null>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [timeLeft, setTimeLeft] = useState(initialDuration * 60);
  const [violations, setViolations] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<string>>(new Set());

  // Refs for event tracking
  const lastActivityRef = useRef<number>(Date.now());
  const documentHiddenRef = useRef(false);
  const keyPressCountRef = useRef(0);
  const keyPressTimeRef = useRef<number>(Date.now());

  // Fetch questions
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/mock-test/${testId}/questions`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setQuestions(response.data.questions);
        // Initialize answers
        const initialAnswers: Record<string, number | null> = {};
        response.data.questions.forEach((q: Question) => {
          initialAnswers[q.id] = null;
        });
        setAnswers(initialAnswers);
      } catch (error) {
        console.error('Error fetching questions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [testId, token]);

  // Timer logic
  useEffect(() => {
    if (submitted || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleTestSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [submitted]);

  // Anti-cheat monitoring
  useEffect(() => {
    if (submitted || violations >= 11) return;

    const handleVisibilityChange = () => {
      if (document.hidden && !documentHiddenRef.current) {
        documentHiddenRef.current = true;
        addViolation('Tab switching detected');
      } else if (!document.hidden && documentHiddenRef.current) {
        documentHiddenRef.current = false;
      }
    };

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      addViolation('Right-click not allowed');
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      const now = Date.now();
      
      // Check for Ctrl+C (copy)
      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        e.preventDefault();
        addViolation('Copy attempt detected');
      }
      
      // Check for print screen
      if (e.key === 'PrintScreen') {
        e.preventDefault();
        addViolation('Screenshot attempt detected');
      }

      // Rapid key press detection
      if (now - keyPressTimeRef.current < 500) {
        keyPressCountRef.current++;
        if (keyPressCountRef.current > 50) {
          addViolation('Rapid input detected - possible bot activity');
          keyPressCountRef.current = 0;
        }
      } else {
        keyPressCountRef.current = 1;
      }
      keyPressTimeRef.current = now;
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);

    // Prevent zooming
    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault();
        addViolation('Zoom attempt detected');
      }
    };
    document.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('wheel', handleWheel);
    };
  }, [violations, submitted]);

  const addViolation = useCallback(
    (reason: string) => {
      setViolations((prev) => {
        const newViolations = prev + 1;
        console.warn(`⚠️ Violation #${newViolations}: ${reason}`);

        if (newViolations >= 11) {
          handleTestSubmit();
        }

        return newViolations;
      });
    },
    []
  );

  // Auto-save answers
  useEffect(() => {
    const saveAnswers = async () => {
      try {
        await axios.post(
          `${import.meta.env.VITE_API_URL}/api/mock-test/${testId}/auto-save`,
          { answers },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      } catch (error) {
        console.error('Error auto-saving:', error);
      }
    };

    const timer = setInterval(saveAnswers, 30000); // Auto-save every 30 seconds
    return () => clearInterval(timer);
  }, [testId, token, answers]);

  const handleAnswerSelect = (optionIndex: number) => {
    if (submitted) return;
    
    const currentQuestion = questions[currentIndex];
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIndex,
    }));
    lastActivityRef.current = Date.now();
  };

  const handleFlagQuestion = () => {
    const currentQuestion = questions[currentIndex];
    setFlaggedQuestions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(currentQuestion.id)) {
        newSet.delete(currentQuestion.id);
      } else {
        newSet.add(currentQuestion.id);
      }
      return newSet;
    });
  };

  const handleTestSubmit = async () => {
    setSubmitted(true);
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/mock-test/${testId}/submit`,
        {
          answers,
          timeSpent: initialDuration * 60 - timeLeft,
          violations,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setTestResults(response.data);
    } catch (error) {
      console.error('Error submitting test:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    if (timeLeft <= 60) return 'text-red-600';
    if (timeLeft <= 300) return 'text-orange-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin">
          <BookOpen className="w-12 h-12 text-pink-500" />
        </div>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="flex items-center justify-center min-h-screen text-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">No questions available</h2>
          <button
            onClick={() => navigate('/dashboard/mock-tests')}
            className="mt-4 px-6 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600"
          >
            Back to Mock Tests
          </button>
        </div>
      </div>
    );
  }

  if (submitted && testResults) {
    return <MockTestResults testResults={testResults} />;
  }

  const currentQuestion = questions[currentIndex];
  const currentAnswer = answers[currentQuestion.id];
  const isCurrentFlagged = flaggedQuestions.has(currentQuestion.id);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-pink-500" />
              <div>
                <h1 className="font-bold text-gray-900">{topic || 'Mock Test'}</h1>
                <p className="text-sm text-gray-600">Question {currentIndex + 1} of {questions.length}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Violations Counter */}
            {violations > 0 && (
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <span className={`font-semibold ${violations >= 10 ? 'text-red-600' : 'text-orange-600'}`}>
                  {violations} warning{violations !== 1 ? 's' : ''}
                </span>
              </div>
            )}

            {/* Timer */}
            <div className={`flex items-center gap-2 font-mono font-bold text-lg ${getTimeColor()}`}>
              <Clock className="w-5 h-5" />
              <span>{formatTime(timeLeft)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Question Area */}
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 sm:p-8"
          >
            {/* Question */}
            <div className="mb-8">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 leading-relaxed">
                {currentQuestion.question}
              </h2>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-8">
              {currentQuestion.options.map((option, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleAnswerSelect(index)}
                  disabled={submitted}
                  className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                    currentAnswer === index
                      ? 'border-pink-500 bg-pink-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  } ${submitted ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-sm ${
                        currentAnswer === index
                          ? 'border-pink-500 bg-pink-500 text-white'
                          : 'border-gray-300'
                      }`}
                    >
                      {String.fromCharCode(65 + index)}
                    </div>
                    <span className="text-base text-gray-800">{option}</span>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-6 border-t border-gray-200">
              <button
                onClick={handleFlagQuestion}
                className={`px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all ${
                  isCurrentFlagged
                    ? 'bg-orange-100 text-orange-700 border border-orange-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                }`}
              >
                <Flag className={`w-4 h-4 ${isCurrentFlagged ? 'fill-current' : ''}`} />
                {isCurrentFlagged ? 'Flagged' : 'Flag for Review'}
              </button>
            </div>
          </motion.div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Question Navigator */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">Questions</h3>
              <div className="grid grid-cols-5 gap-2 max-h-96 overflow-y-auto">
                {questions.map((q, idx) => (
                  <button
                    key={q.id}
                    onClick={() => setCurrentIndex(idx)}
                    disabled={submitted}
                    className={`aspect-square rounded-lg font-bold text-sm transition-all flex items-center justify-center ${
                      idx === currentIndex
                        ? 'bg-pink-500 text-white scale-110'
                        : answers[q.id] !== null
                        ? 'bg-green-100 text-green-700 border-2 border-green-300'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    } ${flaggedQuestions.has(q.id) ? 'ring-2 ring-orange-400' : ''}`}
                  >
                    {idx + 1}
                  </button>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-gray-200"></div>
                  <span className="text-gray-600">Not Answered</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-green-100 border border-green-300"></div>
                  <span className="text-gray-600">Answered</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded ring-2 ring-orange-400"></div>
                  <span className="text-gray-600">Flagged</span>
                </div>
              </div>
            </div>

            {/* Test Progress */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">Progress</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Questions Answered</span>
                    <span className="font-semibold text-gray-900">
                      {Object.values(answers).filter((a) => a !== null).length} / {questions.length}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          (Object.values(answers).filter((a) => a !== null).length /
                            questions.length) *
                          100
                        }%`,
                      }}
                    ></div>
                  </div>
                </div>
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    {flaggedQuestions.size > 0 && `${flaggedQuestions.size} flagged for review`}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex gap-3 justify-between">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
            disabled={currentIndex === 0 || submitted}
            className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleTestSubmit()}
            disabled={submitted}
            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white rounded-lg font-semibold hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
            Submit Test
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setCurrentIndex(Math.min(questions.length - 1, currentIndex + 1))}
            disabled={currentIndex === questions.length - 1 || submitted}
            className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-5 h-5" />
          </motion.button>
        </div>
      </div>
    </div>
  );
};
