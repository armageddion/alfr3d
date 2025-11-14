import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Clock, Thermometer, Droplets, Wind, Sun, Moon } from 'lucide-react';
import { API_BASE_URL } from '../config';

const SituationalAwareness = () => {
  const [time, setTime] = useState(new Date());
  const [weather, setWeather] = useState({ high: 72, humidity: 45, description: 'Loading...' });

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/weather`);
        if (response.ok) {
          const data = await response.json();
          setWeather({
            high: data.high || 72,
            humidity: data.humidity || 45,
            description: data.description || 'Unknown'
          });
        }
      } catch (error) {
        console.error('Failed to fetch weather:', error);
      }
    };

    fetchWeather();
    const weatherTimer = setInterval(fetchWeather, 300000); // Update every 5 minutes
    return () => clearInterval(weatherTimer);
  }, []);

  const isDay = time.getHours() >= 6 && time.getHours() < 18;

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

        {/* Weather */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center space-x-3"
        >
          <Thermometer className="w-6 h-6 text-red-400 drop-shadow-lg" />
          <div>
            <p className="text-sm text-gray-400">Temperature</p>
            <p className="text-lg font-mono text-gray-200">{weather.high}°C</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center space-x-3"
        >
          <Droplets className="w-6 h-6 text-blue-400 drop-shadow-lg" />
          <div>
            <p className="text-sm text-gray-400">Humidity</p>
            <p className="text-lg font-mono text-gray-200">{weather.humidity}%</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex items-center space-x-3"
        >
          <Wind className="w-6 h-6 text-green-400 drop-shadow-lg" />
          <div>
            <p className="text-sm text-gray-400">Weather</p>
            <p className="text-lg font-mono text-gray-200 capitalize">{weather.description}</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SituationalAwareness;