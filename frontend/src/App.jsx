import React from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 selection:bg-blue-500/30">
      <Sidebar />
      <div className="relative">
        <Header />
        <Dashboard />
      </div>
    </div>
  );
}

export default App;
