"use client";

import { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { dashboard, logs as logsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Send, Users, AlertCircle, Clock, TrendingUp, Activity } from "lucide-react";
import { useSearchParams } from "next/navigation";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [activityLogs, setLogs] = useState<any[]>([]);
  const [tab, setTab] = useState<"overview" | "logs">("overview");
  const params = useSearchParams();

  useEffect(() => {
    if (params.get("tab") === "logs") setTab("logs");
    dashboard.stats().then(setStats).catch(() => {});
    logsApi.list(0, 50).then(setLogs).catch(() => {});
  }, [params]);

  const statCards = stats
    ? [
        { label: "Total Sent", value: stats.total_sent, icon: Send, color: "text-green-600 bg-green-50" },
        { label: "Failed", value: stats.total_failed, icon: AlertCircle, color: "text-red-600 bg-red-50" },
        { label: "Pending Queue", value: stats.total_pending, icon: Clock, color: "text-yellow-600 bg-yellow-50" },
        { label: "Total Contacts", value: stats.total_contacts, icon: Users, color: "text-blue-600 bg-blue-50" },
        { label: "Campaigns", value: stats.total_campaigns, icon: TrendingUp, color: "text-purple-600 bg-purple-50" },
        { label: "Today", value: stats.campaigns_today, icon: Activity, color: "text-indigo-600 bg-indigo-50" },
      ]
    : [];

  return (
    <Shell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <div className="flex gap-2">
            <Button variant={tab === "overview" ? "primary" : "secondary"} size="sm" onClick={() => setTab("overview")}>Overview</Button>
            <Button variant={tab === "logs" ? "primary" : "secondary"} size="sm" onClick={() => setTab("logs")}>Activity Logs</Button>
          </div>
        </div>

        {tab === "overview" && (
          <>
            {/* Stat cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {statCards.map((s) => (
                <Card key={s.label}>
                  <CardContent className="flex items-center gap-3 py-5">
                    <div className={`p-2 rounded-lg ${s.color}`}><s.icon className="w-5 h-5" /></div>
                    <div>
                      <p className="text-2xl font-bold">{s.value}</p>
                      <p className="text-xs text-gray-500">{s.label}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Chart */}
            {stats?.daily_sent_data && (
              <Card>
                <CardHeader><h3 className="font-semibold text-gray-800">Messages Sent (Last 7 Days)</h3></CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stats.daily_sent_data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#22c55e" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {tab === "logs" && (
          <Card>
            <CardHeader><h3 className="font-semibold text-gray-800">Activity Logs</h3></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead><tr className="border-b text-left text-gray-500">
                    <th className="pb-2 pr-4">Time</th><th className="pb-2 pr-4">Action</th><th className="pb-2">Detail</th>
                  </tr></thead>
                  <tbody>
                    {activityLogs.map((l) => (
                      <tr key={l.id} className="border-b border-gray-50">
                        <td className="py-2 pr-4 text-gray-400 whitespace-nowrap">{formatDate(l.created_at)}</td>
                        <td className="py-2 pr-4 font-medium">{l.action}</td>
                        <td className="py-2 text-gray-500 truncate max-w-md">{l.detail}</td>
                      </tr>
                    ))}
                    {!activityLogs.length && <tr><td colSpan={3} className="py-8 text-center text-gray-400">No activity yet</td></tr>}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Shell>
  );
}
