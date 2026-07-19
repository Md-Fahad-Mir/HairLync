import { ArrowLeft } from "lucide-react";

export function VerifyOtp({
  otpDigits,
  setOtpDigits,
  otpRefs,
  handleOtpChange,
  handleOtpKeyDown,
  handleVerifyOtp,
  onBack,
}) {
  return (
    <form onSubmit={handleVerifyOtp} className="space-y-4">
      <div className="flex items-center gap-2">
        <button type="button" onClick={onBack} className="text-[#8b949e] cursor-pointer">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-xl font-semibold text-white">Verify OTP</h2>
          <p className="text-sm text-[#8b949e]">Enter the 6-digit code received</p>
        </div>
      </div>

      <div className="flex items-center justify-between gap-2">
        {otpDigits.map((digit, index) => (
          <input
            key={index}
            ref={(element) => {
              otpRefs.current[index] = element;
            }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(event) => handleOtpChange(index, event.target.value)}
            onKeyDown={(event) => handleOtpKeyDown(index, event)}
            onPaste={(event) => {
              event.preventDefault();
              const pasted = event.clipboardData.getData("text").replace(/\D/g, "");
              const digits = pasted.slice(0, otpDigits.length).split("");
              const next = [...otpDigits];
              digits.forEach((digitValue, offset) => {
                const targetIndex = index + offset;
                if (targetIndex < next.length) {
                  next[targetIndex] = digitValue;
                }
              });
              setOtpDigits(next);
              const nextIndex = Math.min(index + digits.length, otpDigits.length - 1);
              otpRefs.current[nextIndex]?.focus();
            }}
            className="h-12 w-12 rounded-lg border border-[#30363d] bg-[#0d1117] text-center text-lg font-semibold text-white outline-none focus:border-[#58a6ff]"
          />
        ))}
      </div>

      <button
        type="submit"
        className="w-full rounded-lg bg-[#58a6ff] px-4 py-2.5 text-sm font-semibold text-[#0d1117] transition hover:bg-[#79b8ff] cursor-pointer"
      >
        Verify OTP
      </button>
    </form>
  );
}
