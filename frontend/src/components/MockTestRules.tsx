import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Shield, Eye, Copy, RefreshCw, Clock, Ban } from 'lucide-react';
import { GradientButton } from './ui/GradientButton';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

interface MockTestRulesProps {
  onAccept: () => void;
  onCancel: () => void;
}

export const MockTestRules = ({ onAccept, onCancel }: MockTestRulesProps) => {
  const { token } = useAuth();
  const [rules, setRules] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/mock-test/rules`,
          {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }
        );
        setRules(response.data.rules || []);
      } catch (error) {
        console.error('Error fetching rules:', error);
        setRules([
          'Complete the entire test without leaving the page',
          'Do not take screenshots during the test',
          'Do not copy or paste questions',
          'Do not switch tabs or windows',
          'You have 10 warnings - 11th violation = 6-hour suspension',
          'All activities are monitored by anti-cheat system',
          'Answers are auto-saved',
          'Cannot navigate away until test completion',
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, [token]);

  const iconMap: Record<string, React.ReactNode> = {
    screenshot: <Eye className="w-5 h-5" />,
    copy: <Copy className="w-5 h-5" />,
    switch: <RefreshCw className="w-5 h-5" />,
    duration: <Clock className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
    suspension: <Ban className="w-5 h-5" />,
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-pink-500 p-6 sm:p-8 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-8 h-8" />
            <h2 className="text-2xl sm:text-3xl font-bold">Mock Test Rules & Security Policy</h2>
          </div>
          <p className="text-red-100">Important: Read and understand these rules before proceeding</p>
        </div>

        {/* Rules Content */}
        <div className="p-6 sm:p-8">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin">
                <Shield className="w-8 h-8 text-pink-500" />
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map((rule, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50 transition-all"
                >
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-pink-500 text-white text-sm font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <p className="text-gray-700 text-sm sm:text-base leading-relaxed">{rule}</p>
                </motion.div>
              ))}
            </div>
          )}

          {/* Warning Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-8 p-4 bg-red-50 border-2 border-red-300 rounded-lg"
          >
            <div className="flex gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-red-800">Important: Account Suspension Warning</h3>
                <p className="text-red-700 text-sm mt-2">
                  Violations of these rules will result in warnings. <strong>On your 11th violation, your account will be automatically suspended for 6 hours</strong>. After suspension lifts and you log back in, your warning counter resets to zero.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Acknowledgment Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mt-8 p-4 bg-blue-50 border-2 border-blue-300 rounded-lg"
          >
            <p className="text-blue-800 text-sm">
              By clicking "I Accept & Agree", you acknowledge that you have read and understood all mock test rules, and agree to comply with our anti-cheat security measures.
            </p>
          </motion.div>
        </div>

        {/* Action Buttons */}
        <div className="bg-gray-50 px-6 sm:px-8 py-4 sm:py-6 flex gap-3 sm:gap-4 border-t border-gray-200">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-3 sm:py-4 rounded-lg border-2 border-gray-300 text-gray-700 font-semibold hover:border-gray-400 hover:bg-gray-100 transition-all text-sm sm:text-base"
          >
            Cancel
          </button>
          <button
            onClick={onAccept}
            className="flex-1 px-4 py-3 sm:py-4 rounded-lg bg-gradient-to-r from-pink-500 to-red-500 text-white font-semibold hover:shadow-lg hover:scale-[1.02] transition-all text-sm sm:text-base"
          >
            I Accept & Agree
          </button>
        </div>
      </motion.div>
    </div>
  );
};
