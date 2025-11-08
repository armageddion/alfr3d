import { motion } from 'framer-motion';
import { User, Home, Plane } from 'lucide-react';

const personnel = [
  { id: 1, name: 'Athos', status: 'home', avatar: 'A' },
  { id: 2, name: 'Porthos', status: 'away', avatar: 'P' },
  { id: 3, name: 'Aramis', status: 'home', avatar: 'Ar' },
];

const PersonnelRoster = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {personnel.map((person, index) => (
        <motion.div
          key={person.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.5 }}
          whileHover={{ scale: 1.03 }}
          className="glass rounded-2xl p-6 cursor-pointer"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-cyan-400/20 flex items-center justify-center text-cyan-400 font-bold drop-shadow-lg">
              {person.avatar}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-200">{person.name}</h3>
              <div className="flex items-center space-x-2 mt-1">
                {person.status === 'home' ? (
                  <Home className="w-4 h-4 text-green-400" />
                ) : (
                  <Plane className="w-4 h-4 text-yellow-400" />
                )}
                <span className={`text-sm ${person.status === 'home' ? 'text-green-400' : 'text-yellow-400'}`}>
                  {person.status === 'home' ? 'Home' : 'Away'}
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default PersonnelRoster;