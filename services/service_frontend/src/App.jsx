import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import Nexus from './pages/Nexus';
import Domain from './pages/Domain';
import Matrix from './pages/Matrix';

function App() {
  return (
    <Router>
      <div className="min-h-screen relative overflow-hidden">
        {/* Background Layers */}
        <div className="fixed inset-0 nebula"></div>
        <div className="fixed inset-0 grid-bg opacity-20"></div>
        
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
          className="relative z-10"
        >
          <Routes>
            <Route path="/" element={<Nexus />} />
            <Route path="/domain" element={<Domain />} />
            <Route path="/matrix" element={<Matrix />} />
          </Routes>
        </motion.div>
      </div>
    </Router>
  );
}

export default App;