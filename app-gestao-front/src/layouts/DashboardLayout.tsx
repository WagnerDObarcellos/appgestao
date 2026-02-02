import { Outlet, NavLink } from "react-router-dom";
import { LayoutDashboard, CheckSquare, User, LogOut, ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function DashboardLayout() {
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r hidden md:flex flex-col">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-800">App Gestão</h2>
          <p className="text-sm text-gray-500">Painel do usuário</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <NavLink
            to="/dashboard"
            end
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                isActive
                  ? "bg-blue-100 text-blue-700 font-semibold"
                  : "text-gray-600 hover:bg-gray-100"
              }`
            }
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          <NavLink
            to="/dashboard/tasks"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                isActive
                  ? "bg-blue-100 text-blue-700 font-semibold"
                  : "text-gray-600 hover:bg-gray-100"
              }`
            }
          >
            <CheckSquare size={18} />
            Tarefas
          </NavLink>

          <NavLink
            to="/dashboard/profile"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                isActive
                  ? "bg-blue-100 text-blue-700 font-semibold"
                  : "text-gray-600 hover:bg-gray-100"
              }`
            }
          >
            <User size={18} />
            Perfil
          </NavLink>
        </nav>
         {user?.role === 'admin' && (
            <NavLink
              to="/dashboard/admin"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                  isActive
                    ? "bg-purple-100 text-purple-700 font-semibold"
                    : "text-gray-600 hover:bg-purple-50"
                }`
              }
            >
              <ShieldCheck size={18} />
              Admin
            </NavLink>
          )}

        <div className="p-4 border-t">
          <button
            onClick={signOut}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <LogOut size={18} />
            Sair
          </button>
        </div>
      </aside>

      {/* Conteúdo principal */}
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
