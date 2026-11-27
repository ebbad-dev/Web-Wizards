import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { restoreSession } from "@/services/auth.service";
import { fetchMe } from "@/services/auth.service";
import { setAccessToken } from "@/lib/axios";
import { useAuthStore } from "@/stores/auth.store";

import ProtectedRoute from "@/components/common/ProtectedRoute";
import AppLayout from "@/components/layouts/AppLayout";
import LoginPage from "@/features/auth/LoginPage";
import RegisterPage from "@/features/auth/RegisterPage";
import AdminDashboard from "@/features/admin/AdminDashboard";
import UserManagement from "@/features/admin/UserManagement";
import ExaminerDashboard from "@/features/examiner/ExaminerDashboard";
import CandidateDashboard from "@/features/candidate/CandidateDashboard";

function DashboardRedirect() {
  const { user } = useAuthStore();
  if (!user) return null;
  if (user.role === "administrator") return <Navigate to="/admin" replace />;
  if (user.role === "examiner") return <Navigate to="/examiner" replace />;
  return <Navigate to="/candidate" replace />;
}

export default function App() {
  const { setUser, setInitialising } = useAuthStore();

  // On first load, attempt to restore session via HttpOnly refresh cookie.
  useEffect(() => {
    (async () => {
      const token = await restoreSession();
      if (token) {
        setAccessToken(token);
        try {
          const me = await fetchMe();
          setUser(me);
        } catch {
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setInitialising(false);
    })();
  }, [setUser, setInitialising]);

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Authenticated — ProtectedRoute gates the layout; AppLayout renders <Outlet> */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardRedirect />} />

        {/* Admin */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["administrator"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute roles={["administrator"]}>
              <UserManagement />
            </ProtectedRoute>
          }
        />

        {/* Examiner */}
        <Route
          path="/examiner"
          element={
            <ProtectedRoute roles={["examiner"]}>
              <ExaminerDashboard />
            </ProtectedRoute>
          }
        />

        {/* Candidate */}
        <Route
          path="/candidate"
          element={
            <ProtectedRoute roles={["candidate"]}>
              <CandidateDashboard />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Fallbacks */}
      <Route path="/unauthorized" element={
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500">403 — Insufficient permissions.</p>
        </div>
      } />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
