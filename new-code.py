Here's every change in order:

---

**1. `JiraClient` — two new methods added before `get_sprints`**

```python
def get_all_sprints(self, board_id: int) -> list:
    """Fetch all sprints (active, future, closed) for a board."""
    all_sprints = []
    start = 0
    max_results = 50
    while True:
        url = (f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
               f"?maxResults={max_results}&startAt={start}")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            break
        batch = data.get("values", [])
        all_sprints.extend(batch)
        if data.get("isLast", True) or len(batch) < max_results:
            break
        start += max_results
    return all_sprints

def get_issues_for_people_report(self, assignees: list[str],
                                 date_from: str = "", date_to: str = "",
                                 sprint_id: int = 0, board_id: int = 0) -> list:
    """Fetch all issues assigned to the given users within a date range or sprint."""
    sp = self.story_point_field_id
    fields = ",".join([
        "summary", "assignee", "status", "priority", "issuetype",
        "duedate", sp, "created", "resolutiondate", "comment",
    ])
    assignee_jql = " OR ".join(f'assignee = "{a}"' for a in assignees)
    if sprint_id and board_id:
        jql = f"({assignee_jql}) AND sprint = {sprint_id}"
    elif date_from and date_to:
        jql = f'({assignee_jql}) AND updated >= "{date_from}" AND updated <= "{date_to}"'
    elif date_from:
        jql = f'({assignee_jql}) AND updated >= "{date_from}"'
    elif date_to:
        jql = f'({assignee_jql}) AND updated <= "{date_to}"'
    else:
        jql = f"({assignee_jql})"
    jql += " ORDER BY assignee ASC, updated DESC"

    all_issues = []
    start = 0
    max_results = 100
    while True:
        encoded = urllib.parse.quote(jql)
        url = (f"{self.base_url}/rest/api/{self.api_version}/search"
               f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}")
        batch = data.get("issues", [])
        all_issues.extend(batch)
        if len(batch) < max_results:
            break
        start += max_results
    return all_issues
```

---

**2. `SprintReportDialog.__init__` — refactored from single view to `QTabWidget`**

The constructor now accepts two new parameters (`client`, `board_id`) and builds a `QTabWidget` with two tabs instead of the flat layout. The sprint report content moves into Tab 1 unchanged. Tab 2 is the new People Report.

```python
def __init__(self, issues: list, sprint_label: str, sp_field: str,
             fl_field: str, base_url: str, adf_to_text_fn,
             client=None, board_id: int = 0, parent=None):
    ...
    self._client      = client
    self._board_id    = board_id
    self._people_html = ""

    self._tabs = QTabWidget()
    layout.addWidget(self._tabs, 1)

    # Tab 1 — Sprint Report (existing content, moved into tab)
    sprint_tab = QWidget()
    ...
    self._tabs.addTab(sprint_tab, "📊  Sprint Report")

    # Tab 2 — People Report (new)
    people_tab = QWidget()
    ...
    self._tabs.addTab(people_tab, "👤  People Report")

    self._build_report()
    self._load_sprints_for_people_tab()
```

---

**3. `SprintReportDialog` — People Report tab UI (inside `__init__`)**

```python
# Scope group — sprint or date range
self._scope_sprint_rb = QRadioButton("Sprint")
self._scope_date_rb   = QRadioButton("Date Range")
self._sprint_scope_combo = QComboBox()   # populated from get_all_sprints
self._date_from = QLineEdit()            # YYYY-MM-DD
self._date_to   = QLineEdit()

# Radio toggle enables/disables the relevant controls
def _on_scope_toggle():
    use_sprint = self._scope_sprint_rb.isChecked()
    self._sprint_scope_combo.setEnabled(use_sprint and ...)
    self._date_from.setEnabled(not use_sprint)
    self._date_to.setEnabled(not use_sprint)

# People group — checklist from current sprint + free-text extras
self._people_list = QListWidget()        # multi-select, pre-filled from sprint assignees
self._extra_people = QLineEdit()         # comma-separated usernames

# Generate button + status label
self._gen_btn = QPushButton("▶  Generate People Report")
self._gen_btn.clicked.connect(self._generate_people_report)
self._people_status = QLabel("")

# Output browser + Save as HTML (disabled until first generate)
self._people_browser = QTextBrowser()
self._save_people_btn = QPushButton("⬇  Save as HTML")
self._save_people_btn.setEnabled(False)
self._save_people_btn.clicked.connect(self._save_people_html)
```

---

**4. `SprintReportDialog._load_sprints_for_people_tab` — new method**

Fetches all sprints in the background on dialog open and populates `_sprint_scope_combo`.

```python
def _load_sprints_for_people_tab(self):
    if not self._client or not self._board_id:
        self._sprint_scope_combo.addItem("No board available")
        return
    worker = _Worker(lambda: self._client.get_all_sprints(self._board_id))
    worker.result.connect(self._on_sprints_loaded)
    worker.error.connect(lambda e: self._sprint_scope_combo.addItem("Failed to load"))
    worker.start()
    self._sprint_worker = worker

def _on_sprints_loaded(self, sprints):
    self._sprint_scope_combo.clear()
    for s in reversed(sprints):   # most recent first
        label = f"{s.get('name', '')}  [{s.get('state', '')}]"
        self._sprint_scope_combo.addItem(label, userData=s.get("id"))
    self._sprint_scope_combo.setEnabled(self._scope_sprint_rb.isChecked())
```

---

**5. `SprintReportDialog._generate_people_report` — new method**

Collects selected people and scope, fetches issues in a `_Worker` thread, calls `_build_people_report` on result.

```python
def _generate_people_report(self):
    # Collect assignees from list selection + free-text box
    selected = [item.data(Qt.ItemDataRole.UserRole)
                for item in self._people_list.selectedItems()]
    extras   = [n.strip() for n in self._extra_people.text().split(",") if n.strip()]
    assignees = list(dict.fromkeys(selected + extras))

    # Determine sprint ID or date range
    if self._scope_sprint_rb.isChecked():
        sprint_id  = self._sprint_scope_combo.currentData() or 0
        date_from = date_to = ""
    else:
        sprint_id = 0
        date_from = self._date_from.text().strip()
        date_to   = self._date_to.text().strip()

    # Fetch in background, render on result
    worker = _Worker(lambda: self._client.get_issues_for_people_report(
        assignees=assignees, date_from=date_from, date_to=date_to,
        sprint_id=sprint_id, board_id=self._board_id,
    ))
    worker.result.connect(lambda issues: self._build_people_report(
        issues, assignees, scope_label))
    worker.error.connect(_on_err)
    worker.start()
```

---

**6. `SprintReportDialog._build_people_report` — new method**

Groups fetched issues by assignee, computes stats, and renders HTML with a summary table followed by per-person detail sections.

```python
def _build_people_report(self, issues, assignees, scope_label):
    # Group by assignee — track total, done, pts, done_pts, by_status, cycle_times
    by_assignee = {a: {"total":0,"done":0,"pts":0,"done_pts":0,
                        "by_status":{},"cycle_times":[],"issues":[]} for a in assignees}
    for iss in issues:
        # ... aggregate stats per person

    # Summary table — one row per person:
    # Person | Stories | Done | Story Progress | Total Pts | Done Pts | Points Progress
    # | Avg Cycle (days) | By Status

    # Per-person detail sections — full issue table:
    # Key | Summary | Status | Pts | Due | Resolved | Type | Priority
```

---

**7. `SprintReportDialog._save_people_html` — new method**

```python
def _save_people_html(self):
    path, _ = QFileDialog.getSaveFileName(
        self, "Save People Report", f"people-report-{date.today()}.html", ...)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(self._people_html)
```

---

**8. `MainWindow._open_sprint_report` — updated to pass `client` and `board_id`**

```python
def _open_sprint_report(self):
    board_id = self.board_combo.currentData() or 0
    dlg = SprintReportDialog(
        ...
        client=self._client,
        board_id=board_id,
        parent=self,
    )
    dlg.exec()
```

---

**Summary of steps:**

1. Added `get_all_sprints` to `JiraClient`
2. Added `get_issues_for_people_report` to `JiraClient`
3. Refactored `SprintReportDialog.__init__` to use `QTabWidget`, moved existing sprint report into Tab 1
4. Built People Report tab UI in Tab 2 (scope group, people group, generate button, browser, save button)
5. Added `_load_sprints_for_people_tab` and `_on_sprints_loaded`
6. Added `_generate_people_report`
7. Added `_build_people_report`
8. Added `_save_people_html`
9. Updated `MainWindow._open_sprint_report` to pass `client` and `board_id`