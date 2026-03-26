import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { GlassCard } from '../ui/GlassCard';
import { motion } from 'framer-motion';

interface LearningProgressGraphProps {
  data?: Array<{ day: string; xp: number }>;
}

export const LearningProgressGraph = ({ data }: LearningProgressGraphProps) => {
  // Use provided data or show empty state if no data (no random mock data)
  const chartData = data && data.length > 0 ? data : (() => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days.map(day => ({
      day,
      xp: 0, // Start with 0, will update as user completes activities
    }));
  })();

  // Custom tooltip component
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/90 backdrop-blur-xl rounded-lg px-3 py-2 shadow-lg border border-white/20">
          <p className="text-sm font-semibold text-gray-800">{payload[0].payload.day}</p>
          <p className="text-sm font-bold text-brand">xp: {payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="w-full"
    >
      <GlassCard className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Learning Progress</h2>
        
        <div className="w-full h-72 min-h-[288px]" style={{ minWidth: '100%' }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={280}>
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
                domain={[0, 'auto']}
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
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <p className="text-xs text-gray-500 mt-4">
          Your daily learning engagement over the past week
        </p>
      </GlassCard>
    </motion.div>
  );
};
