import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore, type UserRole } from "@/stores/auth.store";

interface Props {
  children: React.ReactNode;
  /** If provided, only users with one of these roles may access the route. */
  roles?: UserRole[];
}

export default function ProtectedRoute({ children, roles }: Props) {
  const { isAuthenticated, isInitialising, user } = useAuthStore();
  const location = useLocation();

  if (isInitialising) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500 text-sm">Loading…</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
