import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import initSqlJs, { Database } from 'sql.js';
import { Complaint, Filters, TabId, ToastMessage } from './types';
import { DB_URL, SQL_WASM_URL } from './constants';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import MetricsRow from './components/MetricsRow';
import DataTable from './components/DataTable';
import AnalyticsTab from './components/AnalyticsTab';
import CategoryBreakdown from './components/CategoryBreakdown';
import { ToastContainer } from './components/Toast';
import { exportToExcel, exportToCsv } from './utils/exportUtils';
import { parseDate } from './utils/dateUtils';

const DEFAULT_FILTERS: Filters = {
  category: '',
  partNumber: '',
  initiatedBy: '',
  subject: '',
  dateStart: '',
  dateEnd: '',
};

let toastCounter = 0;

const App: React.FC = () => {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [activeTab, setActiveTab] = useState<TabId>('data');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    if (isAuthenticated && accounts.length > 0) {
      setCurrentUser(accounts[0].username?.toLowerCase() || null);
    }
  }, [isAuthenticated, accounts]);

  const handleLogout = async () => {
    await instance.logoutPopup();
    setCurrentUser(null);
  };

  const addToast = useCallback((message: string, type: ToastMessage['type']) => {
    const id = ++toastCounter;
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const loadDatabase = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const SQL = await initSqlJs({ locateFile: () => SQL_WASM_URL });

      const response = await fetch(DB_URL);
      if (!response.ok) {
        throw new Error(`Failed to download database: ${response.status} ${response.statusText}`);
      }

      const buffer = await response.arrayBuffer();
      const db: Database = new SQL.Database(new Uint8Array(buffer));

      const results = db.exec(
        `SELECT conversation_id, received_utc, from_email, subject, part_number,
                category, summary, case_key, thread_url, first_seen_utc, initiator_email
         FROM complaints
         ORDER BY first_seen_utc DESC`
      );

      if (results.length > 0) {
        const cols = results[0].columns;
        const rows: Complaint[] = results[0].values.map((row) => {
          const obj: Record<string, unknown> = {};
          cols.forEach((col, i) => {
            obj[col] = row[i] !== null ? String(row[i]) : null;
          });
          return obj as unknown as Complaint;
        });
        setComplaints(rows);
      } else {
        setComplaints([]);
      }

      db.close();
      addToast(`Loaded ${results.length > 0 ? results[0].values.length : 0} complaints`, 'success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error loading database';
      setError(msg);
      addToast(`Error: ${msg}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  // Load database when user authenticates
  useEffect(() => {
    if (currentUser) {
      loadDatabase();
    }
  }, [currentUser, loadDatabase]);

  const categories = useMemo(() => {
    const cats = new Set<string>();
    complaints.forEach((c) => {
      if (c.category) cats.add(c.category);
    });
    return Array.from(cats).sort();
  }, [complaints]);

  const filteredComplaints = useMemo(() => {
    return complaints.filter((c) => {
      if (filters.category && c.category !== filters.category) return false;
      if (filters.partNumber) {
        const pn = (c.part_number || '').toLowerCase();
        if (!pn.includes(filters.partNumber.toLowerCase())) return false;
      }
      if (filters.initiatedBy) {
        const email = (c.initiator_email || '').toLowerCase();
        if (!email.includes(filters.initiatedBy.toLowerCase())) return false;
      }
      if (filters.subject) {
        const subj = (c.subject || '').toLowerCase();
        if (!subj.includes(filters.subject.toLowerCase())) return false;
      }
      if (filters.dateStart || filters.dateEnd) {
        const d = parseDate(c.first_seen_utc);
        if (!d) return false;
        if (filters.dateStart) {
          const start = new Date(filters.dateStart);
          start.setHours(0, 0, 0, 0);
          if (d < start) return false;
        }
        if (filters.dateEnd) {
          const end = new Date(filters.dateEnd);
          end.setHours(23, 59, 59, 999);
          if (d > end) return false;
        }
      }
      return true;
    });
  }, [complaints, filters]);

  const handleRefresh = () => loadDatabase();

  const handleExportExcel = () => {
    if (filteredComplaints.length === 0) {
      addToast('No data to export', 'warning');
      return;
    }
    exportToExcel(filteredComplaints);
    addToast(`Exported ${filteredComplaints.length} complaints to Excel`, 'success');
  };

  const handleExportCsv = () => {
    if (filteredComplaints.length === 0) {
      addToast('No data to export', 'warning');
      return;
    }
    exportToCsv(filteredComplaints);
    addToast(`Exported ${filteredComplaints.length} complaints to CSV`, 'success');
  };

  // Not authenticated — show login
  if (!currentUser) {
    return <Login onLogin={setCurrentUser} />;
  }

  // Loading screen
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-mac-light">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4">
            <img src="/mac_logo.png" alt="MAC Logo" className="w-full h-full object-contain animate-pulse" />
          </div>
          <p className="text-slate-600 font-medium">Loading Quality Dashboard...</p>
          <p className="text-slate-400 text-sm mt-1">Downloading complaint database</p>
        </div>
      </div>
    );
  }

  // Error screen
  if (error && complaints.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-mac-light">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4">
            <img src="/mac_logo.png" alt="MAC Logo" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-xl font-bold text-slate-800 mb-2">Failed to Load Data</h1>
          <p className="text-slate-500 text-sm mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-mac-navy hover:bg-mac-blue text-white font-bold rounded-lg text-sm transition-all shadow-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const tabs: { id: TabId; label: string }[] = [
    { id: 'data', label: 'Data Table' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'categories', label: 'Category Breakdown' },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-mac-light">
      <Sidebar
        collapsed={sidebarCollapsed}
        activeTab={activeTab}
        filters={filters}
        categories={categories}
        currentUser={currentUser}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onTabChange={setActiveTab}
        onFilterChange={setFilters}
        onRefresh={handleRefresh}
        onExportExcel={handleExportExcel}
        onExportCsv={handleExportCsv}
        onLogout={handleLogout}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">Quality Dashboard</h1>
            <p className="text-xs text-slate-400 mt-0.5">Complaint tracking and analytics</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded uppercase">
              V1.0.0
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="view-transition space-y-6">
            <MetricsRow allComplaints={complaints} filteredComplaints={filteredComplaints} />

            <div className="flex gap-1 bg-white rounded-lg border border-slate-200 p-1 w-fit shadow-sm">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 text-sm font-bold rounded-md transition-all ${
                    activeTab === tab.id
                      ? 'bg-mac-navy text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'data' && <DataTable complaints={filteredComplaints} />}
            {activeTab === 'analytics' && <AnalyticsTab complaints={filteredComplaints} />}
            {activeTab === 'categories' && <CategoryBreakdown complaints={filteredComplaints} />}
          </div>
        </div>
      </main>

      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
};

export default App;
