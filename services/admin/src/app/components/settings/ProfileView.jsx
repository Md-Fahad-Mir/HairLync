import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  User,
  Mail,
  Globe,
  ShieldCheck,
  Clock3,
} from "lucide-react";
import { ENDPOINTS } from "../../../api/endpoints.js";
import { baseApi } from "../../../api/baseApi.js";

function ProfileField({ label, value }) {
  return (
    <div className="rounded-3xl border border-[#30363d] bg-[#0d1117] p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-[#8b949e] mb-2">
        {label}
      </p>
      <p className="text-sm text-white">{value || "—"}</p>
    </div>
  );
}

export function ProfileView({ onBack }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      setError("");
      setLoading(true);

      try {
        const token = localStorage.getItem("accessToken");
        const response = await baseApi.get(ENDPOINTS.profile, {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        });
        const payload = response?.data?.data || response;
        setProfile(payload);
      
       
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            err?.response?.data?.message ||
            err?.message ||
            "Unable to load profile.",
        );
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  return (
    <div className="space-y-6">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-2 rounded-full border border-[#30363d] bg-[#0d1117] px-4 py-2 text-sm text-[#8b949e] transition hover:border-[#58a6ff] hover:text-white"
      >
        <ArrowLeft size={16} /> Back to Settings
      </button>

      <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#58a6ff]/10 text-[#58a6ff]">
            <User size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">
              Profile Details
            </h2>
            <p className="text-sm text-[#8b949e]">
                View your account details and information below. 
            </p>
          </div>
        </div>
      </div>

      {loading && (
        <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 text-center text-sm text-[#8b949e]">
          Loading profile...
        </div>
      )}

      {error && (
        <div className="rounded-3xl border border-[#ff7b72] bg-[#3f1f1f] p-6 text-sm text-[#ffb3b0]">
          {error}
        </div>
      )}

      {profile && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-[#30363d] bg-[#161b22] p-6 shadow-xl shadow-black/20">
            <div className="grid gap-4 sm:grid-cols-2">
              <ProfileField label="Full Name" value={profile.full_name} />
              <ProfileField label="Email" value={profile.email} />
              <ProfileField label="Role" value={profile.role} />
              <ProfileField
                label="Phone"
                value={profile.phone_number || "Not provided"}
              />
              <ProfileField
                label="Country"
                value={profile.country || "Not provided"}
              />

              <ProfileField
                label="Paid User"
                value={profile.paid_user ? "Yes" : "No"}
              />
              <ProfileField label="Plan" value={profile.current_plan} />

              <ProfileField
                label="Sub Profile"
                value={profile.is_sub_profile ? "Yes" : "No"}
              />
              <ProfileField
                label="Joined"
                value={new Date(profile.date_joined).toLocaleDateString()}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
