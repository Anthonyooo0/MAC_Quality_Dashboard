import React from 'react';
import { TabId, Filters } from '../types';
import FilterPanel from './FilterPanel';
import {
  DashboardIcon,
  AuditIcon,
  RefreshIcon,
  DownloadIcon,
  CollapseIcon,
  ExpandIcon,
  LogoutIcon,
} from '../constants';

interface SidebarProps {
  collapsed: boolean;
  activeTab: TabId;
  filters: Filters;
  categories: string[];
  currentUser: string | null;
  onToggleCollapse: () => void;
  onTabChange: (tab: TabId) => void;
  onFilterChange: (filters: Filters) => void;
  onRefresh: () => void;
  onExportExcel: () => void;
  onExportCsv: () => void;
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  activeTab,
  filters,
  categories,
  onToggleCollapse,
  onTabChange,
  onFilterChange,
  onRefresh,
  onExportExcel,
  onExportCsv,
  currentUser,
  onLogout,
}) => {
  const navItems: { id: TabId | 'audit'; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'data', label: 'Dashboard', icon: DashboardIcon },
    { id: 'audit', label: 'Audit Log', icon: AuditIcon },
  ];

  return (
    <aside
      className={`sidebar flex flex-col ${
        collapsed ? 'w-16' : 'w-64'
      } transition-all duration-300 flex-shrink-0 text-white`}
    >
      {/* Logo / Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 flex items-center justify-center flex-shrink-0">
            <img
              src="/mac_logo.png"
              alt="MAC Logo"
              className="w-full h-full object-contain"
            />
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <h1 className="font-bold text-sm truncate uppercase">Quality Dashboard</h1>
              <p className="text-blue-200 text-[10px] truncate uppercase font-bold tracking-tighter">
                {currentUser || 'MAC Products'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive =
              item.id === 'audit' ? false : activeTab === item.id || (item.id === 'data' && activeTab !== 'data');
            const isActuallyActive = item.id === 'data';

            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.id !== 'audit') onTabChange(item.id as TabId);
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm transition-all ${
                  isActuallyActive
                    ? 'nav-active text-white bg-white/10'
                    : 'text-blue-200 hover:text-white hover:bg-white/5'
                } ${item.id === 'audit' ? 'opacity-50 cursor-not-allowed' : ''}`}
                title={collapsed ? item.label : undefined}
                disabled={item.id === 'audit'}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span className="font-medium">{item.label}</span>}
                {!collapsed && item.id === 'audit' && (
                  <span className="ml-auto text-[9px] font-mono bg-white/10 px-1.5 py-0.5 rounded uppercase">
                    Soon
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Filter panel */}
        <FilterPanel
          filters={filters}
          categories={categories}
          collapsed={collapsed}
          onFilterChange={onFilterChange}
        />

        {/* Action buttons */}
        {!collapsed && (
          <div className="px-4 py-3 border-t border-white/10 space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 block mb-2">
              Actions
            </span>
            <button
              onClick={onRefresh}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <RefreshIcon className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium text-xs">Refresh Data</span>
            </button>
            <button
              onClick={onExportExcel}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <DownloadIcon className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium text-xs">Export Excel</span>
            </button>
            <button
              onClick={onExportCsv}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <DownloadIcon className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium text-xs">Export CSV</span>
            </button>
          </div>
        )}

        {/* Collapsed action icons */}
        {collapsed && (
          <div className="px-2 py-3 border-t border-white/10 space-y-1">
            <button
              onClick={onRefresh}
              className="w-full flex justify-center py-2 text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
              title="Refresh Data"
            >
              <RefreshIcon className="w-5 h-5" />
            </button>
            <button
              onClick={onExportExcel}
              className="w-full flex justify-center py-2 text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
              title="Export Excel"
            >
              <DownloadIcon className="w-5 h-5" />
            </button>
          </div>
        )}
      </nav>

      {/* Sign Out */}
      <div className="p-4 border-t border-white/10">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-sm text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
          title={collapsed ? 'Sign Out' : undefined}
        >
          <LogoutIcon className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span className="font-medium">Sign Out</span>}
        </button>
      </div>

      {/* Collapse toggle */}
      <div className="p-2 border-t border-white/10">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center py-2 text-blue-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ExpandIcon className="w-4 h-4" />
          ) : (
            <CollapseIcon className="w-4 h-4" />
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
