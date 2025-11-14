import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Clock, Thermometer, Droplets, Wind, Sun, Moon, Mail, Calendar, Users } from 'lucide-react';
import { API_BASE_URL } from '../config';

const SituationalAwareness = () => {
  const [time, setTime] = useState(new Date());
  const [saData, setSaData] = useState({ mode: 'weather', content: 'Loading...', priority: 4 });

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchSA = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/situational-awareness`);
        if (response.ok) {
          const data = await response.json();
          setSaData(data || { mode: 'weather', content: 'No data', priority: 4 });
        }
      } catch (error) {
        console.error('Failed to fetch SA:', error);
      }
    };

    fetchSA();
    const saTimer = setInterval(fetchSA, 60000); // Poll every 60s
    return () => clearInterval(saTimer);
  }, []);

  const isDay = time.getHours() >= 6 && time.getHours() < 18;

  const getIcon = (mode) => {
    switch (mode) {
      case 'email': return <Mail className="w-6 h-6 text-blue-400 drop-shadow-lg" />;
      case 'event': return <Calendar className="w-6 h-6 text-green-400 drop-shadow-lg" />;
      case 'gathering': return <Users className="w-6 h-6 text-purple-400 drop-shadow-lg" />;
      default: return <Thermometer className="w-6 h-6 text-red-400 drop-shadow-lg" />;
    }
  };

  return (
    <div className="glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20">
      <h2 className="text-xl font-bold text-cyan-400 mb-4 drop-shadow-lg">Situational Awareness</h2>

      <div className="space-y-4">
        {/* Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-3"
        >
          {isDay ? <Sun className="w-6 h-6 text-yellow-400 drop-shadow-lg" /> : <Moon className="w-6 h-6 text-cyan-400 drop-shadow-lg" />}
          <div>
            <p className="text-sm text-gray-400">Current Time</p>
            <p className="text-lg font-mono text-gray-200">{time.toLocaleTimeString()}</p>
          </div>
        </motion.div>

        {/* Situational Awareness */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center space-x-3"
        >
          {getIcon(saData.mode)}
          <div>
            <p className="text-sm text-gray-400 capitalize">{saData.mode || 'Status'}</p>
            <p className="text-lg font-mono text-gray-200">{saData.content || 'No data'}</p>
            <p className="text-xs text-gray-500">Priority: {saData.priority || 4}</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SituationalAwareness;