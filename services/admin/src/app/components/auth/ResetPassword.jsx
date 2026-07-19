import { ArrowLeft, Eye, EyeOff, Lock } from "lucide-react";

export function ResetPassword({
  newPassword,
  setNewPassword,
  confirmPassword,
  setConfirmPassword,
  showNewPassword,
  setShowNewPassword,
  showConfirmPassword,
  setShowConfirmPassword,
  handleResetPassword,
  onBack,
}) {
  return (
    <form onSubmit={handleResetPassword} className="space-y-4">
      <div className="flex items-center gap-2">
        <button type="button" onClick={onBack} className="text-[#8b949e] cursor-pointer">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-xl font-semibold text-white">Reset password</h2>
          <p className="text-sm text-[#8b949e]">Choose a new secure password</p>
        </div>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm text-[#c9d1d9]">New password</span>
        <div className="flex items-center rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2">
          <Lock className="mr-2 h-4 w-4 text-[#8b949e]" />
          <input
            type={showNewPassword ? "text" : "password"}
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            placeholder="Enter a new password"
            className="w-full bg-transparent text-sm text-[#e6edf3] outline-none"
          />
          <button
            type="button"
            onClick={() => setShowNewPassword((value) => !value)}
            className="ml-2 text-[#8b949e] cursor-pointer"
          >
            {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </label>

      <label className="block">
        <span className="mb-2 block text-sm text-[#c9d1d9]">Confirm password</span>
        <div className="flex items-center rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2">
          <Lock className="mr-2 h-4 w-4 text-[#8b949e]" />
          <input
            type={showConfirmPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Confirm your password"
            className="w-full bg-transparent text-sm text-[#e6edf3] outline-none"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword((value) => !value)}
            className="ml-2 text-[#8b949e] cursor-pointer"
          >
            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </label>

      <button
        type="submit"
        className="w-full rounded-lg bg-[#58a6ff] px-4 py-2.5 text-sm font-semibold text-[#0d1117] transition hover:bg-[#79b8ff] cursor-pointer"
      >
        Reset password
      </button>
    </form>
  );
}
