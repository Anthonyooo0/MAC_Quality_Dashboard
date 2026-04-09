import React from 'react';
import { Complaint } from '../types';

interface MetricsRowProps {
  allComplaints: Complaint[];
  filteredComplaints: Complaint[];
}

const MetricsRow: React.FC<MetricsRowProps> = ({ allComplaints, filteredComplaints }) => {
  const totalComplaints = allComplaints.length;
  const displayed = filteredComplaints.length;

  const categories = new Set(
    filteredComplaints.map((c) => c.category).filter(Boolean)
  );
  const uniquePartNumbers = new Set(
    filteredComplaints.map((c) => c.part_number).filter(Boolean)
  );

  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const last30Days = filteredComplaints.filter((c) => {
    if (!c.first_seen_utc) return false;
    try {
      const d = new Date(c.first_seen_utc);
      return d >= thirtyDaysAgo;
    } catch {
      return false;
    }
  }).length;

  const cards = [
    {
      label: 'Total Complaints',
      value: totalComplaints,
      borderColor: 'border-l-red-500',
    },
    {
      label: 'Displayed',
      value: displayed,
      borderColor: 'border-l-mac-accent',
    },
    {
      label: 'Categories',
      value: categories.size,
      borderColor: 'border-l-blue-500',
    },
    {
      label: 'Unique P/Ns',
      value: uniquePartNumbers.size,
      borderColor: 'border-l-green-500',
    },
    {
      label: 'Last 30 Days',
      value: last30Days,
      borderColor: 'border-l-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`bg-white p-5 rounded-xl border-l-4 ${card.borderColor} shadow-sm`}
        >
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            {card.label}
          </div>
          <div className="text-3xl font-bold text-slate-800 mt-1">{card.value}</div>
        </div>
      ))}
    </div>
  );
};

export default MetricsRow;
