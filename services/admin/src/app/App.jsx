import { jsx, jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { Toaster } from "sonner";
import {
  LayoutDashboard,
  Users,
  Brain,
  Shield,
  Menu,
  X,
  Scissors,
  Bell,
  Settings,
  FileText,
  ChevronRight
} from "lucide-react";
import { Overview } from "./components/overview/Overview.jsx";
import { UserManagement } from "./components/user management/UserManagement.jsx";
import { AuthFlow } from "./components/auth/AuthFlow.jsx";
import { Settings as SettingsView } from "./components/settings/Settings.jsx";
import { TermsAndCondition } from "./components/terms and condition/TermsAndCondition.jsx";
const nav = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "users", label: "User Management", icon: Users },
  { id: "settings", label: "Settings", icon: Settings },
  { id: "terms", label: "Terms & Condition", icon: FileText }
];
function App() {
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [active, setActive] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const current = nav.find((n) => n.id === active);
  const navigate = (id) => {
    setActive(id);
    setSidebarOpen(false);
  };
  const handleLogout = () => {
    setIsSignedIn(false);
    setActive("overview");
    setSidebarOpen(false);
  };

  if (!isSignedIn) {
    return /* @__PURE__ */ jsx(AuthFlow, { onSignIn: () => setIsSignedIn(true) });
  }

  return /* @__PURE__ */ jsxs("div", { className: "min-h-screen bg-[#0d1117] text-[#e6edf3] flex", style: { fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }, children: [
    /* @__PURE__ */ jsx(
      Toaster,
      {
        position: "top-right",
        toastOptions: {
          style: {
            background: "#161b22",
            border: "1px solid #30363d",
            color: "#e6edf3"
          }
        }
      }
    ),
    sidebarOpen && /* @__PURE__ */ jsx(
      "div",
      {
        className: "fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden",
        onClick: () => setSidebarOpen(false)
      }
    ),
    /* @__PURE__ */ jsxs("aside", { className: `fixed top-0 left-0 h-full w-64 bg-[#161b22] border-r border-[#30363d] z-50 flex flex-col transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`, children: [
      /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 px-5 py-5 border-b border-[#30363d]", children: [
        /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-lg bg-gradient-to-br from-[#58a6ff] to-[#ab7df8] flex items-center justify-center", children: /* @__PURE__ */ jsx(Scissors, { size: 16, className: "text-white" }) }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("span", { className: "text-white text-sm", children: "HairLync" }),
          /* @__PURE__ */ jsx("span", { className: "block text-[#8b949e] text-xs", children: "Admin Console" })
        ] }),
        /* @__PURE__ */ jsx("button", { onClick: () => setSidebarOpen(false), className: "ml-auto text-[#8b949e] hover:text-white lg:hidden", children: /* @__PURE__ */ jsx(X, { size: 16 }) })
      ] }),
      /* @__PURE__ */ jsx("nav", { className: "flex-1 px-3 py-4 space-y-1", children: nav.map((item) => {
        const isActive = active === item.id;
        return /* @__PURE__ */ jsxs(
          "button",
          {
            onClick: () => navigate(item.id),
            className: `w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all cursor-pointer ${isActive ? "bg-[#58a6ff]/10 text-[#58a6ff] border border-[#58a6ff]/20" : "text-[#8b949e] hover:text-[#e6edf3] hover:bg-[#1c2128]"}`,
            children: [
              /* @__PURE__ */ jsx(item.icon, { size: 16 }),
              /* @__PURE__ */ jsx("span", { children: item.label }),
              isActive && /* @__PURE__ */ jsx(ChevronRight, { size: 14, className: "ml-auto" })
            ]
          },
          item.id
        );
      }) }),
      /* @__PURE__ */ jsx("div", { className: "px-3 py-4 border-t border-[#30363d]", children: /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-2", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 px-3 py-2 rounded-lg", children: [
          /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-gradient-to-br from-[#f2cc60] to-[#f85149] flex items-center justify-center text-white text-xs shrink-0", children: "SA" }),
          /* @__PURE__ */ jsxs("div", { className: "flex-1 min-w-0", children: [
            /* @__PURE__ */ jsx("p", { className: "text-[#e6edf3] text-sm truncate", children: "Super Admin" }),
            /* @__PURE__ */ jsx("p", { className: "text-[#8b949e] text-xs", children: "admin@hairiq.com" })
          ] })
        ] }),
        /* @__PURE__ */ jsx("button", { onClick: handleLogout, className: "flex items-center justify-center gap-2 rounded-lg border border-[#30363d] px-3 py-2 text-sm text-[#f85149] transition hover:bg-[#3a1f1f] hover:text-[#ff7b72] cursor-pointer", children: [
          /* @__PURE__ */ jsx("span", { children: "Logout" })
        ] })
      ] }) })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex-1 lg:ml-64 flex flex-col min-h-screen", children: [
      /* @__PURE__ */ jsxs("header", { className: "sticky top-0 z-30 bg-[#0d1117]/90 backdrop-blur-md border-b border-[#30363d] px-4 sm:px-6 py-3 flex items-center gap-4", children: [
        /* @__PURE__ */ jsx(
          "button",
          {
            onClick: () => setSidebarOpen(true),
            className: "text-[#8b949e] hover:text-white lg:hidden",
            children: /* @__PURE__ */ jsx(Menu, { size: 20 })
          }
        ),
        /* @__PURE__ */ jsx("div", { className: "flex-1", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-2 text-xs text-[#8b949e]", children: [
          /* @__PURE__ */ jsx("span", { children: "HairLync" }),
          /* @__PURE__ */ jsx(ChevronRight, { size: 12 }),
          /* @__PURE__ */ jsx("span", { className: "text-[#e6edf3]", children: current.label })
        ] }) }),
        /* @__PURE__ */ jsx("div", { className: "flex items-center", children: /* @__PURE__ */ jsx("div", { className: "flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#58a6ff] to-[#ab7df8] text-sm font-semibold text-white", children: "SA" }) })
      ] }),
      /* @__PURE__ */ jsxs("main", { className: "flex-1 px-4 sm:px-6 py-6", children: [
        active === "overview" && /* @__PURE__ */ jsx(Overview, {}),
        active === "users" && /* @__PURE__ */ jsx(UserManagement, {}),
        active === "settings" && /* @__PURE__ */ jsx(SettingsView, {}),
        active === "terms" && /* @__PURE__ */ jsx(TermsAndCondition, {})
      ] })
    ] })
  ] });
}
export {
  App as default
};
