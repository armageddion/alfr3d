import { motion } from 'framer-motion';
import { useState } from 'react';
import { Edit, Trash2, Plus } from 'lucide-react';

const quips = [
  { id: 1, type: 'smart', text: 'It is good to see you.' },
  { id: 2, type: 'smart', text: 'You look pretty today.' },
  { id: 3, type: 'email', text: 'Yet another email' },
];

const Personality = () => {
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  const handleEdit = (id, text) => {
    setEditingId(id);
    setEditText(text);
  };

  const handleSave = () => {
    // Save logic here
    setEditingId(null);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-cyan-400 mb-6 drop-shadow-lg">Personality Settings</h2>
      
      <div className="space-y-4">
        {quips.map((quip, index) => (
          <motion.div
            key={quip.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
            className="glass rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <span className="text-sm text-cyan-400 uppercase tracking-wide">{quip.type}</span>
                {editingId === quip.id ? (
                  <input
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    className="w-full mt-2 p-2 bg-slate-700 rounded text-gray-200"
                  />
                ) : (
                  <p className="text-gray-200 mt-1">{quip.text}</p>
                )}
              </div>
              <div className="flex space-x-2 ml-4">
                {editingId === quip.id ? (
                  <button
                    onClick={handleSave}
                    className="p-2 text-green-400 hover:bg-green-400/20 rounded"
                  >
                    Save
                  </button>
                ) : (
                  <button
                    onClick={() => handleEdit(quip.id, quip.text)}
                    className="p-2 text-cyan-400 hover:bg-cyan-400/20 rounded"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                )}
                <button className="p-2 text-red-400 hover:bg-red-400/20 rounded">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="mt-6 flex items-center space-x-2 px-4 py-2 bg-cyan-400/20 border border-cyan-400 rounded-lg text-cyan-400 hover:bg-cyan-400/30 transition-colors drop-shadow-lg"
      >
        <Plus className="w-5 h-5" />
        <span>Add New Quip</span>
      </motion.button>
    </div>
  );
};

export default Personality;