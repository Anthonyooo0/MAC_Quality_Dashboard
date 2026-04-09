import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Complaint } from '../types';

interface AnalyticsTabProps {
  complaints: Complaint[];
}

const AnalyticsTab: React.FC<AnalyticsTabProps> = ({ complaints }) => {
  // Monthly complaints (all time)
  const monthlyData = useMemo(() => {
    const counts: Record<string, number> = {};
    complaints.forEach((c) => {
      if (!c.first_seen_utc) return;
      try {
        const d = new Date(c.first_seen_utc);
        if (isNaN(d.getTime())) return;
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        counts[key] = (counts[key] || 0) + 1;
      } catch {
        // skip
      }
    });

    return Object.entries(counts)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, count]) => ({
        month,
        complaints: count,
      }));
  }, [complaints]);

  // Last 12 weeks
  const weeklyData = useMemo(() => {
    const now = new Date();
    const weeks: { label: string; start: Date; end: Date }[] = [];

    for (let i = 11; i >= 0; i--) {
      const end = new Date(now);
      end.setDate(end.getDate() - i * 7);
      const start = new Date(end);
      start.setDate(start.getDate() - 6);
      const label = `${start.getMonth() + 1}/${start.getDate()}`;
      weeks.push({ label, start, end });
    }

    return weeks.map((week) => {
      const count = complaints.filter((c) => {
        if (!c.first_seen_utc) return false;
        try {
          const d = new Date(c.first_seen_utc);
          return d >= week.start && d <= week.end;
        } catch {
          return false;
        }
      }).length;

      return { week: week.label, complaints: count };
    });
  }, [complaints]);

  return (
    <div className="view-transition space-y-6">
      {/* Monthly trend */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b bg-slate-50">
          <h3 className="font-bold text-slate-700 text-sm">Monthly Complaints Trend</h3>
        </div>
        <div className="p-5">
          {monthlyData.length === 0 ? (
            <div className="text-center text-slate-400 py-12">No data available</div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line
                  type="monotone"
                  dataKey="complaints"
                  stroke="#1a365d"
                  strokeWidth={2}
                  dot={{ fill: '#1a365d', r: 4 }}
                  activeDot={{ r: 6, fill: '#3182ce' }}
                  name="Complaints"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Last 12 weeks */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b bg-slate-50">
          <h3 className="font-bold text-slate-700 text-sm">Last 12 Weeks</h3>
        </div>
        <div className="p-5">
          {weeklyData.every((d) => d.complaints === 0) ? (
            <div className="text-center text-slate-400 py-12">No data in the last 12 weeks</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="week"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar
                  dataKey="complaints"
                  fill="#1a365d"
                  radius={[4, 4, 0, 0]}
                  name="Complaints"
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsTab;
