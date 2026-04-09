import React from 'react';
import { Filters } from '../types';

interface FilterPanelProps {
  filters: Filters;
  categories: string[];
  collapsed: boolean;
  onFilterChange: (filters: Filters) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  categories,
  collapsed,
  onFilterChange,
}) => {
  const update = (key: keyof Filters, value: string) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const clearAll = () => {
    onFilterChange({
      category: '',
      partNumber: '',
      initiatedBy: '',
      subject: '',
      dateStart: '',
      dateEnd: '',
    });
  };

  const hasFilters = Object.values(filters).some((v) => v !== '');

  if (collapsed) return null;

  return (
    <div className="px-4 py-3 border-t border-white/10">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300">
          Filters
        </span>
        {hasFilters && (
          <button
            onClick={clearAll}
            className="text-[10px] text-blue-300 hover:text-white transition-colors uppercase font-bold"
          >
            Clear
          </button>
        )}
      </div>

      <div className="space-y-2">
        {/* Category */}
        <div>
          <label className="block text-[10px] font-bold text-blue-300/70 uppercase mb-1">
            Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => update('category', e.target.value)}
            className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs focus:border-blue-400 focus:outline-none"
          >
            <option value="" className="text-slate-800">
              (All)
            </option>
            {categories.map((cat) => (
              <option key={cat} value={cat} className="text-slate-800">
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Part Number */}
        <div>
          <label className="block text-[10px] font-bold text-blue-300/70 uppercase mb-1">
            Part Number
          </label>
          <input
            type="text"
            value={filters.partNumber}
            onChange={(e) => update('partNumber', e.target.value)}
            placeholder="Search..."
            className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs placeholder-blue-300/40 focus:border-blue-400 focus:outline-none"
          />
        </div>

        {/* Initiated By */}
        <div>
          <label className="block text-[10px] font-bold text-blue-300/70 uppercase mb-1">
            Initiated By
          </label>
          <input
            type="text"
            value={filters.initiatedBy}
            onChange={(e) => update('initiatedBy', e.target.value)}
            placeholder="Search..."
            className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs placeholder-blue-300/40 focus:border-blue-400 focus:outline-none"
          />
        </div>

        {/* Subject */}
        <div>
          <label className="block text-[10px] font-bold text-blue-300/70 uppercase mb-1">
            Subject
          </label>
          <input
            type="text"
            value={filters.subject}
            onChange={(e) => update('subject', e.target.value)}
            placeholder="Search..."
            className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs placeholder-blue-300/40 focus:border-blue-400 focus:outline-none"
          />
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-[10px] font-bold text-blue-300/70 uppercase mb-1">
            Date Range
          </label>
          <div className="space-y-1">
            <input
              type="date"
              value={filters.dateStart}
              onChange={(e) => update('dateStart', e.target.value)}
              className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs focus:border-blue-400 focus:outline-none [color-scheme:dark]"
            />
            <input
              type="date"
              value={filters.dateEnd}
              onChange={(e) => update('dateEnd', e.target.value)}
              className="w-full px-2 py-1.5 rounded-lg bg-white/10 border border-white/10 text-white text-xs focus:border-blue-400 focus:outline-none [color-scheme:dark]"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
