Here's every change in order:

---

**1. Sprint Report tab UI in `__init__` — replaced static layout with scope controls**

```python
# ── Tab 1: Sprint Report ──────────────────────────────────────────────
sprint_tab = QWidget()
sprint_layout = QVBoxLayout(sprint_tab)
sprint_layout.setSpacing(10)
sprint_layout.setContentsMargins(0, 12, 0, 0)

# Controls row — mirrors People tab layout
sr_ctrl_row = QHBoxLayout()
sr_ctrl_row.setSpacing(12)

# -- Scope: Sprint or Date Range
sr_scope_grp = QGroupBox("SCOPE")
sr_scope_inner = QVBoxLayout(sr_scope_grp)
sr_scope_inner.setSpacing(6)

self._sr_scope_sprint_rb = QRadioButton("Sprint")
self._sr_scope_date_rb   = QRadioButton("Date Range")
self._sr_scope_sprint_rb.setChecked(True)
sr_scope_inner.addWidget(self._sr_scope_sprint_rb)
sr_scope_inner.addWidget(self._sr_scope_date_rb)

self._sr_sprint_combo = QComboBox()
self._sr_sprint_combo.setMinimumWidth(220)
self._sr_sprint_combo.addItem("Loading sprints…")
self._sr_sprint_combo.setEnabled(False)
sr_scope_inner.addWidget(self._sr_sprint_combo)

sr_date_row = QHBoxLayout()
self._sr_date_from = QLineEdit()
self._sr_date_from.setPlaceholderText("From  YYYY-MM-DD")
self._sr_date_from.setEnabled(False)
self._sr_date_to = QLineEdit()
self._sr_date_to.setPlaceholderText("To  YYYY-MM-DD")
self._sr_date_to.setEnabled(False)
sr_date_row.addWidget(self._sr_date_from)
sr_date_row.addWidget(QLabel("→"))
sr_date_row.addWidget(self._sr_date_to)
sr_scope_inner.addLayout(sr_date_row)
sr_ctrl_row.addWidget(sr_scope_grp)
sr_ctrl_row.addStretch()
sprint_layout.addLayout(sr_ctrl_row)

def _on_sr_scope_toggle():
    use_sprint = self._sr_scope_sprint_rb.isChecked()
    self._sr_sprint_combo.setEnabled(use_sprint and self._sr_sprint_combo.count() > 0)
    self._sr_date_from.setEnabled(not use_sprint)
    self._sr_date_to.setEnabled(not use_sprint)

self._sr_scope_sprint_rb.toggled.connect(_on_sr_scope_toggle)
self._sr_scope_date_rb.toggled.connect(_on_sr_scope_toggle)

# Generate button + status
sr_gen_row = QHBoxLayout()
self._sr_gen_btn = QPushButton("▶  Generate Sprint Report")
self._sr_gen_btn.setObjectName("save_btn")
self._sr_gen_btn.clicked.connect(self._generate_sprint_report)
sr_gen_row.addWidget(self._sr_gen_btn)
self._sr_status = QLabel("")
self._sr_status.setObjectName("dim")
sr_gen_row.addWidget(self._sr_status, 1)
sprint_layout.addLayout(sr_gen_row)

from PyQt6.QtWidgets import QTextBrowser
self._browser = QTextBrowser()
self._browser.setOpenExternalLinks(True)
self._browser.setStyleSheet(...)
sprint_layout.addWidget(self._browser, 1)

self._save_sprint_btn = QPushButton("⬇  Save as HTML")
self._save_sprint_btn.setEnabled(False)   # disabled until first generate
self._save_sprint_btn.clicked.connect(self._save_html)
sprint_layout.addLayout(sprint_btn_row)
self._tabs.addTab(sprint_tab, "📊  Sprint Report")
```

---

**2. End of `__init__` — removed `_build_report()`, `_load_sprints_for_people_tab()`, and `QTimer`. Replaced with single `_load_sprints_for_tabs()` call**

```python
# Before:
self._build_report()
self._load_sprints_for_people_tab()
QTimer.singleShot(50, lambda: self._browser.setHtml(self._html))

# After:
self._load_sprints_for_tabs()
```

---

**3. `_load_sprints_for_tabs` — new method replacing `_load_sprints_for_people_tab`**

Fetches all sprints once and populates both the Sprint Report combo (`_sr_sprint_combo`) and the People Report combo (`_sprint_scope_combo`) in a single background call.

```python
def _load_sprints_for_tabs(self):
    if not self._client or not self._board_id:
        for combo in (self._sr_sprint_combo, self._sprint_scope_combo):
            combo.clear()
            combo.addItem("No board available")
        return

    def _do():
        return self._client.get_all_sprints(self._board_id)

    worker = _Worker(_do)
    worker.result.connect(self._on_sprints_loaded)
    worker.error.connect(lambda e: (
        self._sr_sprint_combo.addItem("Failed to load"),
        self._sprint_scope_combo.addItem("Failed to load"),
    ))
    worker.start()
    self._sprint_worker = worker
```

---

**4. `_on_sprints_loaded` — updated to populate both combos**

Also pre-selects the current sprint in the Sprint Report combo if the label matches.

```python
def _on_sprints_loaded(self, sprints):
    for combo in (self._sr_sprint_combo, self._sprint_scope_combo):
        combo.clear()
        if not sprints:
            combo.addItem("No sprints found")
            continue
        for s in reversed(sprints):  # most recent first
            state = s.get("state", "")
            label = f"{s.get('name', '')}  [{state}]"
            combo.addItem(label, userData=s.get("id"))

    # Pre-select the current sprint in the Sprint Report combo
    for i in range(self._sr_sprint_combo.count()):
        if self._sprint_label in (self._sr_sprint_combo.itemText(i) or ""):
            self._sr_sprint_combo.setCurrentIndex(i)
            break

    self._sr_sprint_combo.setEnabled(
        self._sr_scope_sprint_rb.isChecked() and bool(sprints)
    )
    self._sprint_scope_combo.setEnabled(
        self._scope_sprint_rb.isChecked() and bool(sprints)
    )
```

---

**5. `_generate_sprint_report` — new method**

For Sprint scope: calls `get_sprint_issues(board_id, sprint_id)`. For Date Range scope: builds a JQL query with `updated >=` / `updated <=` bounds and fetches via the search API. On success calls `_build_report(issues, scope_label)`.

```python
def _generate_sprint_report(self):
    self._sr_gen_btn.setEnabled(False)
    self._sr_status.setText("Fetching issues…")
    self._browser.setHtml("<p style='color:#888;padding:20px;'>Loading…</p>")

    if self._sr_scope_sprint_rb.isChecked():
        sprint_id   = self._sr_sprint_combo.currentData() or 0
        scope_label = self._sr_sprint_combo.currentText()
        if not sprint_id:
            self._sr_gen_btn.setEnabled(True)
            self._sr_status.setText("⚠ No sprint selected.")
            return

        def _do():
            return self._client.get_sprint_issues(self._board_id, sprint_id)
    else:
        date_from   = self._sr_date_from.text().strip()
        date_to     = self._sr_date_to.text().strip()
        scope_label = f"{date_from or '…'} → {date_to or '…'}"

        def _do():
            # Build JQL for date range and fetch via search API
            jql_parts = []
            if date_from:
                jql_parts.append(f'updated >= "{date_from}"')
            if date_to:
                jql_parts.append(f'updated <= "{date_to}"')
            jql = " AND ".join(jql_parts) if jql_parts else "updated >= -90d"
            jql += " ORDER BY updated DESC"
            # ... paginated fetch via /rest/api/2/search
            return all_issues

    def _on_done(issues):
        self._sr_gen_btn.setEnabled(True)
        self._sr_status.setText(f"✓ {len(issues)} issues loaded.")
        self._save_sprint_btn.setEnabled(True)
        self._build_report(issues, scope_label)

    def _on_err(e):
        self._sr_gen_btn.setEnabled(True)
        self._sr_status.setText(f"✗ {e}")
        self._browser.setHtml(f"<p style='color:#f78166;padding:20px;'>Error: {e}</p>")

    worker = _Worker(_do)
    worker.result.connect(_on_done)
    worker.error.connect(_on_err)
    worker.start()
    self._sr_worker = worker
```

---

**6. `_build_report` — updated signature and body to use passed-in issues and scope label**

```python
# Before:
def _build_report(self):
    sp = self._sp_field
    today = date.today().strftime("%Y-%m-%d")
    # used self._issues throughout
    # used self._sprint_label in HTML title

# After:
def _build_report(self, issues: list = None, scope_label: str = ""):
    issues = issues if issues is not None else self._issues
    sp     = self._sp_field
    today  = date.today().strftime("%Y-%m-%d")
    title  = scope_label or self._sprint_label
    # uses issues variable throughout
    # uses title in HTML <title> and meta line
```

---

**7. `_save_html` — derives filename slug from current scope selection**

```python
# Before:
slug = re.sub(r"[^\w\-]", "-", self._sprint_label)[:60]

# After:
scope = self._sr_sprint_combo.currentText() if self._sr_scope_sprint_rb.isChecked() \
        else f"{self._sr_date_from.text()}-{self._sr_date_to.text()}"
slug = re.sub(r"[^\w\-]", "-", scope or self._sprint_label)[:60]
```

---

**Summary of steps in order:**

1. Replaced Sprint Report tab static UI with scope controls (radio buttons, sprint combo, date range fields, generate button, status label, disabled save button)
2. Removed `_build_report()`, `_load_sprints_for_people_tab()`, and `QTimer` from end of `__init__`
3. Added `_load_sprints_for_tabs()` — single fetch populating both sprint combos
4. Updated `_on_sprints_loaded` to populate both combos and pre-select the current sprint
5. Added `_generate_sprint_report` — handles Sprint and Date Range scopes, fetches in background
6. Updated `_build_report` signature to accept `issues` and `scope_label` parameters
7. Updated `_save_html` to derive filename slug from current scope selection