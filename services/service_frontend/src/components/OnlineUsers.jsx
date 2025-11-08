import { motion } from 'framer-motion';
import { User, Users } from 'lucide-react';

const users = [
  { id: 1, name: 'Athos', status: 'online', type: 'user' },
  { id: 2, name: 'Porthos', status: 'online', type: 'user' },
  { id: 3, name: 'Aramis', status: 'away', type: 'user' },
  { id: 4, name: 'Guest1', status: 'online', type: 'guest' },
  { id: 5, name: 'Guest2', status: 'away', type: 'guest' },
];

const OnlineUsers = () => {
  const onlineUsers = users.filter(user => user.status === 'online');
  const awayUsers = users.filter(user => user.status === 'away');

  return (
    <div className="glass rounded-2xl p-6">
      <h2 className="text-xl font-bold text-cyan-400 mb-4 drop-shadow-lg">Online Users</h2>

      <div className="space-y-3">
        {/* Online Users */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-400 font-semibold">Online ({onlineUsers.length})</span>
          </div>
          {onlineUsers.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              className="flex items-center space-x-2 py-1"
            >
              <User className={`w-4 h-4 ${user.type === 'user' ? 'text-cyan-400' : 'text-yellow-400'}`} />
              <span className="text-sm text-gray-300">{user.name}</span>
            </motion.div>
          ))}
        </div>

        {/* Away Users */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
            <span className="text-sm text-yellow-400 font-semibold">Away ({awayUsers.length})</span>
          </div>
          {awayUsers.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (onlineUsers.length + index) * 0.1, duration: 0.3 }}
              className="flex items-center space-x-2 py-1"
            >
              <User className={`w-4 h-4 ${user.type === 'user' ? 'text-cyan-400' : 'text-yellow-400'}`} />
              <span className="text-sm text-gray-500">{user.name}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OnlineUsers;