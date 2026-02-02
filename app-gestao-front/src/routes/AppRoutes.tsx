import { Routes, Route, Navigate } from "react-router-dom";
import Login from "@/pages/Login";
import UserDashboard from "@/pages/UserDashboard";
import DashboardLayout from "@/layouts/DashboardLayout";
import { ProtectedRoute } from "./ProtectedRoute";

export function AppRoutes() {
  return (
    <Routes>
      {/* Redireciona raiz para login */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<Login />} />

      <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
      <Route index element={<UserDashboard />} />
      </Route>
      <Route path="/dashboard/profile" element={<div>Profile Page</div>} />
      <Route path="/dashboard/tasks" element={<div>Tasks Page</div>} />
      <Route path="/dashboard/admin" element={<div>Admin Page</div>} />
    </Routes>
  );
}
