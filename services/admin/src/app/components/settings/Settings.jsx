import { Settings as SettingsIcon } from "lucide-react";

export function Settings() {
  return (
    <div className="rounded-2xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
      <div className="max-w-2xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#58a6ff]/10 text-[#58a6ff]">
            <SettingsIcon size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Settings</h2>
            <p className="text-sm text-[#8b949e]">Manage preferences, notifications, security, and integrations.</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
            <p className="text-sm font-medium text-white">Notifications</p>
            <p className="mt-1 text-sm text-[#8b949e]">Turn alerts on or off for bookings and user actions.</p>
          </div>
          <div className="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
            <p className="text-sm font-medium text-white">Security</p>
            <p className="mt-1 text-sm text-[#8b949e]">Review access controls and password requirements.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
