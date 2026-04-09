import React, { useState, useMemo } from 'react';
import { Complaint, SortConfig, ColumnKey } from '../types';
import { ALL_COLUMNS, SortAscIcon, SortDescIcon } from '../constants';
import { toEasternTime } from '../utils/dateUtils';

interface DataTableProps {
  complaints: Complaint[];
}

const DataTable: React.FC<DataTableProps> = ({ complaints }) => {
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: 'first_seen_utc',
    direction: 'desc',
  });
  const [visibleColumns, setVisibleColumns] = useState<Set<ColumnKey>>(
    new Set(ALL_COLUMNS.filter((c) => c.defaultVisible).map((c) => c.key))
  );
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [page, setPage] = useState(0);
  const pageSize = 50;

  const toggleColumn = (key: ColumnKey) => {
    setVisibleColumns((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const handleSort = (key: string) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const sorted = useMemo(() => {
    const arr = [...complaints];
    arr.sort((a, b) => {
      const aVal = (a as unknown as Record<string, string | null>)[sortConfig.key];
      const bVal = (b as unknown as Record<string, string | null>)[sortConfig.key];
      const aStr = (aVal || '').toLowerCase();
      const bStr = (bVal || '').toLowerCase();
      if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return arr;
  }, [complaints, sortConfig]);

  const totalPages = Math.ceil(sorted.length / pageSize);
  const paginated = sorted.slice(page * pageSize, (page + 1) * pageSize);

  const columns = ALL_COLUMNS.filter((c) => visibleColumns.has(c.key));

  const renderCell = (complaint: Complaint, key: ColumnKey) => {
    switch (key) {
      case 'first_seen_utc':
        return (
          <span className="font-mono text-xs text-slate-600">
            {toEasternTime(complaint.first_seen_utc)}
          </span>
        );
      case 'thread_url':
        return complaint.thread_url ? (
          <a
            href={complaint.thread_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-mac-accent hover:text-mac-blue font-medium text-xs underline"
          >
            Open
          </a>
        ) : (
          <span className="text-slate-300 text-xs">--</span>
        );
      case 'summary':
        return (
          <span className="text-xs text-slate-600 line-clamp-2" title={complaint.summary || ''}>
            {complaint.summary || ''}
          </span>
        );
      case 'initiator_email':
        return <span className="text-xs text-slate-700 font-medium">{complaint.initiator_email || ''}</span>;
      case 'part_number':
        return (
          <span className="font-mono text-xs text-slate-700">
            {complaint.part_number || ''}
          </span>
        );
      case 'category':
        return complaint.category ? (
          <span className="px-2 py-0.5 bg-blue-50 text-mac-accent rounded text-[10px] font-bold uppercase border border-blue-200">
            {complaint.category}
          </span>
        ) : (
          <span className="text-slate-300 text-xs">--</span>
        );
      case 'subject':
        return (
          <span className="text-xs text-slate-600 line-clamp-1" title={complaint.subject || ''}>
            {complaint.subject || ''}
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="view-transition">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-slate-500">
          Showing <span className="font-bold text-slate-700">{paginated.length}</span> of{' '}
          <span className="font-bold text-slate-700">{sorted.length}</span> complaints
        </div>
        <div className="relative">
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg transition-all"
          >
            Columns
          </button>
          {showColumnSelector && (
            <div className="absolute right-0 top-full mt-1 bg-white rounded-xl border border-slate-200 shadow-lg p-3 z-50 min-w-[180px]">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Show Columns
              </div>
              {ALL_COLUMNS.map((col) => (
                <label
                  key={col.key}
                  className="flex items-center gap-2 py-1 cursor-pointer hover:bg-slate-50 px-1 rounded"
                >
                  <input
                    type="checkbox"
                    checked={visibleColumns.has(col.key)}
                    onChange={() => toggleColumn(col.key)}
                    className="rounded border-slate-300 text-mac-accent focus:ring-mac-accent/20"
                  />
                  <span className="text-xs text-slate-700">{col.label}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className="px-4 py-3 font-bold text-slate-600 text-xs uppercase tracking-wider cursor-pointer sort-header select-none whitespace-nowrap"
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      {sortConfig.key === col.key && (
                        sortConfig.direction === 'asc' ? (
                          <SortAscIcon className="w-3 h-3" />
                        ) : (
                          <SortDescIcon className="w-3 h-3" />
                        )
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginated.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-400">
                    No complaints match the current filters.
                  </td>
                </tr>
              ) : (
                paginated.map((complaint, idx) => (
                  <tr
                    key={complaint.conversation_id}
                    className={`hover:bg-slate-50 transition-colors ${
                      idx % 2 === 1 ? 'bg-slate-50/50' : ''
                    }`}
                  >
                    {columns.map((col) => (
                      <td key={col.key} className="px-4 py-3 max-w-xs">
                        {renderCell(complaint, col.key)}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <div className="text-xs text-slate-500">
            Page {page + 1} of {totalPages}
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(0)}
              disabled={page === 0}
              className="px-2 py-1 text-xs border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              First
            </button>
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-2 py-1 text-xs border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-2 py-1 text-xs border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              Next
            </button>
            <button
              onClick={() => setPage(totalPages - 1)}
              disabled={page >= totalPages - 1}
              className="px-2 py-1 text-xs border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              Last
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
