import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Users, UserRound, Scissors, Store } from "lucide-react";
import { users } from "../data";

const metrics = [
  { label: "Total User", value: "8,742", sub: "342 new this week", icon: Users, color: "#58a6ff", bg: "rgba(88,166,255,0.1)" },
  { label: "Client", value: "5,240", sub: "128 active today", icon: UserRound, color: "#ab7df8", bg: "rgba(171,125,248,0.1)" },
  { label: "Barber", value: "186", sub: "12 online now", icon: Scissors, color: "#3fb950", bg: "rgba(63,185,80,0.1)" },
  { label: "Salon", value: "94", sub: "18 pending approval", icon: Store, color: "#f2cc60", bg: "rgba(242,204,96,0.1)" },
];

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const availableYears = [...new Set(users.map((user) => new Date(user.joined).getFullYear()))].sort();

function getMonthlyGrowthData(year) {
  return monthNames.map((month, index) => ({
    month,
    count: users.filter((user) => {
      const joinedAt = new Date(user.joined);
      return joinedAt.getFullYear() === year && joinedAt.getMonth() === index;
    }).length,
  }));
}

export function Overview() {
  const [selectedYear, setSelectedYear] = useState(availableYears[availableYears.length - 1]);
  const growthData = getMonthlyGrowthData(selectedYear);
  const maxCount = Math.max(...growthData.map((item) => item.count), 4);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl text-white mb-1">System Overview</h1>
        <p className="text-[#8b949e] text-sm">Real-time platform performance & business metrics</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <p className="text-[#8b949e] text-xs uppercase tracking-wider mb-1">{m.label}</p>
                <p className="text-white text-2xl">{m.value}</p>
              </div>
              <div className="rounded-lg p-2" style={{ background: m.bg }}>
                <m.icon size={20} style={{ color: m.color }} />
              </div>
            </div>
            <p className="text-[#3fb950] text-xs">{m.sub}</p>
          </div>
        ))}
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-white">User Growth Ratio</h2>
          <label className="flex items-center gap-2 text-sm text-[#8b949e]">
            <span>Year</span>
            <select
              value={selectedYear}
              onChange={(event) => setSelectedYear(Number(event.target.value))}
              className="rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] outline-none"
            >
              {availableYears.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </label>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={growthData} barSize={20}>
            <XAxis dataKey="month" tick={{ fill: "#8b949e", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#8b949e", fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, maxCount + 2]} />
            <Tooltip
              formatter={(value) => [`${value} users`, "Joined"]}
              contentStyle={{ background: "#161b22", border: "1px solid #30363d", borderRadius: 8, color: "#fff" }}
            />
            <Bar dataKey="count" name="Joined" fill="#58a6ff" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
