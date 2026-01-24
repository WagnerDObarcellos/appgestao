import { useAuth } from "../contexts/AuthContext";
import { Outlet } from "react-router-dom";
import Sidebar from '../components/sidebar';

const Dashboard = () => {
  const { user, signOut } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Bem-vindo, {user?.email}</p>

      <button onClick={signOut}>Sair</button>
      <Sidebar /> {/* Seu menu fixo */}
      <main>
        <Outlet /> {/* Aqui o UserDashboard será injetado */}
      </main>
    </div>
    
  );
};

export default Dashboard;
