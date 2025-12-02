import { motion } from 'framer-motion';
import { useState } from 'react';
import Core from '../components/Core';
import SituationalAwareness from '../components/SituationalAwareness';
import OnlineUsers from '../components/OnlineUsers';
import GuestRoster from '../components/GuestRoster';
import ContainerHealth from '../components/ContainerHealth';
import EventStream from '../components/EventStream';
import TacticalPanel from '../components/TacticalPanel';
import LocationPanel from '../components/LocationPanel';

const Nexus = () => {
  const [systemHealth] = useState('cyan');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="min-h-screen p-8 bg-fui-bg"
      style={{
        backgroundImage: "linear-gradient(to right, #222 1px, transparent 1px), linear-gradient(to bottom, #222 1px, transparent 1px)",
        backgroundSize: '20px 20px'
      }}
    >
      <div className="w-full px-8">
        <motion.h1
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="text-4xl font-tech font-bold text-fui-accent mb-8 text-center uppercase tracking-widest"
        >
          ALFR3D Nexus
        </motion.h1>

          <div className="grid gap-8 w-full" style={{ gridTemplateColumns: '0.8fr 1.2fr 2fr 1.2fr 0.8fr' }}>
          {/* Column 1: Location */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="flex flex-col"
          >
            <LocationPanel />
          </motion.div>

           {/* Column 2: Situational Awareness */}
           <motion.div
             initial={{ opacity: 0, y: -20 }}
             animate={{ opacity: 1, y: 0 }}
             transition={{ delay: 0.5, duration: 0.6 }}
             className="flex flex-col"
           >
             <TacticalPanel title="Situational Awareness">
               <SituationalAwareness />
             </TacticalPanel>
           </motion.div>

          {/* Column 3: Core + Event Stream */}
           <motion.div
             initial={{ opacity: 0, scale: 0.8 }}
             animate={{ opacity: 1, scale: 1 }}
             transition={{ delay: 0.6, duration: 0.8 }}
             className="flex flex-col gap-8 px-6 items-center"
           >
            <Core health={systemHealth} />
            <TacticalPanel title="Event Stream">
              <EventStream />
            </TacticalPanel>
          </motion.div>

           {/* Column 4: Guest Roster + Residents */}
           <motion.div
             initial={{ opacity: 0, y: 20 }}
             animate={{ opacity: 1, y: 0 }}
             transition={{ delay: 0.7, duration: 0.6 }}
             className="flex flex-col gap-6"
           >
             <TacticalPanel title="Guest Roster">
               <GuestRoster />
             </TacticalPanel>
             <TacticalPanel title="R3sidents">
               <OnlineUsers />
             </TacticalPanel>
           </motion.div>

           {/* Column 5: Container Health */}
           <motion.div
             initial={{ opacity: 0, x: 50 }}
             animate={{ opacity: 1, x: 0 }}
             transition={{ delay: 0.8, duration: 0.6 }}
             className="flex flex-col"
           >
             <TacticalPanel title="Container Health">
               <ContainerHealth />
             </TacticalPanel>
           </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default Nexus;
