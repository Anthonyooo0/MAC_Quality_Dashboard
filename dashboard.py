# dashboard_enhanced.py - Full Excel-like editing with two-way sync
import os
import threading
import traceback
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import sqlite3
from PIL import Image, ImageTk


from main import BASE_DIR, process, fetch_all_rows, EXCEL_PATH, DB_PATH, to_et_naive, init_db

# Style config
PRIMARY_COLOR = "#1E3A8A"
SECONDARY_COLOR = "#EEF2FF"
BACKGROUND_COLOR = "#F7F7F7"
TEXT_COLOR = "#0F172A"
BUTTON_COLOR = "#1E40AF"
BUTTON_HOVER = "#1B3A96"
CARD_BG = "#FFFFFF"
HEADER_BG = "#1E3A8A"
HEADER_TEXT = "#FFFFFF"


class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.default_bg = kw.get("bg", BUTTON_COLOR)
        self.hover_bg = BUTTON_HOVER
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(bg=self.hover_bg)

    def on_leave(self, e):
        self.configure(bg=self.default_bg)


class EditableComplaintDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("MAC Complaint Dashboard - Enhanced Editor")
        self.geometry("1400x800")
        self.configure(bg=BACKGROUND_COLOR)
        
        # Track custom columns
        self.custom_columns = self._load_custom_columns()
        self.sort_column = None
        self.sort_reverse = False
        
        # Build UI
        self._build_header()
        self._build_controls_section()
        self._build_filter_bar()
        self._build_table()
        self._build_status_bar()
        
        self.refresh_table()

    def _load_custom_columns(self):
        """Load custom column definitions from database"""
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS custom_columns (
                    column_name TEXT PRIMARY KEY,
                    column_type TEXT DEFAULT 'TEXT'
                )
            """)
            cur.execute("SELECT column_name FROM custom_columns")
            cols = [row[0] for row in cur.fetchall()]
            con.close()
            return cols
        except Exception:
            return []

    def _save_custom_column(self, col_name):
        """Save new custom column to database"""
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO custom_columns (column_name) VALUES (?)", (col_name,))
            
            # Add column to complaints table if it doesn't exist
            cur.execute(f"PRAGMA table_info(complaints)")
            existing = [row[1] for row in cur.fetchall()]
            if col_name not in existing:
                cur.execute(f"ALTER TABLE complaints ADD COLUMN [{col_name}] TEXT")
            
            con.commit()
            con.close()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add column: {e}")
            return False

    def _delete_custom_column(self, col_name):
        """Remove custom column from tracking (SQLite doesn't support DROP COLUMN easily)"""
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("DELETE FROM custom_columns WHERE column_name=?", (col_name,))
            con.commit()
            con.close()
            if col_name in self.custom_columns:
                self.custom_columns.remove(col_name)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete column: {e}")
            return False

    def _build_header(self):
        header = tk.Frame(self, bg=HEADER_BG, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)  # Maintain fixed height
        
        # Container for logo and title
        content_frame = tk.Frame(header, bg=HEADER_BG)
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Left side: Logo
        logo_frame = tk.Frame(content_frame, bg=HEADER_BG)
        logo_frame.pack(side="left", padx=(20, 10))
        
        # Try to load logo image
        logo_path = os.path.join(BASE_DIR, "mac_logo.png")  # Place mac_logo.png in same folder as dashboard.py
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open(logo_path)
            
            # Resize logo to fit header nicely (50px height works well for MAC logo)
            max_height = 50
            ratio = max_height / logo_img.height
            new_width = int(logo_img.width * ratio)
            logo_img = logo_img.resize((new_width, max_height), Image.Resampling.LANCZOS)
            
            self.logo_photo = ImageTk.PhotoImage(logo_img)  # Keep reference to prevent garbage collection
            logo_label = tk.Label(logo_frame, image=self.logo_photo, bg=HEADER_BG)
            logo_label.pack()
        except Exception as e:
            # Fallback if logo not found or PIL not installed
            print(f"[WARN] Could not load logo: {e}")
            logo_label = tk.Label(logo_frame, text="MAC\nPRODUCTS", bg=HEADER_BG, fg=HEADER_TEXT, 
                                font=("Segoe UI", 10, "bold"), justify="center")
            logo_label.pack()
        
        # Right side: Title
        title_frame = tk.Frame(content_frame, bg=HEADER_BG)
        title_frame.pack(side="left", expand=True, fill="both", padx=(10, 20))
        
        title = tk.Label(
            title_frame, text="Quality Automation Dashboard",
            bg=HEADER_BG, fg=HEADER_TEXT, font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        title.pack(side="left", expand=True, fill="both")
        

    def _build_controls_section(self):
        section = tk.Frame(self, bg=BACKGROUND_COLOR)
        section.pack(fill="x", pady=15, padx=15)
        
        # Left buttons
        btn_frame = tk.Frame(section, bg=BACKGROUND_COLOR)
        btn_frame.pack(side="left")
        
        HoverButton(btn_frame, text="Run Sync", bg=BUTTON_COLOR, fg="white",
                   font=("Segoe UI", 11, "bold"), padx=20, pady=8,
                   command=self.run_sync_clicked).pack(side="left", padx=5)
        
        HoverButton(btn_frame, text="Refresh", bg=BUTTON_COLOR, fg="white",
                   font=("Segoe UI", 11, "bold"), padx=20, pady=8,
                   command=self.refresh_table).pack(side="left", padx=5)
        
        HoverButton(btn_frame, text="Save to Excel", bg="#059669", fg="white",
                   font=("Segoe UI", 11, "bold"), padx=20, pady=8,
                   command=self.save_to_excel_clicked).pack(side="left", padx=5)
        
        HoverButton(btn_frame, text="Open Excel", bg=BUTTON_COLOR, fg="white",
                   font=("Segoe UI", 11, "bold"), padx=20, pady=8,
                   command=self.open_excel_clicked).pack(side="left", padx=5)
        
        # Right buttons
        edit_frame = tk.Frame(section, bg=BACKGROUND_COLOR)
        edit_frame.pack(side="right")
        
        HoverButton(edit_frame, text="Add Column", bg="#7C3AED", fg="white",
                   font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                   command=self.add_column_clicked).pack(side="left", padx=5)
        
        HoverButton(edit_frame, text="Delete Column", bg="#DC2626", fg="white",
                   font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                   command=self.delete_column_clicked).pack(side="left", padx=5)
        
        # Stats
        stats_card = tk.Frame(section, bg=CARD_BG, bd=1, relief="solid")
        stats_card.pack(side="right", padx=10)
        
        self.stats_var = tk.StringVar(value="No data yet")
        tk.Label(stats_card, textvariable=self.stats_var, bg=CARD_BG, fg=TEXT_COLOR,
                font=("Segoe UI", 10), justify="left", padx=15, pady=10).pack()

    def _build_filter_bar(self):  # <-- REPLACE THIS ENTIRE METHOD
        frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        frame.pack(fill="x", padx=15, pady=(0, 5))
        
        tk.Label(frame, text="🔍 Quick Filters:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        
        # Category filter - with all categories pre-loaded
        tk.Label(frame, text="Category:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.category_var = tk.StringVar(value="(All)")
        
        # Define all available categories
        all_categories = [
            "(All)",
            "Product",
            "Shipping",
            "Documentation/Revision",
            "Invoicing/RTV",
            "Supplier/SCAR",
            "Damage/Transit",
            "Missing Parts",
            "Other"
        ]
        
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var, width=22, state="readonly")
        self.category_combo["values"] = all_categories
        self.category_combo.pack(side="left", padx=(5, 20))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # P/N filter
        tk.Label(frame, text="P/N:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.pn_filter = tk.StringVar()
        pn_entry = tk.Entry(frame, textvariable=self.pn_filter, width=18)
        pn_entry.pack(side="left", padx=(5, 20))
        pn_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Initiator filter
        tk.Label(frame, text="Initiator:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.initiator_filter = tk.StringVar()
        init_entry = tk.Entry(frame, textvariable=self.initiator_filter, width=20)
        init_entry.pack(side="left", padx=(5, 20))
        init_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Subject filter
        tk.Label(frame, text="Subject:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.subj_filter = tk.StringVar()
        subj_entry = tk.Entry(frame, textvariable=self.subj_filter, width=25)
        subj_entry.pack(side="left", padx=(5, 10))
        subj_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Clear filters button
        HoverButton(frame, text="Clear Filters", bg="#6B7280", fg="white",
                   font=("Segoe UI", 9), padx=10, pady=4,
                   command=self.clear_filters).pack(side="left", padx=5)

    def _build_table(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Define base columns
        self.base_columns = [
            "Date (ET)", "Initiated By", "P/N", "Category", "Summary", "Subject", "Link"
        ]
        
        # Combine with custom columns
        self.all_columns = self.base_columns + self.custom_columns
        
        # Create treeview
        self.tree = ttk.Treeview(frame, columns=self.all_columns, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        for col in self.all_columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        
        # Set column widths
        widths = {
            "Date (ET)": 130, "Initiated By": 200, "P/N": 150,
            "Category": 150, "Summary": 400, "Subject": 300, "Link": 80
        }
        for col in self.all_columns:
            w = widths.get(col, 150)
            self.tree.column(col, width=w, anchor="w" if col in ["Summary", "Subject", "Initiated By"] else "center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        
        # Bindings
        self.tree.bind("<Double-1>", self.on_cell_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)  # Right-click menu

    def _build_status_bar(self):
        footer = tk.Frame(self, bg=SECONDARY_COLOR)
        footer.pack(fill="x", side="bottom")
        
        self.status = tk.StringVar(value="Ready. Double-click cells to edit.")
        tk.Label(footer, textvariable=self.status, bg=SECONDARY_COLOR, fg=TEXT_COLOR,
                anchor="w", padx=10, pady=5).pack(fill="x")

    def sort_by_column(self, col):
        """Sort table by clicking column header"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        self.apply_filters()

    def clear_filters(self):
        """Reset all filters"""
        self.category_var.set("(All)")
        self.pn_filter.set("")
        self.initiator_filter.set("")
        self.subj_filter.set("")
        self.apply_filters()

    def apply_filters(self):
        """Apply all active filters and refresh table"""
        self.refresh_table()

    def set_status(self, msg):
        self.status.set(msg)
        self.update_idletasks()

    def run_sync_clicked(self):
        self.set_status("Running sync... Please wait.")
        thread = threading.Thread(target=self._run_sync_worker, daemon=True)
        thread.start()

    def _run_sync_worker(self):
        try:
            summary = process()
            self.after(0, self.refresh_table)
            self.after(0, lambda: self.set_status("Sync complete."))
            self.after(0, lambda: self.show_summary_popup(summary))
        except Exception as e:
            print(traceback.format_exc())
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.set_status("Error during sync!"))

    def show_summary_popup(self, summary):
        msg = (
            f"Complaint sync completed.\n\n"
            f"New: {summary['new']}\n"
            f"Updated: {summary['updated']}\n"
            f"Filtered Out: {summary['filtered_out']}\n"
            f"Unchanged: {summary['unchanged']}\n"
            f"Total Checked: {summary['checked']}\n"
        )
        if summary["excel_written"]:
            msg += "\nExcel log has been updated."
        messagebox.showinfo("Sync Summary", msg)

    def save_to_excel_clicked(self):
        """Save current dashboard state to Excel"""
        try:
            from main import export_to_excel
            export_to_excel()
            self.set_status("Excel saved successfully.")
            messagebox.showinfo("Success", "Dashboard saved to Excel!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Excel: {e}")

    def open_excel_clicked(self):
        path = os.path.abspath(EXCEL_PATH)
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showinfo("Not Found", "Run a sync first to generate Excel.")

    def add_column_clicked(self):
        """Add a new custom column"""
        col_name = simpledialog.askstring("Add Column", "Enter new column name:")
        if not col_name:
            return
        
        col_name = col_name.strip()
        if col_name in self.all_columns:
            messagebox.showwarning("Duplicate", "Column already exists!")
            return
        
        if self._save_custom_column(col_name):
            self.custom_columns.append(col_name)
            self.all_columns.append(col_name)
            self.refresh_table()
            messagebox.showinfo("Success", f"Column '{col_name}' added!")

    def delete_column_clicked(self):
        """Delete a custom column"""
        if not self.custom_columns:
            messagebox.showinfo("No Columns", "No custom columns to delete.")
            return
        
        # Show selection dialog
        win = tk.Toplevel(self)
        win.title("Delete Column")
        win.geometry("300x200")
        
        tk.Label(win, text="Select column to delete:").pack(pady=10)
        
        listbox = tk.Listbox(win)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        for col in self.custom_columns:
            listbox.insert(tk.END, col)
        
        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a column.")
                return
            col_name = listbox.get(sel[0])
            if self._delete_custom_column(col_name):
                self.all_columns.remove(col_name)
                self.refresh_table()
                win.destroy()
                messagebox.showinfo("Success", f"Column '{col_name}' deleted!")
        
        tk.Button(win, text="Delete", command=delete_selected).pack(pady=10)

    def refresh_table(self):
        init_db()
        df = fetch_all_rows()
        
        # Clear old rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df.empty:
            self.stats_var.set("No complaints found.")
            return
        
        # Add ET date column
        def _to_et_wrapper(x):
            return to_et_naive(x) if pd.notna(x) and str(x).strip() else None
        
        df["__first_et"] = df["first_seen_utc"].apply(_to_et_wrapper) if "first_seen_utc" in df.columns else None
        
        # Build display DataFrame
        display = pd.DataFrame()
        display["Date (ET)"] = df["__first_et"] if "__first_et" in df else ""
        display["Initiated By"] = df.get("initiator_email", "")
        display["P/N"] = df.get("part_number", "")
        display["Category"] = df.get("category", "")
        display["Summary"] = df.get("summary", "")
        display["Subject"] = df.get("subject", "")
        display["Link"] = df.get("thread_url", "")
        
        # Add custom columns
        for col in self.custom_columns:
            display[col] = df.get(col, "")
        
        # Store conversation_id for editing
        display["_conversation_id"] = df.get("conversation_id", "")
        
        # Apply filters
        if self.category_var.get() != "(All)":
            display = display[display["Category"] == self.category_var.get()]
        
        if self.pn_filter.get().strip():
            key = self.pn_filter.get().strip().upper()
            display = display[display["P/N"].astype(str).str.upper().str.contains(key, na=False)]
        
        if self.initiator_filter.get().strip():
            key = self.initiator_filter.get().strip().lower()
            display = display[display["Initiated By"].astype(str).str.lower().str.contains(key, na=False)]
        
        if self.subj_filter.get().strip():
            key = self.subj_filter.get().strip().lower()
            display = display[display["Subject"].astype(str).str.lower().str.contains(key, na=False)]
        
        # Sort if column selected
        if self.sort_column and self.sort_column in display.columns:
            display = display.sort_values(self.sort_column, ascending=not self.sort_reverse, na_position="last")
        else:
            # Default: sort by date descending (most recent first)
            if "Date (ET)" in display.columns:
                display = display.sort_values("Date (ET)", ascending=False, na_position="last")
        
        # Update category dropdown
        if "Category" in df.columns:
            cats = ["(All)"] + sorted(df["Category"].dropna().unique().tolist())
            self.category_combo["values"] = cats
        
        # Insert rows
        for _, row in display.iterrows():
            values = [row.get(col, "") for col in self.all_columns]
            conv_id = row.get("_conversation_id", "")
            self.tree.insert("", "end", values=values, tags=(conv_id,))
        
        self.stats_var.set(f"Total: {len(df)} | Displayed: {len(display)}")
        self.set_status(f"Table refreshed. Showing {len(display)} of {len(df)} complaints.")

    def on_cell_double_click(self, event):
        """Edit cell on double-click"""
        item = self.tree.focus()
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        if not column:
            return
        
        col_index = int(column.replace("#", "")) - 1
        if col_index < 0 or col_index >= len(self.all_columns):
            return
        
        col_name = self.all_columns[col_index]
        
        # Don't edit Link column (open instead)
        if col_name == "Link":
            url = self.tree.item(item, "values")[col_index]
            if url:
                import webbrowser
                webbrowser.open(url)
            return
        
        # Get current value
        current_value = self.tree.item(item, "values")[col_index]
        
        # Show edit dialog
        new_value = simpledialog.askstring("Edit Cell", f"Edit {col_name}:", initialvalue=current_value)
        if new_value is None:  # User cancelled
            return
        
        # Update in tree
        values = list(self.tree.item(item, "values"))
        values[col_index] = new_value
        self.tree.item(item, values=values)
        
        # Update in database
        conv_id = self.tree.item(item, "tags")[0]
        self._update_cell_in_db(conv_id, col_name, new_value)
        
        self.set_status(f"Updated {col_name} for complaint {conv_id[:8]}...")

    def _update_cell_in_db(self, conversation_id, col_name, new_value):
        """Update a single cell in the database"""
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            
            # Map display names to DB columns
            col_map = {
                "Date (ET)": "first_seen_utc",
                "Initiated By": "initiator_email",
                "P/N": "part_number",
                "Category": "category",
                "Summary": "summary",
                "Subject": "subject",
                "Link": "thread_url"
            }
            
            db_col = col_map.get(col_name, col_name)
            
            cur.execute(f"UPDATE complaints SET [{db_col}]=? WHERE conversation_id=?", 
                       (new_value, conversation_id))
            con.commit()
            con.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update: {e}")

    def on_right_click(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Delete Row", command=lambda: self.delete_row(item))
        menu.add_separator()
        menu.add_command(label="Open Link", command=lambda: self.open_row_link(item))
        
        menu.post(event.x_root, event.y_root)

    def delete_row(self, item):
        """Delete a complaint row"""
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this complaint?"):
            return
        
        conv_id = self.tree.item(item, "tags")[0]
        
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("DELETE FROM complaints WHERE conversation_id=?", (conv_id,))
            con.commit()
            con.close()
            
            self.tree.delete(item)
            self.set_status(f"Deleted complaint {conv_id[:8]}...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    def open_row_link(self, item):
        """Open the thread URL for a row"""
        values = self.tree.item(item, "values")
        link_index = self.all_columns.index("Link")
        url = values[link_index]
        if url:
            import webbrowser
            webbrowser.open(url)


def main():
    EditableComplaintDashboard().mainloop()


if __name__ == "__main__":
    main()