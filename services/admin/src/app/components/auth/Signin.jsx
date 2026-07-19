import { Eye, EyeOff, Lock, Mail } from "lucide-react";

export function Signin({
  email,
  setEmail,
  password,
  setPassword,
  showPassword,
  setShowPassword,
  handleSignIn,
  onForgotPassword,
}) {
  return (
    <form onSubmit={handleSignIn} className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold text-white">Sign in</h2>
        <p className="mt-1 text-sm text-[#8b949e]">Access the HairLync admin console</p>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm text-[#c9d1d9]">Email</span>
        <div className="flex items-center rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2">
          <Mail className="mr-2 h-4 w-4 text-[#8b949e]" />
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="admin@hairlync.com"
            className="w-full bg-transparent text-sm text-[#e6edf3] outline-none"
          />
        </div>
      </label>

      <label className="block">
        <span className="mb-2 block text-sm text-[#c9d1d9]">Password</span>
        <div className="flex items-center rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2">
          <Lock className="mr-2 h-4 w-4 text-[#8b949e]" />
          <input
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            className="w-full bg-transparent text-sm text-[#e6edf3] outline-none"
          />
          <button
            type="button"
            onClick={() => setShowPassword((value) => !value)}
            className="ml-2 text-[#8b949e] cursor-pointer"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </label>

      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={onForgotPassword}
          className="text-sm text-[#58a6ff] hover:underline cursor-pointer"
        >
          Forgot password?
        </button>
      </div>

      <button
        type="submit"
        className="w-full rounded-lg bg-[#58a6ff] px-4 py-2.5 text-sm font-semibold text-[#0d1117] transition hover:bg-[#79b8ff] cursor-pointer"
      >
        Sign In
      </button>
    </form>
  );
}
