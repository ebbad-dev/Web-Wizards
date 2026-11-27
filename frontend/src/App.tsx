import { Routes, Route, Navigate } from "react-router-dom";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route
        path="/login"
        element={
          <div className="flex min-h-screen items-center justify-center bg-gray-50">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-blue-600">NIGRAN-360</h1>
              <p className="mt-2 text-gray-600">Secure Examination Management System</p>
              <p className="mt-4 text-sm text-gray-400">Phase 2: Authentication coming next</p>
            </div>
          </div>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
