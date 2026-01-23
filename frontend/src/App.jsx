import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import SignatureGenerator from './components/SignatureGenerator';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 selection:bg-blue-500/30">
        <Sidebar />
        <div className="relative">
          <Header />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/signature/" element={<SignatureGenerator />} />
            {/* Fallback for other urls if needed */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
