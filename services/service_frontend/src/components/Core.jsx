import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import Lottie from 'lottie-react';
import { useState, useEffect } from 'react';

const Core = ({ health }) => {
  const [animationData, setAnimationData] = useState(null);
  const [animationFinished, setAnimationFinished] = useState(false);
  const [rotation, setRotation] = useState(0);
  const currentHour = new Date().getHours();
  const isDay = currentHour >= 6 && currentHour < 18;

  useEffect(() => {
    fetch('/lottie/logo.json')
      .then(response => response.json())
      .then(data => setAnimationData(data))
      .catch(error => console.error('Error loading Lottie animation:', error));
  }, []);

  useEffect(() => {
    if (animationFinished) {
      const rotateRandomly = () => {
        const randomRotation = (Math.random() - 0.5) * 60; // -30 to +30
        setRotation(randomRotation);
        const randomDelay = Math.random() * 3000 + 1000; // 1-4 seconds
        setTimeout(rotateRandomly, randomDelay);
      };
      rotateRandomly();
    }
  }, [animationFinished]);

  return (
    <motion.svg
      width="400"
      height="400"
      viewBox="0 0 300 300"
      className="drop-shadow-2xl"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 1, delay: 0.5 }}
    >
        {/* Outer Ring */}
        <motion.circle
          cx="150"
          cy="150"
          r="140"
          fill="none"
          stroke={`url(#gradient-${health})`}
          strokeWidth="2"
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        />
        
        {/* Middle Ring */}
        <motion.circle
          cx="150"
          cy="150"
          r="110"
          fill="none"
          stroke={`url(#gradient-${health})`}
          strokeWidth="1"
          animate={{ rotate: -360 }}
          transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
        />
        
        {/* Inner Ring */}
        <motion.circle
          cx="150"
          cy="150"
          r="80"
          fill="none"
          stroke={`url(#gradient-${health})`}
          strokeWidth="1"
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        />
        
        {/* Central Core - Lottie Logo */}
        <foreignObject x="80" y="80" width="140" height="140">
          <motion.div
            animate={animationFinished ? { rotate: rotation } : {
              scale: [1, 1.1, 1],
              opacity: [0.8, 1, 0.8]
            }}
            transition={animationFinished ? {
              duration: 0.5,
              ease: "easeInOut"
            } : {
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ width: '100%', height: '100%' }}
          >
            {animationData && (
              <Lottie
                animationData={animationData}
                loop={false}
                autoplay
                onComplete={() => setAnimationFinished(true)}
                style={{ width: '100%', height: '100%' }}
                rendererSettings={{
                  preserveAspectRatio: 'xMidYMid slice'
                }}
              />
            )}
          </motion.div>
        </foreignObject>
        
        {/* Sun/Moon Icon */}
        <motion.g
          animate={{
            x: Math.cos((currentHour / 24) * 2 * Math.PI - Math.PI/2) * 120,
            y: Math.sin((currentHour / 24) * 2 * Math.PI - Math.PI/2) * 120
          }}
          transition={{ duration: 1 }}
        >
          {isDay ? (
            <Sun className="w-8 h-8 text-yellow-400 drop-shadow-lg" />
          ) : (
            <Moon className="w-8 h-8 text-cyan-400 drop-shadow-lg" />
          )}
        </motion.g>
        
        {/* Gradients */}
        <defs>
          <radialGradient id="gradient-cyan" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.2" />
          </radialGradient>
          <radialGradient id="gradient-yellow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#fbbf24" stopOpacity="0.2" />
          </radialGradient>
          <radialGradient id="gradient-magenta" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ec4899" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0.2" />
          </radialGradient>
        </defs>
      </motion.svg>
  );
};

export default Core;