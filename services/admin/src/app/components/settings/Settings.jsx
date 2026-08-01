import { ArrowRight, Lock, User } from "lucide-react";

export function Settings({ onOpenProfile, onOpenChangePassword }) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#58a6ff]/10 text-[#58a6ff]">
            <User size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Profile</h2>
            <p className="text-sm text-[#8b949e]">View and update your account details on the profile page.</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onOpenProfile}
          className="mt-5 flex w-full items-center justify-between rounded-3xl border border-[#30363d] bg-[#0d1117] px-5 py-4 text-left transition hover:border-[#58a6ff] hover:bg-[#0f1720] cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#0f1720] text-[#58a6ff]">
              <User size={18} />
            </div>
            <div>
              <p className="text-white text-sm font-medium">Profile</p>
              <p className="text-[#8b949e] text-xs">Open the profile page to load your account details.</p>
            </div>
          </div>
          <ArrowRight size={18} className="text-[#8b949e]" />
        </button>
      </div>

      <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#f85149]/10 text-[#f85149]">
            <Lock size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Security</h2>
            <p className="text-sm text-[#8b949e]">Update your password to keep your account secure.</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onOpenChangePassword}
          className="mt-5 flex w-full items-center justify-between rounded-3xl border border-[#30363d] bg-[#0d1117] px-5 py-4 text-left transition hover:border-[#f85149] hover:bg-[#170b10] cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#170b10] text-[#f85149]">
              <Lock size={18} />
            </div>
            <div>
              <p className="text-white text-sm font-medium">Change Password</p>
              <p className="text-[#8b949e] text-xs">Update your password to keep your account secure</p>
            </div>
          </div>
          <ArrowRight size={18} className="text-[#8b949e]" />
        </button>
      </div>
    </div>
  );
}
