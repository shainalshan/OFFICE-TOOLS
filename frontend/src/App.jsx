import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import SignatureGenerator from './components/SignatureGenerator';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/signature/" element={<SignatureGenerator />} />
          {/* Fallback for other urls if needed */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
