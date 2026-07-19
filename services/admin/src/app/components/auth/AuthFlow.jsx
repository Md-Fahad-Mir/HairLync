import { useRef, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { Signin } from "./Signin";
import { ForgotPassword } from "./ForgotPassword";
import { VerifyOtp } from "./VerifyOtp";
import { ResetPassword } from "./ResetPassword";

export function AuthFlow({ onSignIn }) {
  const [step, setStep] = useState("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otpDigits, setOtpDigits] = useState(["", "", "", "", "", ""]);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const otpRefs = useRef([]);

  const handleSignIn = (event) => {
    event.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }
    setError("");
    toast.success("Signed in successfully");
    onSignIn?.();
  };

  const handleForgotPassword = (event) => {
    event.preventDefault();
    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }
    setError("");
    toast.success("Verification code sent to your email");
    setStep("otp");
  };

  const handleOtpChange = (index, value) => {
    const sanitized = value.replace(/\D/g, "").slice(0, 1);
    const next = [...otpDigits];
    next[index] = sanitized;
    setOtpDigits(next);

    if (sanitized && index < otpDigits.length - 1) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index, event) => {
    if (event.key === "Backspace" && !otpDigits[index] && index > 0) {
      const next = [...otpDigits];
      next[index - 1] = "";
      setOtpDigits(next);
      otpRefs.current[index - 1]?.focus();
      return;
    }

    if (event.key === "ArrowLeft" && index > 0) {
      event.preventDefault();
      otpRefs.current[index - 1]?.focus();
    }

    if (event.key === "ArrowRight" && index < otpDigits.length - 1) {
      event.preventDefault();
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleVerifyOtp = (event) => {
    event.preventDefault();
    const code = otpDigits.join("");
    if (code.length !== 6) {
      setError("Enter the 6-digit verification code.");
      return;
    }
    setError("");
    setStep("reset");
  };

  const handleResetPassword = (event) => {
    event.preventDefault();
    if (!newPassword.trim() || !confirmPassword.trim()) {
      setError("Please enter both password fields.");
      return;
    }
    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    toast.success("Password reset successfully");
    setStep("signin");
    setPassword(newPassword);
    setNewPassword("");
    setConfirmPassword("");
    setOtpDigits(["", "", "", "", "", ""]);
  };

  const goToForgotPassword = () => {
    setError("");
    setStep("forgot");
  };

  const goBackToSignin = () => setStep("signin");
  const goBackToForgot = () => setStep("forgot");
  const goBackToOtp = () => setStep("otp");

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-[#30363d] bg-[#161b22] p-6 shadow-2xl shadow-black/40">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#58a6ff] to-[#ab7df8]">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">HairLync Admin</p>
            <p className="text-sm text-[#8b949e]">Secure access portal</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-[#f85149]/40 bg-[#3a1f1f] px-3 py-2 text-sm text-[#f85149]">
            {error}
          </div>
        )}

        {step === "signin" && (
          <Signin
            email={email}
            setEmail={setEmail}
            password={password}
            setPassword={setPassword}
            showPassword={showPassword}
            setShowPassword={setShowPassword}
            handleSignIn={handleSignIn}
            onForgotPassword={goToForgotPassword}
          />
        )}

        {step === "forgot" && (
          <ForgotPassword
            email={email}
            setEmail={setEmail}
            handleForgotPassword={handleForgotPassword}
            onBack={goBackToSignin}
          />
        )}

        {step === "otp" && (
          <VerifyOtp
            otpDigits={otpDigits}
            setOtpDigits={setOtpDigits}
            otpRefs={otpRefs}
            handleOtpChange={handleOtpChange}
            handleOtpKeyDown={handleOtpKeyDown}
            handleVerifyOtp={handleVerifyOtp}
            onBack={goBackToForgot}
          />
        )}

        {step === "reset" && (
          <ResetPassword
            newPassword={newPassword}
            setNewPassword={setNewPassword}
            confirmPassword={confirmPassword}
            setConfirmPassword={setConfirmPassword}
            showNewPassword={showNewPassword}
            setShowNewPassword={setShowNewPassword}
            showConfirmPassword={showConfirmPassword}
            setShowConfirmPassword={setShowConfirmPassword}
            handleResetPassword={handleResetPassword}
            onBack={goBackToOtp}
          />
        )}
      </div>
    </div>
  );
}
