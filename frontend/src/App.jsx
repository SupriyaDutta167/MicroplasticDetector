import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 50%, #e8f5e8 100%)'
    }}>
      <Navbar />
      <Dashboard />
    </div>
  );
}

export default App;