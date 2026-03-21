import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Trophy, Target, CheckCircle2, XCircle, AlertCircle, Download, Share2, RotateCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

interface QuestionReview {
  id: string;
  question: string;
  options: string[];
  userAnswer: number;
  correctAnswer: number;
  isCorrect: boolean;
  explanation?: string;
}

interface TestResult {
  testId: string;
  score: number;
  totalQuestions: number;
  correctAnswers: number;
  wrongAnswers: number;
  skippedAnswers: number;
  percentage: number;
  timeSpent: number;
  violations: number;
  questionReview: QuestionReview[];
  categoryStats?: Record<string, { correct: number; total: number }>;
  timestamp: string;
}

interface MockTestResultsProps {
  testResults: TestResult;
}

export const MockTestResults = ({ testResults }: MockTestResultsProps) => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [expandedQuestion, setExpandedQuestion] = useState<string | null>(null);
  const [categoryData, setCategoryData] = useState<Array<{ name: string; correct: number; incorrect: number }>>([]);

  useEffect(() => {
    if (testResults.categoryStats) {
      const data = Object.entries(testResults.categoryStats).map(([category, stats]) => ({
        name: category,
        correct: stats.correct,
        incorrect: stats.total - stats.correct,
      }));
      setCategoryData(data);
    }
  }, [testResults.categoryStats]);

  const handleDownloadReport = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/mock-test/${testResults.testId}/report`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `mock-test-report-${testResults.timestamp}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentElement?.removeChild(link);
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  const handleRetakeTest = () => {
    navigate(`/dashboard/mock-tests/${testResults.testId}/retake`);
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'from-green-500 to-emerald-500';
    if (percentage >= 60) return 'from-blue-500 to-cyan-500';
    return 'from-red-500 to-pink-500';
  };

  const getScoreGrade = (percentage: number) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B';
    if (percentage >= 60) return 'C';
    return 'D';
  };

  const formatTime = (minutes: number) => {
    const mins = Math.floor(minutes / 60);
    const secs = minutes % 60;
    return `${mins}m ${secs}s`;
  };

  const COLORS = ['#56a565', '#ef4444', '#f97316', '#6b7280'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-500 to-red-500 text-white py-8 sm:py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
          >
            <Trophy className="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4" />
          </motion.div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-2">Test Completed!</h1>
          <p className="text-pink-100">Here's your performance summary</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Main Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-gradient-to-br ${getScoreColor(testResults.percentage)} rounded-2xl shadow-2xl p-8 sm:p-12 text-white mb-8`}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
            {/* Score Circle */}
            <div className="flex justify-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4, type: 'spring' }}
                className="relative w-40 h-40 rounded-full bg-white/20 flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="text-6xl font-bold">{getScoreGrade(testResults.percentage)}</div>
                  <div className="text-2xl font-semibold mt-2">{testResults.percentage}%</div>
                </div>
              </motion.div>
            </div>

            {/* Stats */}
            <div className="md:col-span-2 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-white/70 text-sm font-semibold">Score</p>
                  <p className="text-3xl font-bold">{testResults.score}</p>
                </div>
                <div>
                  <p className="text-white/70 text-sm font-semibold">Duration</p>
                  <p className="text-3xl font-bold">{formatTime(testResults.timeSpent)}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/30">
                <div className="text-center">
                  <p className="text-white/70 text-sm">Correct</p>
                  <p className="text-2xl font-bold text-green-200">{testResults.correctAnswers}</p>
                </div>
                <div className="text-center">
                  <p className="text-white/70 text-sm">Wrong</p>
                  <p className="text-2xl font-bold text-red-200">{testResults.wrongAnswers}</p>
                </div>
                <div className="text-center">
                  <p className="text-white/70 text-sm">Skipped</p>
                  <p className="text-2xl font-bold text-gray-200">{testResults.skippedAnswers}</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Charts */}
        {categoryData.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-8"
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance by Topic</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="correct" fill="#10b981" name="Correct" />
                  <Bar dataKey="incorrect" fill="#ef4444" name="Incorrect" />
                </BarChart>
              </ResponsiveContainer>

              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Correct', value: testResults.correctAnswers },
                      { name: 'Wrong', value: testResults.wrongAnswers },
                      { name: 'Skipped', value: testResults.skippedAnswers },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#ef4444" />
                    <Cell fill="#f97316" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}

        {/* Review Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Question Review</h2>

          <div className="space-y-3">
            {testResults.questionReview.map((q, idx) => (
              <motion.div
                key={q.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="border border-gray-200 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() =>
                    setExpandedQuestion(expandedQuestion === q.id ? null : q.id)
                  }
                  className="w-full p-4 flex items-start gap-4 hover:bg-gray-50 transition-colors"
                >
                  {/* Status Icon */}
                  <div className="flex-shrink-0 pt-1">
                    {q.isCorrect ? (
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                    ) : q.userAnswer === undefined ? (
                      <AlertCircle className="w-6 h-6 text-orange-500" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-500" />
                    )}
                  </div>

                  {/* Question */}
                  <div className="flex-1 text-left">
                    <p className="font-semibold text-gray-900 mb-2">
                      Q{idx + 1}: {q.question}
                    </p>
                    <div className="flex gap-4 text-sm">
                      {q.userAnswer !== undefined && (
                        <p className="text-gray-600">
                          Your answer:{' '}
                          <span className={q.isCorrect ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                            {String.fromCharCode(65 + q.userAnswer)}
                          </span>
                        </p>
                      )}
                      {!q.isCorrect && (
                        <p className="text-gray-600">
                          Correct answer:{' '}
                          <span className="text-green-600 font-semibold">
                            {String.fromCharCode(65 + q.correctAnswer)}
                          </span>
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Expand Icon */}
                  <div className="flex-shrink-0">
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform ${
                        expandedQuestion === q.id ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  </div>
                </button>

                {/* Expanded Content */}
                {expandedQuestion === q.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-t border-gray-200 bg-gray-50 p-4"
                  >
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">All Options:</h4>
                        <div className="space-y-2">
                          {q.options.map((option, idx) => (
                            <div
                              key={idx}
                              className={`p-3 rounded border-l-4 ${
                                idx === q.correctAnswer
                                  ? 'border-l-green-500 bg-green-50'
                                  : idx === q.userAnswer
                                  ? 'border-l-red-500 bg-red-50'
                                  : 'border-l-gray-300 bg-white'
                              }`}
                            >
                              <div className="flex gap-3">
                                <span className="font-semibold text-gray-900">
                                  {String.fromCharCode(65 + idx)}.
                                </span>
                                <span className="text-gray-700">{option}</span>
                                {idx === q.correctAnswer && (
                                  <span className="ml-auto text-green-600 font-semibold text-sm">✓ Correct</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {q.explanation && (
                        <div className="p-4 bg-blue-50 rounded border border-blue-200">
                          <h4 className="font-semibold text-blue-900 mb-2">Explanation:</h4>
                          <p className="text-blue-800">{q.explanation}</p>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          <button
            onClick={() => navigate('/dashboard/mock-tests')}
            className="px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-semibold hover:bg-gray-300 transition-all"
          >
            Back to Tests
          </button>

          <button
            onClick={handleRetakeTest}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition-all flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Retake Test
          </button>

          <button
            onClick={handleDownloadReport}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download Report
          </button>
        </motion.div>
      </div>
    </div>
  );
};
