import { useAuthStore } from "@/stores/auth.store";

export default function CandidateDashboard() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold text-gray-900">Candidate Dashboard</h1>
      <p className="text-sm text-gray-600">
        Welcome, <span className="font-medium">{user?.full_name}</span>. Your available
        examinations will appear here.
      </p>
      <div className="rounded-xl bg-indigo-50 border border-indigo-100 px-5 py-4 text-sm text-indigo-700">
        Phase 4: Browse enrolled examinations and begin attempts.
      </div>
    </div>
  );
}
