import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { ENDPOINTS } from "../../../api/endpoints.js";
import { baseApi } from "../../../api/baseApi.js";

export function ChangePasswordView({ onBack }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("All fields are required.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirm password must match.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      const token = localStorage.getItem("accessToken");
      const { data } = await baseApi.post(
        ENDPOINTS.change_password,
        {
          old_password: oldPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        },
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        }
      );

      toast.success(data?.message || "Password changed successfully.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || "Unable to change password.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
   
     <div className="space-y-6 max-w-4xl mx-auto">
      <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
        <div className="flex items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-3">
            <div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={onBack}
                  className="inline-flex items-center justify-center rounded-full border border-[#30363d] bg-[#0d1117] p-2 text-sm text-[#8b949e] transition hover:border-[#f85149] hover:text-white"
                >
                  <ArrowLeft size={16} />
                </button>
                <h2 className="text-xl font-semibold text-white">Change Password</h2>
              </div>
              <p className="text-sm text-[#8b949e]">Use your current password to set a new one securely.</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm text-[#8b949e]">Old Password</span>
            <input
              type="password"
              value={oldPassword}
              onChange={(event) => setOldPassword(event.target.value)}
              className="mt-2 w-full rounded-3xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-white outline-none focus:border-[#f85149]"
              placeholder="Enter current password"
            />
          </label>

          <label className="block">
            <span className="text-sm text-[#8b949e]">New Password</span>
            <input
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              className="mt-2 w-full rounded-3xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-white outline-none focus:border-[#f85149]"
              placeholder="Enter new password"
            />
          </label>

          <label className="block">
            <span className="text-sm text-[#8b949e]">Confirm Password</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              className="mt-2 w-full rounded-3xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-white outline-none focus:border-[#f85149]"
              placeholder="Confirm new password"
            />
          </label>

          {error && <p className="text-sm text-[#ff7b72]">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full rounded-3xl px-4 py-3 text-sm font-semibold text-white transition ${isSubmitting ? "bg-[#6c2e3c] cursor-not-allowed" : "bg-[#f85149] hover:bg-[#ff6d6d]"} cursor-pointer`}
          >
            {isSubmitting ? "Changing password..." : "Change Password"}
          </button>
        </form>
      </div>
    </div>
   
  );
}
