import { ArrowLeft, Mail } from "lucide-react";

export function ForgotPassword({ email, setEmail, handleForgotPassword, onBack }) {
  return (
    <form onSubmit={handleForgotPassword} className="space-y-4">
      <div className="flex items-center gap-2">
        <button type="button" onClick={onBack} className="text-[#8b949e] cursor-pointer">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-xl font-semibold text-white">Forgot password</h2>
          <p className="text-sm text-[#8b949e]">Enter your email to receive an OTP</p>
        </div>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm text-[#c9d1d9]">Email</span>
        <div className="flex items-center rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2">
          <Mail className="mr-2 h-4 w-4 text-[#8b949e]" />
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="your@email.com"
            className="w-full bg-transparent text-sm text-[#e6edf3] outline-none"
          />
        </div>
      </label>

      <button
        type="submit"
        className="w-full rounded-lg bg-[#58a6ff] px-4 py-2.5 text-sm font-semibold text-[#0d1117] transition hover:bg-[#79b8ff] cursor-pointer"
      >
        Send OTP
      </button>
    </form>
  );
}
