import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { User, Monitor, Edit, Trash2, Plus, Save, X } from 'lucide-react';
import { API_BASE_URL } from '../config';

const PersonnelRoster = () => {
  const [users, setUsers] = useState([]);
  const [devices, setDevices] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [editingDevice, setEditingDevice] = useState(null);
  const [newUser, setNewUser] = useState({ name: '', type: 'guest', email: '', about_me: '' });
  const [newDevice, setNewDevice] = useState({ name: '', type: 'guest', ip: '', mac: '', user: '' });
  const [showAddUser, setShowAddUser] = useState(false);
  const [showAddDevice, setShowAddDevice] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDevices, setUserDevices] = useState([]);
  const [deviceHistory, setDeviceHistory] = useState([]);
  const [showDeviceHistory, setShowDeviceHistory] = useState(false);

  useEffect(() => {
    console.log('PersonnelRoster component mounted');
    fetchUsers();
    fetchDevices();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(API_BASE_URL + '/api/users');
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await fetch(API_BASE_URL + '/api/devices');
      const data = await response.json();
      setDevices(data);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const handleEditUser = (user) => {
    setEditingUser({ ...user });
  };

  const handleSaveUser = async () => {
    try {
      const response = await fetch(API_BASE_URL + '/api/users/' + editingUser.id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingUser),
      });
      if (response.ok) {
        await fetchUsers();
        setEditingUser(null);
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const response = await fetch(API_BASE_URL + '/api/users/' + id, {
          method: 'DELETE',
        });
        if (response.ok) {
          await fetchUsers();
        }
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const handleAddUser = async () => {
    if (!newUser.name || !newUser.type) return;
    try {
      const response = await fetch(API_BASE_URL + '/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });
      if (response.ok) {
        await fetchUsers();
        setNewUser({ name: '', type: 'guest', email: '', about_me: '' });
        setShowAddUser(false);
      }
    } catch (error) {
      console.error('Error adding user:', error);
    }
  };

  const handleEditDevice = (device) => {
    setEditingDevice({ ...device });
  };

  const handleSaveDevice = async () => {
    try {
      const response = await fetch(API_BASE_URL + '/api/devices/' + editingDevice.id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingDevice),
      });
      if (response.ok) {
        await fetchDevices();
        setEditingDevice(null);
      }
    } catch (error) {
      console.error('Error updating device:', error);
    }
  };

  const handleDeleteDevice = async (id) => {
    if (window.confirm('Are you sure you want to delete this device?')) {
      try {
        const response = await fetch(API_BASE_URL + '/api/devices/' + id, {
          method: 'DELETE',
        });
        if (response.ok) {
          await fetchDevices();
        }
      } catch (error) {
        console.error('Error deleting device:', error);
      }
    }
  };

  const handleAddDevice = async () => {
    if (!newDevice.name || !newDevice.type) return;
    try {
      const response = await fetch(API_BASE_URL + '/api/devices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newDevice),
      });
      if (response.ok) {
        await fetchDevices();
        setNewDevice({ name: '', type: 'guest', ip: '', mac: '', user: '' });
        setShowAddDevice(false);
      }
    } catch (error) {
      console.error('Error adding device:', error);
    }
  };

  const handleUserClick = async (user) => {
    console.log('handleUserClick called with user:', user);
    console.log('Setting selectedUser to:', user);
    setSelectedUser(user);
    setUserDevices([]);
    setShowDeviceHistory(false);
    console.log('State should be updated now');
    try {
      const response = await fetch(API_BASE_URL + '/api/users/' + user.id + '/devices');
      const devices = await response.json();
      console.log('Received devices:', devices);
      console.log('Setting userDevices to:', devices);
      setUserDevices(devices);
      console.log('All state updates complete');
    } catch (error) {
      console.error('Error fetching user devices:', error);
    }
  };

  const handleDeviceHistoryClick = async (device) => {
    console.log('handleDeviceHistoryClick called with device:', device);
    try {
      const response = await fetch(API_BASE_URL + '/api/devices/' + device.id + '/history');
      const history = await response.json();
      console.log('Received history:', history);
      console.log('Setting deviceHistory and showDeviceHistory');
      setDeviceHistory(history);
      setShowDeviceHistory(true);
      console.log('Device history state updated');
    } catch (error) {
      console.error('Error fetching device history:', error);
    }
  };

  console.log('Rendering PersonnelRoster with:', { selectedUser, userDevices: userDevices.length, showDeviceHistory });

  return (
    <div className="space-y-8">
      {/* Users Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-cyan-400">Users</h2>
          <button
            onClick={() => setShowAddUser(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-400/20 border border-cyan-400 rounded-lg text-cyan-400 hover:bg-cyan-400/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add User</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {users.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20 cursor-pointer hover:bg-slate-700/30 transition-colors"
              onClick={() => {
                console.log('User card clicked!');
                handleUserClick(user);
              }}
            >
              <div className="flex items-center justify-between mb-4">
                  <User className={'w-6 h-6 ' + (user.type !== 'guest' ? 'text-green-400' : 'text-yellow-400')} />
                <div className="flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditUser(user);
                    }}
                    className="p-1 text-cyan-400 hover:bg-cyan-400/20 rounded"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteUser(user.id);
                    }}
                    className="p-1 text-red-400 hover:bg-red-400/20 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {editingUser && editingUser.id === user.id ? (
                <div className="space-y-2">
                  <input
                    value={editingUser.name}
                    onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    placeholder="Name"
                  />
                  <select
                    value={editingUser.type}
                    onChange={(e) => setEditingUser({ ...editingUser, type: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                  >
                    <option value="technoking">Technoking</option>
                    <option value="resident">Resident</option>
                    <option value="guest">Guest</option>
                  </select>
                  <input
                    value={editingUser.email}
                    onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    placeholder="Email"
                  />
                  <textarea
                    value={editingUser.about_me}
                    onChange={(e) => setEditingUser({ ...editingUser, about_me: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    rows={2}
                    placeholder="About Me"
                  />
                  <div className="flex space-x-2">
                    <button
                      onClick={handleSaveUser}
                      className="px-3 py-1 bg-green-400/20 border border-green-400 rounded text-green-400 hover:bg-green-400/30"
                    >
                      <Save className="w-4 h-4 inline mr-1" />
                      Save
                    </button>
                    <button
                      onClick={() => setEditingUser(null)}
                      className="px-3 py-1 bg-gray-400/20 border border-gray-400 rounded text-gray-400 hover:bg-gray-400/30"
                    >
                      <X className="w-4 h-4 inline mr-1" />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <h3 className="text-lg font-semibold text-gray-200">{user.name}</h3>
                  <p className="text-sm text-cyan-400 uppercase">{user.type}</p>
                  <p className="text-xs text-gray-400">{user.email}</p>
                  <p className="text-xs text-gray-500">{user.about_me}</p>
                  <p className="text-xs text-gray-500">State: {user.state}</p>
                </div>
              )}
            </motion.div>
          ))}
        </div>
        {showAddUser && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20"
          >
            <h3 className="text-lg font-semibold text-cyan-400 mb-4">Add New User</h3>
            <div className="space-y-3">
              <input
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                placeholder="Name"
              />
              <select
                value={newUser.type}
                onChange={(e) => setNewUser({ ...newUser, type: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
              >
                <option value="technoking">Technoking</option>
                <option value="resident">Resident</option>
                <option value="guest">Guest</option>
              </select>
              <input
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                placeholder="Email"
              />
              <textarea
                value={newUser.about_me}
                onChange={(e) => setNewUser({ ...newUser, about_me: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                rows={2}
                placeholder="About Me"
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleAddUser}
                  className="px-4 py-2 bg-green-400/20 border border-green-400 rounded text-green-400 hover:bg-green-400/30"
                >
                  Add
                </button>
                <button
                  onClick={() => setShowAddUser(false)}
                  className="px-4 py-2 bg-gray-400/20 border border-gray-400 rounded text-gray-400 hover:bg-gray-400/30"
                >
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Devices Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-cyan-400">Devices</h2>
          <button
            onClick={() => setShowAddDevice(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-400/20 border border-cyan-400 rounded-lg text-cyan-400 hover:bg-cyan-400/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Device</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {devices.map((device, index) => (
            <motion.div
              key={device.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20 cursor-pointer hover:bg-slate-700/30 transition-colors"
                  onClick={() => {
                    console.log('User device card clicked!');
                    handleDeviceHistoryClick(device);
                  }}
            >
              <div className="flex items-center justify-between mb-4">
                <Monitor className="w-6 h-6 text-cyan-400" />
                <div className="flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditDevice(device);
                    }}
                    className="p-1 text-cyan-400 hover:bg-cyan-400/20 rounded"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteDevice(device.id);
                    }}
                    className="p-1 text-red-400 hover:bg-red-400/20 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {editingDevice && editingDevice.id === device.id ? (
                <div className="space-y-2">
                  <input
                    value={editingDevice.name}
                    onChange={(e) => setEditingDevice({ ...editingDevice, name: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    placeholder="Name"
                  />
                  <select
                    value={editingDevice.type}
                    onChange={(e) => setEditingDevice({ ...editingDevice, type: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                  >
                    <option value="alfr3d">Alfr3d</option>
                    <option value="HW">HW</option>
                    <option value="guest">Guest</option>
                    <option value="light">Light</option>
                    <option value="resident">Resident</option>
                  </select>
                  <input
                    value={editingDevice.ip}
                    onChange={(e) => setEditingDevice({ ...editingDevice, ip: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    placeholder="IP"
                  />
                  <input
                    value={editingDevice.mac}
                    onChange={(e) => setEditingDevice({ ...editingDevice, mac: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                    placeholder="MAC"
                  />
                  <select
                    value={editingDevice.user || ''}
                    onChange={(e) => setEditingDevice({ ...editingDevice, user: e.target.value })}
                    className="w-full p-2 bg-slate-700 rounded text-gray-200"
                  >
                    <option value="">No User</option>
                    {users.map(user => (
                      <option key={user.id} value={user.name}>{user.name}</option>
                    ))}
                  </select>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleSaveDevice}
                      className="px-3 py-1 bg-green-400/20 border border-green-400 rounded text-green-400 hover:bg-green-400/30"
                    >
                      <Save className="w-4 h-4 inline mr-1" />
                      Save
                    </button>
                    <button
                      onClick={() => setEditingDevice(null)}
                      className="px-3 py-1 bg-gray-400/20 border border-gray-400 rounded text-gray-400 hover:bg-gray-400/30"
                    >
                      <X className="w-4 h-4 inline mr-1" />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <h3 className="text-lg font-semibold text-gray-200">{device.name}</h3>
                  <p className="text-sm text-cyan-400 uppercase">{device.type}</p>
                  <p className="text-xs text-gray-400">IP: {device.ip}</p>
                  <p className="text-xs text-gray-400">MAC: {device.mac}</p>
                  <p className="text-xs text-gray-500">User: {device.user || 'None'}</p>
                  <p className="text-xs text-gray-500">State: {device.state}</p>
                </div>
              )}
            </motion.div>
          ))}
        </div>
        {showAddDevice && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20"
          >
            <h3 className="text-lg font-semibold text-cyan-400 mb-4">Add New Device</h3>
            <div className="space-y-3">
              <input
                value={newDevice.name}
                onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                placeholder="Name"
              />
              <select
                value={newDevice.type}
                onChange={(e) => setNewDevice({ ...newDevice, type: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
              >
                <option value="alfr3d">Alfr3d</option>
                <option value="HW">HW</option>
                <option value="guest">Guest</option>
                <option value="light">Light</option>
                <option value="resident">Resident</option>
              </select>
              <input
                value={newDevice.ip}
                onChange={(e) => setNewDevice({ ...newDevice, ip: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                placeholder="IP"
              />
              <input
                value={newDevice.mac}
                onChange={(e) => setNewDevice({ ...newDevice, mac: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
                placeholder="MAC"
              />
              <select
                value={newDevice.user}
                onChange={(e) => setNewDevice({ ...newDevice, user: e.target.value })}
                className="w-full p-2 bg-slate-700 rounded text-gray-200"
              >
                <option value="">No User</option>
                {users.map(user => (
                  <option key={user.id} value={user.name}>{user.name}</option>
                ))}
              </select>
              <div className="flex space-x-2">
                <button
                  onClick={handleAddDevice}
                  className="px-4 py-2 bg-green-400/20 border border-green-400 rounded text-green-400 hover:bg-green-400/30"
                >
                  Add
                </button>
                <button
                  onClick={() => setShowAddDevice(false)}
                  className="px-4 py-2 bg-gray-400/20 border border-gray-400 rounded text-gray-400 hover:bg-gray-400/30"
                >
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* User Devices Section */}
        {selectedUser && (
          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-cyan-400">
                Devices for {selectedUser.name}
              </h3>
              <button
                onClick={() => setSelectedUser(null)}
                className="text-gray-400 hover:text-cyan-400 transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {userDevices.map((device, index) => (
                <motion.div
                  key={device.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="glass rounded-2xl p-4 border border-cyan-500/30 bg-slate-800/20 cursor-pointer hover:bg-slate-700/30 transition-colors"
              onClick={() => {
                console.log('Device card clicked!');
                handleDeviceHistoryClick(device);
              }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <Monitor className="w-5 h-5 text-cyan-400" />
                    <span className="text-xs text-cyan-400 uppercase">{device.type}</span>
                  </div>
                  <h4 className="text-sm font-semibold text-gray-200 mb-2">{device.name}</h4>
                  <div className="text-xs text-gray-400 space-y-1">
                    <div>IP: {device.ip}</div>
                    <div>MAC: {device.mac}</div>
                    <div>State: {device.state}</div>
                    <div>Last Online: {device.last_online}</div>
                  </div>
                </motion.div>
              ))}
              {userDevices.length === 0 && (
                <div className="col-span-full text-center text-gray-400 py-8">
                  No devices found for this user
                </div>
              )}
            </div>
          </div>
        )}

        {/* Device History Section */}
        {showDeviceHistory && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 glass rounded-2xl p-6 border border-cyan-500/30 bg-slate-800/20"
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-cyan-400">Device History</h3>
              <button
                onClick={() => setShowDeviceHistory(false)}
                className="text-gray-400 hover:text-white text-xl"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {deviceHistory.map((entry, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-l-4 border-cyan-400 pl-4 py-3 bg-slate-700/20 rounded-r"
                >
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-cyan-400 font-medium">{entry.timestamp}</span>
                    <span className="text-gray-400">{entry.state}</span>
                  </div>
                  <div className="text-sm text-gray-300 space-y-1">
                    <div>Name: <span className="text-white">{entry.name}</span></div>
                    <div>IP: <span className="text-white">{entry.ip}</span></div>
                    <div>MAC: <span className="text-white">{entry.mac}</span></div>
                    {entry.user && <div>User: <span className="text-white">{entry.user}</span></div>}
                  </div>
                </motion.div>
              ))}
              {deviceHistory.length === 0 && (
                <div className="text-center text-gray-400 py-8">
                  No history found for this device
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default PersonnelRoster;