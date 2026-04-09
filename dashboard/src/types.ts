export interface Complaint {
  conversation_id: string;
  received_utc: string | null;
  from_email: string | null;
  subject: string | null;
  part_number: string | null;
  category: string | null;
  summary: string | null;
  case_key: string | null;
  thread_url: string | null;
  first_seen_utc: string | null;
  initiator_email: string | null;
}

export interface Filters {
  category: string;
  partNumber: string;
  initiatedBy: string;
  subject: string;
  dateStart: string;
  dateEnd: string;
}

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  key: string;
  direction: SortDirection;
}

export type TabId = 'data' | 'analytics' | 'categories';

export interface ToastMessage {
  id: number;
  message: string;
  type: 'success' | 'warning' | 'error';
}

export type ColumnKey =
  | 'first_seen_utc'
  | 'initiator_email'
  | 'part_number'
  | 'category'
  | 'summary'
  | 'subject'
  | 'thread_url';

export interface ColumnDef {
  key: ColumnKey;
  label: string;
  defaultVisible: boolean;
}
