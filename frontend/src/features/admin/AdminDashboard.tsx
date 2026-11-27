import { useQuery } from "@tanstack/react-query";
import api from "@/lib/axios";

interface UserList {
  total: number;
  items: { id: string; role: string; is_active: boolean }[];
}

function useSummary() {
  return useQuery({
    queryKey: ["admin", "users-summary"],
    queryFn: async () => {
      const res = await api.get<UserList>("/users?page_size=1");
      return res.data;
    },
  });
}

export default function AdminDashboard() {
  const { data, isLoading } = useSummary();

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">Administrator Dashboard</h1>

      {isLoading ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard label="Total users" value={data?.total ?? "—"} />
        </div>
      )}

      <div>
        <a
          href="/admin/users"
          className="inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          Manage users →
        </a>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl bg-white border border-gray-200 shadow-sm p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
