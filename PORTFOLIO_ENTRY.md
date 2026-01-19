# MAC Quality Dashboard - Technical Portfolio Entry

## Executive Summary

**MAC Quality Dashboard** is an enterprise-grade quality management automation system that intelligently processes customer complaint emails using AI classification, automatically extracting and categorizing quality issues from Microsoft Outlook email threads into a centralized database with rich analytics.

---

## 1. Project Overview

### What It Does
The MAC Quality Dashboard automates the traditionally manual process of tracking and categorizing customer complaints by:
- **Automatically syncing emails** from Microsoft 365 mailboxes via the Graph API
- **AI-powered classification** using Google Gemini to identify and categorize complaints
- **Intelligent data extraction** of part numbers, case identifiers, and complaint summaries
- **Thread deduplication** across email conversations to prevent duplicate entries
- **Interactive analytics** with trend visualization and category breakdowns
- **Multi-platform deployment** supporting web, desktop, and standalone Windows executables

### Core Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Streamlit (Web UI), Tkinter (Desktop), Plotly/Altair (Visualization) |
| **Backend** | Python 3.11+, SQLite, Pandas, BeautifulSoup |
| **AI/ML** | Google Generative AI (Gemini 3.5 Flash) |
| **Authentication** | Microsoft MSAL (OAuth 2.0 Device Code Flow) |
| **APIs** | Microsoft Graph API, Google Generative AI API |
| **Data Export** | OpenPyXL (Excel with formatting) |

### Architecture Pattern
**Modular Monolith with Event-Driven Processing Pipeline**

```
                    ┌─────────────────────────────────────┐
                    │         User Interfaces             │
                    │  ┌─────────────┐  ┌──────────────┐  │
                    │  │ Streamlit   │  │   Tkinter    │  │
                    │  │  Web App    │  │   Desktop    │  │
                    │  └─────────────┘  └──────────────┘  │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │     Authentication Layer (MSAL)     │
                    │   OAuth 2.0 Device Code + Silent    │
                    └───────────────┬─────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                    Email Processing Pipeline                          │
│  ┌──────────┐   ┌───────────┐   ┌───────────┐   ┌─────────────────┐  │
│  │  Fetch   │──▶│   Parse   │──▶│   Gate    │──▶│  AI Classify    │  │
│  │ (Graph)  │   │  (BS4)    │   │ (Keywords)│   │  (Gemini)       │  │
│  └──────────┘   └───────────┘   └───────────┘   └─────────────────┘  │
│                                                          │            │
│  ┌──────────────────────────────────────────────────────▼─────────┐  │
│  │                    Data Extraction Layer                        │  │
│  │  • Part Number Validation (Master List)                         │  │
│  │  • Case Key Generation (Deduplication)                          │  │
│  │  • Origin Extraction (Thread Analysis)                          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │         Data Layer                  │
                    │  ┌─────────┐      ┌─────────────┐   │
                    │  │ SQLite  │      │    Excel    │   │
                    │  │   DB    │      │   Export    │   │
                    │  └─────────┘      └─────────────┘   │
                    └─────────────────────────────────────┘
```

---

## 2. Technical Highlights

### 2.1 AI-Powered Email Classification

**Implementation:** `main.py:893-941`

The system leverages Google Gemini for intelligent email classification with structured JSON output:

```python
def gemini_extract(model, subject_clean, from_email, latest_reply,
                   timeout_s=30, retries=3, backoff=1.8):
    # Exponential backoff retry pattern
    for attempt in range(1, retries + 1):
        try:
            resp = model.generate_content(prompt,
                request_options={"timeout": timeout_s})
            # Robust JSON parsing with fallback extraction
            data = json.loads(text)
        except Exception as e:
            sleep_for = backoff ** (attempt - 1)  # 1.0s, 1.8s, 3.24s
            time.sleep(sleep_for)
```

**Key Features:**
- Temperature-0 inference for deterministic classification
- JSON mode with MIME type enforcement
- Exponential backoff (1.8x multiplier) for resilience
- Multi-format response parsing with regex fallback

### 2.2 Multi-Layer Email Filtering System

**Implementation:** `main.py:97-237`

A sophisticated noise filtering pipeline ensures only genuine complaints are processed:

```
Layer 1: Sender Blocklist     → Block known newsletter/HR senders
Layer 2: Domain Blocklist     → Block marketing domains
Layer 3: Subject Phrase Gate  → Block "training", "out of office", etc.
Layer 4: Keyword Gate         → Require quality terms (NCMR, RMA, defect...)
Layer 5: Strong Signal Boost  → Prioritize NCMR, SCAR, DMR mentions
Layer 6: AI Classification    → Final is_complaint boolean determination
```

### 2.3 Sophisticated Email Thread Parsing

**Implementation:** `main.py:296-376`

Deep parsing of email conversation history to extract original complaint origin:

```python
def extract_origins_deep(full_body_plain):
    # Pattern 1: Standard "From:" + "Sent:" headers
    for line in lines:
        if "From:" in line:
            emails = _EMAIL_ANYWHERE.findall(line)
            # Look ahead for Sent: timestamp
            for j in range(i + 1, min(i + 10, len(lines))):
                if any(l2.startswith(lbl) for lbl in _SENT_LABELS):
                    # Parse international date formats

    # Pattern 2: Inline "On X wrote:" patterns
    inline = re.findall(
        r"On\s+(.+?)\s+(?:wrote|escribió):.*?([EMAIL_PATTERN])",
        full_body_plain, flags=re.I | re.M
    )
```

**Supported Formats:**
- US/International date formats (12 patterns)
- Multi-language sent labels (English, Spanish, Dutch, German)
- Quoted reply markers (7 different email clients)

### 2.4 OAuth 2.0 Device Code Flow Authentication

**Implementation:** `streamlit_app.py:626-713`, `main.py:137-158`

Enterprise-grade authentication with user-friendly device code flow:

```python
@st.dialog("Microsoft Authentication Required")
def show_auth_dialog():
    flow = app.initiate_device_flow(scopes=SCOPES)
    st.code(flow["user_code"])  # Display: ABC123456

    # Polling with timeout display
    elapsed = time.time() - st.session_state.auth_started
    remaining = max(0, 900 - elapsed)  # 15-minute timeout
```

**Features:**
- Silent token renewal for seamless re-authentication
- Session state token persistence
- Automatic token expiration handling

### 2.5 Intelligent Case Key Generation & Deduplication

**Implementation:** `main.py:378-438`

Normalized case keys enable deduplication across different email threads:

```python
CASE_ID_PATTERNS = [
    (r'\bNCMR[\s:-]*([0-9]{4}[-/][0-9]{3,6}|[0-9]{6,})', 'ncmr'),
    (r'\bSCAR[\s:-]*([0-9]{4}[-/][0-9]{3,6}|[0-9]{5,})', 'scar'),
    (r'\bPO\s*(?:#|No\.?)?\s*[:\-]?\s*([0-9]{5,})', 'po'),
    # ... 7 pattern types total
]

def canonical_case_key(domain, pn_norm, subject, text_for_ids):
    ext = extract_external_id(text_for_ids)  # Find NCMR-2024-001, etc.
    key = f"{dom}-{pn_norm}-{ext}" if ext else f"{dom}-{pn_norm}"
    return normalize_case_key(key)[:80]  # Consistent format
```

### 2.6 Atomic Excel Writes with Corruption Prevention

**Implementation:** `main.py:676-704`

File locking protection using temporary file + atomic rename:

```python
def _safe_write_excel(write_fn, target_path, retries=3, sleep_s=1.2):
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=base + "_tmp_", suffix=ext)
    for attempt in range(1, retries + 1):
        try:
            write_fn(tmp_path)
            os.replace(tmp_path, target_path)  # Atomic operation
            return target_path
        except PermissionError:
            time.sleep(sleep_s)  # Wait for Excel to release lock
    # Fallback: timestamped alternative path
    fallback_path = f"{base}_{timestamp}{ext}"
```

### 2.7 Part Number Validation with Master List

**Implementation:** `main.py:528-606`

Intelligent part number extraction with master list validation:

```python
PN_PATTERNS = [
    r'\bP\s*/?\s*N\s*[:\-]?\s*([A-Za-z0-9\-_\.\/]{5,25})',
    r'\b(Part|Item|SKU)\s*(?:No\.?)?\s*[:\-]?\s*([A-Za-z0-9\-_\.\/]{5,25})',
]

def is_valid_pn_basic(token):
    if not PN_ALLOWED.match(token): return False
    return _has_digit(token) and _has_letter(token)

# Validate against 2.6MB master list (loaded once at startup)
PN_MASTER_SET = load_master_pns(PN_MASTER_PATH)  # ~10,000+ P/Ns
```

### 2.8 Session State Management Pattern

**Implementation:** `streamlit_app.py:209-227`

Robust state management for Streamlit's stateless execution model:

```python
# Persistent state across reruns
state_keys = {
    'df': pd.DataFrame(),        # Cached data
    'sync_running': False,       # Mutex flag
    'access_token': None,        # Auth token
    'sync_report_data': None,    # Modal content
}
for key, default in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default
```

---

## 3. Key Features Built

### Email Synchronization Engine
- **Incremental sync**: Only fetches emails since last sync timestamp
- **Pagination handling**: Automatic `@odata.nextLink` traversal
- **Conversation threading**: Groups replies under single complaint record
- **Progress tracking**: Real-time logs with timestamp

### AI Classification System
- **Binary complaint detection**: `is_complaint` boolean classification
- **Multi-category assignment**: 8 predefined quality categories
- **Summary generation**: ≤45 word business-style summaries
- **Part number extraction**: Validated against master inventory

### Interactive Analytics Dashboard
- **Trend visualization**: Monthly/weekly complaint volume charts
- **Category breakdown**: Pie charts and bar graphs
- **Metrics cards**: Total, filtered, unique P/Ns, 30-day counts
- **Date range filtering**: Interactive date picker

### Multi-Platform Support
- **Web Application**: Streamlit cloud-ready deployment
- **Desktop Application**: Native Tkinter interface
- **Windows Executable**: PyInstaller single-file bundle
- **Docker/Codespaces**: Pre-configured development container

### Data Management
- **Inline editing**: Double-click cell editing with auto-save
- **Custom columns**: User-defined fields via ALTER TABLE
- **Formatted Excel export**: Hyperlinks, tables, column widths
- **Row deletion**: Right-click context menu

---

## 4. Technical Challenges Solved

### Challenge 1: Email Thread Origin Extraction
**Problem:** Identifying the original complaint sender and date from deeply nested email threads with varying quote formats.

**Solution:** Multi-pattern regex engine supporting 7+ email client quote styles and 12+ international date formats, with fallback to Graph API thread traversal.

### Challenge 2: Duplicate Complaint Detection
**Problem:** Same issue reported across multiple email threads with different conversation IDs.

**Solution:** Normalized case key generation combining sender domain + part number + external ID (NCMR/SCAR numbers), enabling cross-thread deduplication.

### Challenge 3: Excel File Locking on Windows
**Problem:** `PermissionError` when user has Excel file open during sync.

**Solution:** Atomic write pattern using temp file + `os.replace()` with retry logic and timestamped fallback path.

### Challenge 4: OAuth Authentication in Web Context
**Problem:** Device code flow requires background polling while maintaining UI responsiveness.

**Solution:** Streamlit dialog component with session state polling, countdown timer, and automatic token refresh.

### Challenge 5: AI Response Parsing Robustness
**Problem:** LLM occasionally returns malformed JSON or wrapped arrays.

**Solution:** Multi-layer parsing: direct JSON → regex extraction → array unwrapping → empty dict fallback.

---

## 5. Code Quality Indicators

### Design Patterns Used

| Pattern | Implementation |
|---------|---------------|
| **Strategy** | Swappable UI backends (Streamlit/Tkinter) |
| **Pipeline** | Multi-stage email processing |
| **Repository** | SQLite abstraction via dedicated functions |
| **Decorator** | `@st.dialog` for modal components |
| **Singleton** | Global MSAL app, Gemini client, PN master set |
| **Retry with Backoff** | Gemini API calls, Excel writes |

### Code Organization
```
MAC_Quality_Dashboard/
├── main.py              # Core business logic (1,175 lines)
│   ├── Configuration & Environment
│   ├── Email Processing Pipeline
│   ├── AI Integration (Gemini)
│   ├── Database Operations
│   └── Excel Export
├── streamlit_app.py     # Web UI layer (1,119 lines)
│   ├── Theme & Styling
│   ├── Session State
│   ├── Authentication Dialogs
│   └── Analytics Components
├── dashboard.py         # Desktop UI (624 lines)
├── launcher.py          # Windows EXE entry (374 lines)
└── prompts.py           # AI prompt templates (54 lines)
```

### Error Handling Approaches
- **Try-except with logging**: All external API calls wrapped
- **Graceful degradation**: AI disabled → manual entry still works
- **User feedback**: `st.error()`, `st.warning()`, `messagebox.showerror()`
- **Timeout protection**: 30s Gemini timeout, 15-min auth timeout

### Security Considerations
- **Environment variable secrets**: Never hardcoded credentials
- **Masked logging**: API keys displayed as `GEM...KEY`
- **Token expiration**: Automatic refresh, no persistent storage
- **Input validation**: Part number regex, category whitelist

---

## 6. Metrics & Scale

### Codebase Statistics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | 3,346 |
| **Python Files** | 5 |
| **Functions Defined** | 110 |
| **Database Tables** | 3 (complaints, custom_columns, settings) |
| **API Integrations** | 2 (Microsoft Graph, Google Gemini) |
| **UI Platforms** | 3 (Web, Desktop, EXE) |

### Database Schema

```sql
-- Primary complaint storage
complaints (
    conversation_id TEXT PRIMARY KEY,  -- MS Graph unique ID
    received_utc TEXT,                 -- Latest message timestamp
    from_email TEXT,                   -- Sender address
    subject TEXT,                      -- Cleaned subject line
    jo_number TEXT,                    -- Internal job order
    part_number TEXT,                  -- Validated P/N
    category TEXT,                     -- AI-assigned category
    summary TEXT,                      -- AI-generated summary
    case_key TEXT,                     -- Deduplication key
    thread_url TEXT,                   -- Outlook deep link
    first_seen_utc TEXT,               -- Original complaint date
    initiator_email TEXT               -- Original sender
)

-- Extensibility
custom_columns (column_name TEXT PRIMARY KEY, column_type TEXT)
settings (key TEXT PRIMARY KEY, value TEXT)
```

### Dependencies (15 core packages)

```
streamlit>=1.28.0       pandas>=2.0.0         plotly>=5.17.0
google-generativeai     msal>=1.24.0          requests>=2.31.0
beautifulsoup4>=4.12.0  lxml>=4.9.0           openpyxl>=3.1.0
python-dateutil>=2.8.2  python-dotenv>=1.0.0  numpy>=1.24.0
altair>=5.0.0           Pillow>=10.0.0        pyinstaller>=6.0.0
```

---

## 7. Live Demo Capabilities

### Web Dashboard Features
- Real-time email sync with progress logging
- OAuth 2.0 authentication flow
- Interactive data table with inline editing
- Filterable by category, P/N, initiator, date range
- Export to formatted Excel with hyperlinks

### Analytics Visualizations
- Line charts: Complaint trends over time
- Bar charts: Weekly activity breakdown
- Pie charts: Category distribution
- Metrics cards: KPI summary

---

## Version & Status

**Current Version:** v2.1
**Status:** Production-ready, actively maintained
**Last Updated:** January 2025
**License:** Proprietary (MAC Products)

---

*This portfolio entry demonstrates expertise in Python full-stack development, AI/ML integration, enterprise authentication, and building production-ready data processing systems.*
