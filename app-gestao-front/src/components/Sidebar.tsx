import { Outlet, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function DashboardLayout() {
  const { user} = useAuth();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white p-4">
        <nav className="space-y-3">
          <Link to="/dashboard" className="block">Dashboard</Link>
          <Link to="/dashboard/profile" className="block">Perfil</Link>
          <Link to="/dashboard/tasks" className="block">Tarefas</Link>

          {user?.role === "admin" && (
            <Link to="/admin" className="block text-red-400">
              Admin
            </Link>
          )}
        </nav>        
      </aside>      
    </div>
  );
}
