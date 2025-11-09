import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useRef } from 'react';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';

const EventStream = () => {
  const [displayedEvents, setDisplayedEvents] = useState([]);
  const eventStreamRef = useRef(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/events');
        const events = await response.json();
        // Reverse to show newest first, limit to 10
        const latestEvents = events.reverse().slice(0, 10);
        setDisplayedEvents(latestEvents);
        // Autoscroll to bottom
        if (eventStreamRef.current) {
          eventStreamRef.current.scrollTop = eventStreamRef.current.scrollHeight;
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
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
      <div ref={eventStreamRef} className="space-y-3 overflow-y-auto h-full pb-4">
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