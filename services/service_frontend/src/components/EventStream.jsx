import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';

const events = [
  { id: 'event1', type: 'info', message: 'System initialized successfully', time: '10:30 AM' },
  { id: 'event2', type: 'warning', message: 'Device service latency detected', time: '10:25 AM' },
  { id: 'event3', type: 'success', message: 'User authentication completed', time: '10:20 AM' },
  { id: 'event4', type: 'info', message: 'Environment data updated', time: '10:15 AM' },
];

const EventStream = () => {
  const [displayedEvents, setDisplayedEvents] = useState([]);

  useEffect(() => {
    events.forEach((event, index) => {
      setTimeout(() => {
        setDisplayedEvents(prev => [event, ...prev]);
      }, index * 1000);
    });
  }, []);

  const getIcon = (type) => {
    switch (type) {
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      default: return <Clock className="w-4 h-4 text-cyan-400" />;
    }
  };

  return (
    <div className="glass rounded-2xl p-6 h-96 overflow-hidden">
      <h2 className="text-xl font-bold text-cyan-400 mb-4 drop-shadow-lg">Event Stream</h2>
      <div className="space-y-3 overflow-y-auto h-full pb-4">
        <AnimatePresence>
          {displayedEvents.map((event) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ duration: 0.5 }}
              className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/30"
            >
              {getIcon(event.type)}
              <div className="flex-1">
                <p className="text-sm text-gray-300">{event.message}</p>
                <p className="text-xs text-gray-500 mt-1">{event.time}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EventStream;