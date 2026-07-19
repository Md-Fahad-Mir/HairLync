import { useState } from "react";
import { Search, Shield, ShieldOff, Ban, CheckCircle, X, ChevronDown } from "lucide-react";
import { users as initialUsers } from "../data";
import { toast } from "sonner";

const roleBadge = {
  client: "bg-[#1f3a5f] text-[#58a6ff]",
  barber: "bg-[#2d1f5f] text-[#ab7df8]",
  salon: "bg-[#1f3a2d] text-[#3fb950]",
  admin: "bg-[#3a1f1f] text-[#f85149]",
};

export function UserManagement() {
  const [users, setUsers] = useState(initialUsers);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [verifiedFilter, setVerifiedFilter] = useState("all");
  const [selected, setSelected] = useState(null);

  const selectedUser = selected || {
    id: 0,
    name: "",
    email: "",
    phone: "",
    role: "client",
    verified: false,
    active: true,
    rating: 0,
    reviews: 0,
    bookings: 0,
    joined: "",
    lastActive: "",
  };

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    const matchSearch = u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || u.phone.includes(q);
    const matchRole = roleFilter === "all" || u.role === roleFilter;
    const matchVerified = verifiedFilter === "all" || (verifiedFilter === "verified" ? u.verified : !u.verified);
    return matchSearch && matchRole && matchVerified;
  });

  const toggleVerify = (id) => {
    setUsers((prev) => prev.map((u) => {
      if (u.id !== id) return u;
      const next = { ...u, verified: !u.verified };
      toast.success(next.verified ? `${u.name} verified successfully` : `Verification revoked for ${u.name}`);
      if (selected && selected.id === id) setSelected(next);
      return next;
    }));
  };

  const toggleSuspend = (id) => {
    setUsers((prev) => prev.map((u) => {
      if (u.id !== id) return u;
      const next = { ...u, active: !u.active };
      toast[next.active ? "success" : "warning"](next.active ? `${u.name} account restored` : `${u.name} account suspended`);
      if (selected && selected.id === id) setSelected(next);
      return next;
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl text-white mb-1">User Management</h1>
        <p className="text-[#8b949e] text-sm">Manage accounts, verifications, and access control</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8b949e]" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, email, phone..."
            className="w-full bg-[#161b22] border border-[#30363d] rounded-lg pl-9 pr-4 py-2 text-sm text-[#e6edf3] placeholder-[#8b949e] focus:outline-none focus:border-[#58a6ff]"
          />
        </div>
        <div className="relative">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="appearance-none bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-2 pr-8 text-sm text-[#e6edf3] focus:outline-none focus:border-[#58a6ff] cursor-pointer"
          >
            <option value="all">All Roles</option>
            <option value="client">Client</option>
            <option value="barber">Barber</option>
            <option value="salon">Salon</option>
          </select>
          <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#8b949e] pointer-events-none" />
        </div>
        <div className="relative">
          <select
            value={verifiedFilter}
            onChange={(e) => setVerifiedFilter(e.target.value)}
            className="appearance-none bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-2 pr-8 text-sm text-[#e6edf3] focus:outline-none focus:border-[#58a6ff] cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="verified">Verified</option>
            <option value="unverified">Unverified</option>
          </select>
          <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#8b949e] pointer-events-none" />
        </div>
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#30363d]">
                {["User", "Role", "Status", "Verified", "Joined"].map((h) => (
                  <th key={h} className="text-left text-[#8b949e] px-4 py-3 text-xs uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.id} className="border-b border-[#30363d] hover:bg-[#1c2128] transition-colors last:border-0">
                  <td className="px-4 py-3">
                    <button onClick={() => setSelected(u)} className="flex items-center gap-3 text-left">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#58a6ff] to-[#ab7df8] flex items-center justify-center text-white text-xs shrink-0">
                        {u.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                      </div>
                      <div>
                        <p className="text-[#e6edf3] hover:text-[#58a6ff] transition-colors">{u.name}</p>
                        <p className="text-[#8b949e] text-xs">{u.email}</p>
                      </div>
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-md text-xs capitalize ${roleBadge[u.role] || roleBadge.client}`}>{u.role}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`flex items-center gap-1.5 text-xs ${u.active ? "text-[#3fb950]" : "text-[#f85149]"}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${u.active ? "bg-[#3fb950]" : "bg-[#f85149]"}`} />
                      {u.active ? "Active" : "Suspended"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {u.verified
                      ? <span className="flex items-center gap-1 text-[#3fb950] text-xs"><CheckCircle size={12} /> Verified</span>
                      : <span className="text-[#8b949e] text-xs">—</span>}
                  </td>
                  <td className="px-4 py-3 text-[#8b949e]">{u.joined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setSelected(null)}>
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
          <div className="relative bg-[#161b22] border border-[#30363d] rounded-2xl p-6 w-full max-w-lg shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setSelected(null)} className="absolute top-4 right-4 text-[#8b949e] hover:text-white">
              <X size={18} />
            </button>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#58a6ff] to-[#ab7df8] flex items-center justify-center text-white text-lg">
                {selectedUser.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
              </div>
              <div>
                <h2 className="text-white text-lg">{selectedUser.name}</h2>
                <p className="text-[#8b949e] text-sm">{selectedUser.email}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-0.5 rounded text-xs capitalize ${roleBadge[selectedUser.role] || roleBadge.client}`}>{selectedUser.role}</span>
                  <span className={`text-xs ${selectedUser.active ? "text-[#3fb950]" : "text-[#f85149]"}`}>{selectedUser.active ? "Active" : "Suspended"}</span>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                { label: "Phone", value: selectedUser.phone },
                { label: "Joined", value: selectedUser.joined },
                { label: "Last Active", value: selectedUser.lastActive },
                { label: "Total Bookings", value: selectedUser.bookings },
                ...(selectedUser.rating > 0 ? [{ label: "Avg Rating", value: `${selectedUser.rating} ★` }, { label: "Total Reviews", value: selectedUser.reviews }] : []),
              ].map(({ label, value }) => (
                <div key={label} className="bg-[#0d1117] rounded-lg p-3">
                  <p className="text-[#8b949e] text-xs mb-1">{label}</p>
                  <p className="text-[#e6edf3]">{value}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-3 mt-6">
              {(selectedUser.role === "barber" || selectedUser.role === "salon") && (
                <button
                  onClick={() => toggleVerify(selectedUser.id)}
                  className={`flex-1 py-2 rounded-lg text-sm transition-colors ${selectedUser.verified ? "bg-[#1f3a2d] text-[#3fb950] hover:bg-[#243d29]" : "bg-[#1f3a5f] text-[#58a6ff] hover:bg-[#24466b]"}`}
                >
                  {selectedUser.verified ? "Revoke Verification" : "Verify Partner"}
                </button>
              )}
              <button
                onClick={() => toggleSuspend(selectedUser.id)}
                className={`flex-1 py-2 rounded-lg text-sm transition-colors ${selectedUser.active ? "bg-[#3a1f1f] text-[#f85149] hover:bg-[#461f1f]" : "bg-[#1f3a2d] text-[#3fb950] hover:bg-[#243d29]"}`}
              >
                {selectedUser.active ? "Suspend Account" : "Restore Access"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
