import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { GlassCard } from '../ui/GlassCard';
import { motion } from 'framer-motion';

interface LearningProgressGraphProps {
  data?: Array<{ day: string; xp: number }>;
}

const getEngagementLabel = (value: number): string => {
  if (value === 0) return 'No engagement';
  if (value <= 0.25) return 'Low (1-25%)';
  if (value <= 0.5) return 'Medium (26-50%)';
  if (value <= 0.75) return 'High (51-75%)';
  return 'Full (76-100%)';
};

const getEngagementColor = (value: number): string => {
  if (value === 0) return 'text-gray-400';
  if (value <= 0.25) return 'text-orange-500';
  if (value <= 0.5) return 'text-amber-500';
  if (value <= 0.75) return 'text-pink-500';
  return 'text-green-500';
};

export const LearningProgressGraph = ({ data }: LearningProgressGraphProps) => {
  // Use provided data or show empty state if no data (no random mock data)
  const chartData = data && data.length > 0 ? data : (() => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map(day => ({
      day,
      xp: 0, // Start with 0, will update as user completes activities
    }));
  })();

  // Custom tooltip component with engagement level info
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const value = payload[0].value;
      const engagementLabel = getEngagementLabel(value);
      const scoreRange = value <= 0 ? '0%' : value < 0.25 ? '1-25%' : value < 0.5 ? '26-50%' : value < 0.75 ? '51-75%' : '76-100%';
      
      return (
        <div className="bg-white/90 backdrop-blur-xl rounded-lg px-4 py-3 shadow-lg border border-white/20">
          <p className="text-sm font-semibold text-gray-800">{payload[0].payload.day}</p>
          <p className="text-sm font-bold text-brand">Engagement: {(value * 100).toFixed(0)}%</p>
          <p className="text-xs text-gray-600 mt-1">{engagementLabel}</p>
          <p className="text-xs text-gray-500">Score Range: {scoreRange}</p>
        </div>
      );
    }
    return null;
  };

  // Calculate statistics
  const maxEngagement = Math.max(...chartData.map(d => d.xp || 0), 1);
  const avgEngagement = chartData.length > 0 ? chartData.reduce((sum, d) => sum + (d.xp || 0), 0) / chartData.length : 0;
  const daysWithProgress = chartData.filter(d => d.xp > 0).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="w-full"
    >
      <GlassCard className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Learning Progress</h2>
            <p className="text-xs text-gray-500 mt-1">Daily engagement levels over the past 7 days</p>
          </div>
          <div className="text-right text-xs space-y-1">
            <div>
              <span className="text-gray-600">Peak: </span>
              <span className={`font-bold ${getEngagementColor(maxEngagement)}`}>{(maxEngagement * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-600">Average: </span>
              <span className={`font-bold ${getEngagementColor(avgEngagement)}`}>{(avgEngagement * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-600">Active Days: </span>
              <span className="font-bold text-brand">{daysWithProgress}/7</span>
            </div>
          </div>
        </div>
        
        <div className="w-full h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
              <XAxis 
                dataKey="day" 
                stroke="rgba(107, 114, 128, 0.5)"
                style={{ fontSize: '14px' }}
              />
              <YAxis 
                stroke="rgba(107, 114, 128, 0.5)"
                style={{ fontSize: '14px' }}
                domain={[0, 1]}
                label={{ 
                  value: 'Engagement Level', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { fontSize: '12px', fill: 'rgba(107, 114, 128, 0.7)' }
                }}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(236, 72, 153, 0.2)', strokeWidth: 2 }} />
              <Line
                type="monotone"
                dataKey="xp"
                stroke="#ec4899"
                strokeWidth={3}
                dot={{ fill: '#ec4899', r: 5 }}
                activeDot={{ r: 7 }}
                isAnimationActive={true}
                name="Engagement"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
          <div className="bg-gradient-to-r from-orange-50 to-amber-50 p-2 rounded border border-orange-100">
            <p className="text-orange-700 font-semibold">Low: 1-25% score</p>
          </div>
          <div className="bg-gradient-to-r from-amber-50 to-pink-50 p-2 rounded border border-amber-100">
            <p className="text-amber-700 font-semibold">Medium: 26-50% score</p>
          </div>
          <div className="bg-gradient-to-r from-pink-50 to-pink-100 p-2 rounded border border-pink-100">
            <p className="text-pink-700 font-semibold">High: 51-75% score</p>
          </div>
          <div className="bg-gradient-to-r from-green-50 to-green-100 p-2 rounded border border-green-100">
            <p className="text-green-700 font-semibold">Full: 76-100% score</p>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
};
