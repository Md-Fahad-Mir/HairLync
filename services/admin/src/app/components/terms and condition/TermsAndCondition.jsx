import { FileText } from "lucide-react";

export function TermsAndCondition() {
  return (
    <div className="rounded-2xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
      <div className="max-w-2xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#58a6ff]/10 text-[#58a6ff]">
            <FileText size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Terms & Condition</h2>
            <p className="text-sm text-[#8b949e]">Read the platform terms, privacy policy, and service rules before using the system.</p>
          </div>
        </div>
        <div className="rounded-xl border border-[#30363d] bg-[#0d1117] p-4 text-sm text-[#e6edf3]">
          <div className="space-y-3">
            <p>By using HairLync, you agree to follow all platform rules, protect user data, and comply with service policies.</p>
            <p>All account activity must remain secure, transparent, and aligned with the applicable terms of service.</p>
            <p>Administrators are responsible for approving only valid partners and maintaining a safe environment for clients and salons.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
