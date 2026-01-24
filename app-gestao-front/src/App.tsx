import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UserDashboard from './components/dashboard/UserDashboard';
import { PrivateRoute } from "./components/PrivateRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/user-dashboard" element={<PrivateRoute><UserDashboard /></PrivateRoute>} />
        
      </Routes>
    </BrowserRouter>
  );
}

export default App;
