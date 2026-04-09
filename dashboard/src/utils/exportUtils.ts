import * as XLSX from 'xlsx';
import { Complaint } from '../types';
import { toEasternTime } from './dateUtils';

interface ExportRow {
  'Date (ET)': string;
  'Initiated By': string;
  'Part Number': string;
  'Category': string;
  'Summary': string;
  'Subject': string;
  'Thread URL': string;
  'From Email': string;
  'Case Key': string;
}

function mapToExportRows(complaints: Complaint[]): ExportRow[] {
  return complaints.map((c) => ({
    'Date (ET)': toEasternTime(c.first_seen_utc),
    'Initiated By': c.initiator_email || '',
    'Part Number': c.part_number || '',
    'Category': c.category || '',
    'Summary': c.summary || '',
    'Subject': c.subject || '',
    'Thread URL': c.thread_url || '',
    'From Email': c.from_email || '',
    'Case Key': c.case_key || '',
  }));
}

export function exportToExcel(complaints: Complaint[], filename?: string): void {
  const rows = mapToExportRows(complaints);
  const ws = XLSX.utils.json_to_sheet(rows);

  // Set column widths
  ws['!cols'] = [
    { wch: 22 }, // Date
    { wch: 30 }, // Initiated By
    { wch: 16 }, // Part Number
    { wch: 20 }, // Category
    { wch: 60 }, // Summary
    { wch: 40 }, // Subject
    { wch: 50 }, // Thread URL
    { wch: 30 }, // From Email
    { wch: 16 }, // Case Key
  ];

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Complaints');

  const name = filename || `MAC_Complaints_${new Date().toISOString().split('T')[0]}.xlsx`;
  XLSX.writeFile(wb, name);
}

export function exportToCsv(complaints: Complaint[], filename?: string): void {
  const rows = mapToExportRows(complaints);
  const ws = XLSX.utils.json_to_sheet(rows);
  const csv = XLSX.utils.sheet_to_csv(ws);

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `MAC_Complaints_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
