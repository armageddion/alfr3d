import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Cpu, HardDrive, MemoryStick, AlertTriangle } from 'lucide-react';

const ContainerHealth = () => {
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [containers, setContainers] = useState([]);

  useEffect(() => {
    const fetchContainers = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/containers');
        const data = await response.json();
        console.log('Fetched containers for ContainerHealth:', data);
        setContainers(data);
      } catch (error) {
        console.error('Error fetching containers for ContainerHealth:', error);
      }
    };
    fetchContainers();
    const interval = setInterval(fetchContainers, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass rounded-2xl p-6">
      <h2 className="text-xl font-bold text-cyan-400 mb-4 drop-shadow-lg">Container Health</h2>

      <div className="space-y-4">
        {containers.map((container, index) => (
          <motion.div
            key={container.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedContainer(container)}
            className="cursor-pointer"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-semibold text-gray-200">{container.name}</span>
              {container.errors > 0 && <AlertTriangle className="w-4 h-4 text-red-400" />}
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="flex items-center space-x-1">
                <Cpu className="w-3 h-3 text-cyan-400" />
                <span className="text-gray-300">{container.cpu}%</span>
              </div>
              <div className="flex items-center space-x-1">
                <MemoryStick className="w-3 h-3 text-green-400" />
                <span className="text-gray-300">{container.mem}%</span>
              </div>
              <div className="flex items-center space-x-1">
                <HardDrive className="w-3 h-3 text-yellow-400" />
                <span className="text-gray-300">{container.disk}%</span>
              </div>
            </div>

            {/* Progress bars */}
            <div className="mt-2 space-y-1">
              <div className="w-full bg-slate-700 rounded-full h-1">
                <motion.div
                  className="bg-cyan-400 h-1 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${container.cpu}%` }}
                  transition={{ delay: 0.5 + index * 0.1, duration: 1 }}
                />
              </div>
              <div className="w-full bg-slate-700 rounded-full h-1">
                <motion.div
                  className="bg-green-400 h-1 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${container.mem}%` }}
                  transition={{ delay: 0.6 + index * 0.1, duration: 1 }}
                />
              </div>
              <div className="w-full bg-slate-700 rounded-full h-1">
                <motion.div
                  className="bg-yellow-400 h-1 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${container.disk}%` }}
                  transition={{ delay: 0.7 + index * 0.1, duration: 1 }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {selectedContainer && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 bg-slate-800/50 rounded-lg"
        >
          <h3 className="text-sm font-semibold text-cyan-400 mb-2">{selectedContainer.name} Details</h3>
          <p className="text-xs text-gray-400">Errors: {selectedContainer.errors}</p>
        </motion.div>
      )}
    </div>
  );
};

export default ContainerHealth;