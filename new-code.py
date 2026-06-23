Here's the complete code for everything that was changed, and the exact steps it follows at runtime.

---

## 1. Kanban filter bar — `KanbanBoardWidget.__init__` (lines 4248–4291)

```python
# ── Filter bar ────────────────────────────────────────────────────────
filter_bar = QFrame()
filter_bar.setStyleSheet(
    f"QFrame {{ background: transparent; border-bottom: 1px solid {BORDER}; "
    f"padding-bottom: 4px; }}"
)
fb = QHBoxLayout(filter_bar)
fb.setContentsMargins(0, 0, 0, 6)
fb.setSpacing(8)

self._filter_edit = QLineEdit()
self._filter_edit.setPlaceholderText("🔍  Filter cards by summary or key…")
self._filter_edit.setMaximumWidth(260)
self._filter_edit.textChanged.connect(self._apply_filters)
fb.addWidget(self._filter_edit)

fb.addWidget(QLabel("Assignee:"))
self._assignee_combo = QComboBox()
self._assignee_combo.setMinimumWidth(140)
self._assignee_combo.addItem("All", None)
self._assignee_combo.currentIndexChanged.connect(self._apply_filters)
fb.addWidget(self._assignee_combo)

fb.addWidget(QLabel("Priority:"))
self._priority_combo = QComboBox()
self._priority_combo.setMinimumWidth(110)
self._priority_combo.addItem("All", None)
for p in ["Highest", "High", "Medium", "Low", "Lowest"]:
    self._priority_combo.addItem(p, p)
self._priority_combo.currentIndexChanged.connect(self._apply_filters)
fb.addWidget(self._priority_combo)

self._clear_btn = QPushButton("✕  Clear")
self._clear_btn.setObjectName("toolbar_btn")
self._clear_btn.setFixedHeight(26)
self._clear_btn.clicked.connect(self._clear_filters)
fb.addWidget(self._clear_btn)
fb.addStretch()

self._filter_count_lbl = QLabel("")
self._filter_count_lbl.setObjectName("dim")
fb.addWidget(self._filter_count_lbl)

layout.addWidget(filter_bar)
```

**Steps:** Three controls are connected to `_apply_filters`. All three fire immediately on any change — no button press needed.

---

## 2. Filter logic — `_rebuild_assignee_combo`, `_apply_filters`, `_clear_filters` (lines 4336–4399)

```python
def _rebuild_assignee_combo(self, issues: list):
    self._assignee_combo.blockSignals(True)
    current = self._assignee_combo.currentData()
    self._assignee_combo.clear()
    self._assignee_combo.addItem("All", None)
    seen = {}
    for iss in issues:
        aobj = (iss.get("fields") or {}).get("assignee") or {}
        name = aobj.get("displayName") or aobj.get("name") or ""
        uid  = aobj.get("accountId") or aobj.get("name") or ""
        if uid and uid not in seen:
            seen[uid] = name
            self._assignee_combo.addItem(name or uid, uid)
    for i in range(self._assignee_combo.count()):
        if self._assignee_combo.itemData(i) == current:
            self._assignee_combo.setCurrentIndex(i)
            break
    self._assignee_combo.blockSignals(False)

def _apply_filters(self):
    term     = self._filter_edit.text().lower().strip()
    assignee = self._assignee_combo.currentData()
    priority = self._priority_combo.currentData()

    filtered = []
    for iss in self._all_issues:
        f = iss.get("fields") or {}
        if term:
            key     = iss.get("key", "").lower()
            summary = f.get("summary", "").lower()
            if term not in key and term not in summary:
                continue
        if assignee:
            aobj = f.get("assignee") or {}
            uid  = aobj.get("accountId") or aobj.get("name") or ""
            if uid != assignee:
                continue
        if priority:
            pri = (f.get("priority") or {}).get("name", "")
            if pri != priority:
                continue
        filtered.append(iss)

    self._render_issues(filtered)
    total   = len(self._all_issues)
    showing = len(filtered)
    is_filtered = term or assignee or priority
    self._filter_count_lbl.setText(
        f"Showing {showing} of {total}" if is_filtered else ""
    )

def _clear_filters(self):
    self._filter_edit.blockSignals(True)
    self._assignee_combo.blockSignals(True)
    self._priority_combo.blockSignals(True)
    self._filter_edit.clear()
    self._assignee_combo.setCurrentIndex(0)
    self._priority_combo.setCurrentIndex(0)
    self._filter_edit.blockSignals(False)
    self._assignee_combo.blockSignals(False)
    self._priority_combo.blockSignals(False)
    self._render_issues(self._all_issues)
    self._filter_count_lbl.setText("")
```

**Steps:**
- `populate()` calls `_rebuild_assignee_combo` to build the assignee list from the loaded issues, then calls `_render_issues` with the full list. Signals are blocked during the rebuild so it doesn't trigger a spurious filter pass.
- `_apply_filters` walks `self._all_issues` (the full unfiltered list) and applies all three criteria in sequence. Only issues that pass all active criteria are passed to `_render_issues`. The "Showing N of M" label is shown only when at least one filter is active.
- `_clear_filters` blocks signals on all three controls, resets them, then unblocks and calls `_render_issues` once directly — avoiding three redundant filter passes.

---

## 3. Dynamic board title and tab label

**Board heading** — `set_sprint_name` (line 4314):
```python
def set_sprint_name(self, name: str):
    self._title_lbl.setText(f"◈  {name.upper()}" if name else "◈  ACTIVE SPRINT")
```

**Called in `_on_issues_loaded`** in `MainWindow`:
```python
sprint_name = self.sprint_combo.currentText()
self.kanban_widget.set_sprint_name(sprint_name)
self.kanban_widget.set_base_url(self.edit_panel._base_url)
self.backlog_widget.set_base_url(self.edit_panel._base_url)
self.tabs.setTabText(1, f"⊞  {sprint_name}" if sprint_name else "⊞  ACTIVE SPRINT")
```

**Reset in `_clear_sprint_view`**:
```python
self.tabs.setTabText(1, "⊞  ACTIVE SPRINT")
self.kanban_widget.set_sprint_name("")
```

**Steps:** Every time `Load Stories` completes, the sprint combo's current text is read and pushed to both the board heading label and the tab's text. When the view is cleared (board change, instance switch, etc.) both reset to the default "ACTIVE SPRINT" text.

---

## 4. Backlog Open in Jira — `BacklogWidget._show_context_menu` (lines 4518–4560)

```python
def set_base_url(self, url: str):
    self._base_url = url

def _show_context_menu(self, pos):
    row = self._table.rowAt(pos.y())
    if row < 0:
        return
    key_item = self._table.item(row, 0)
    if not key_item:
        return
    key = key_item.text()

    selected_rows = list({idx.row() for idx in self._table.selectedIndexes()})
    selected_keys = [
        self._table.item(r, 0).text()
        for r in selected_rows
        if self._table.item(r, 0)
    ]
    if not selected_keys:
        selected_keys = [key]

    menu = QMenu(self)
    open_action = menu.addAction("⎋  Open in Jira")
    open_action.setEnabled(bool(self._base_url) and len(selected_keys) == 1)
    menu.addSeparator()
    copy_key = menu.addAction(
        "⎘  Copy Key" if len(selected_keys) == 1
        else f"⎘  Copy {len(selected_keys)} Keys"
    )
    menu.addSeparator()
    move_action = menu.addAction(
        "⇧  Move to Sprint" if len(selected_keys) == 1
        else f"⇧  Move {len(selected_keys)} Stories to Sprint"
    )
    move_action.setEnabled(self._sprint_combo.currentData() is not None)

    chosen = menu.exec(self._table.viewport().mapToGlobal(pos))
    if chosen == open_action:
        webbrowser.open(f"{self._base_url}/browse/{key}")
    elif chosen == copy_key:
        QApplication.clipboard().setText(", ".join(selected_keys))
    elif chosen == move_action:
        sprint_id = self._sprint_combo.currentData()
        if sprint_id:
            for k in selected_keys:
                self.move_to_sprint.emit(k, sprint_id)
```

**Steps:**
- The context menu is registered with `CustomContextMenu` policy — right-clicking anywhere in the table fires `_show_context_menu`.
- The selected rows are collected first; the right-clicked row is used as the fallback if nothing is selected.
- **Open in Jira** is only enabled when exactly one story is selected and `_base_url` is set (it's fed from `edit_panel._base_url` whenever a sprint loads). Multi-select disables it since there's no sensible single URL.
- **Copy Key** adapts its label and copies a comma-separated list for multi-select.
- **Move to Sprint** adapts its label for multi-select and is disabled if no sprint is selected in the dropdown. Emits `move_to_sprint` once per key, which `MainWindow._on_backlog_move_to_sprint` handles.