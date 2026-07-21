Let me go through each change systematically with the exact code and the steps to apply it to your offline codebase.

---

## 2.27.1 — Backlog Fixes

### Step 1 — Add `project_changed` signal to `BacklogWidget`

Find the `BacklogWidget` class signals (around where `load_requested` is defined) and add one line:

```python
class BacklogWidget(QWidget):
    """Shows stories not assigned to any sprint (backlog items)."""
    story_selected   = pyqtSignal(str)
    move_to_sprint   = pyqtSignal(str, int)   # (issue_key, sprint_id)
    load_requested   = pyqtSignal()            # ask MainWindow to load backlog
    project_changed  = pyqtSignal(object)      # emitted when user picks a different project
```

---

### Step 2 — Wire `_bl_project_combo` to trigger on change

In `BacklogWidget.__init__`, find where `_bl_project_combo` is created and add the connect call:

```python
self._bl_project_combo = QComboBox()
self._bl_project_combo.setMinimumWidth(160)
self._bl_project_combo.setEnabled(False)
self._bl_project_combo.currentIndexChanged.connect(self._on_bl_project_changed)
lb.addWidget(self._bl_project_combo)
```

---

### Step 3 — Add `_on_bl_project_changed` to `BacklogWidget`

Add this new method anywhere inside `BacklogWidget`, just before `sync_combos`:

```python
def _on_bl_project_changed(self, idx: int):
    """User picked a different project in the backlog load bar — clear boards and notify MainWindow."""
    if idx < 0:
        return
    # Clear board combo and disable load button until boards reload
    self._bl_board_combo.blockSignals(True)
    self._bl_board_combo.clear()
    self._bl_board_combo.setEnabled(False)
    self._bl_board_combo.blockSignals(False)
    self._bl_load_btn.setEnabled(False)
    # Emit signal so MainWindow can load boards for the selected project
    project_data = self._bl_project_combo.itemData(idx)
    self.project_changed.emit(project_data)
```

---

### Step 4 — Block signals in `sync_combos`

`sync_combos` must block signals so mirroring from the Stories tab doesn't spuriously fire `_on_bl_project_changed`. It should already block signals — verify it looks like this:

```python
def sync_combos(self, project_combo: QComboBox, board_combo: QComboBox):
    self._bl_project_combo.blockSignals(True)
    self._bl_board_combo.blockSignals(True)
    # ... populate combos ...
    self._bl_project_combo.blockSignals(False)
    self._bl_board_combo.blockSignals(False)
```

---

### Step 5 — Wire `project_changed` in `MainWindow._build_ui`

Find where `backlog_widget.load_requested` is connected and add the second line:

```python
self.backlog_widget.load_requested.connect(self._on_backlog_load_requested)
self.backlog_widget.project_changed.connect(self._on_backlog_project_changed)
```

---

### Step 6 — Add `_on_backlog_project_changed` to `MainWindow`

Add this new method near the other backlog helpers:

```python
def _on_backlog_project_changed(self, project_data):
    """User changed the project in the backlog load bar — load boards for it."""
    if not self._client or not project_data:
        return
    project_key = project_data if isinstance(project_data, str) else str(project_data)
    self._status(f"Loading boards for {project_key}…")
    self._busy(True)

    def _do():
        return self._client.get_boards(project_key)

    def _on_done(boards):
        self._busy(False)
        bl = self.backlog_widget
        bl._bl_board_combo.blockSignals(True)
        bl._bl_board_combo.clear()
        for b in boards:
            bl._bl_board_combo.addItem(b.get("name", str(b["id"])), b["id"])
        bl._bl_board_combo.setEnabled(len(boards) > 0)
        bl._bl_load_btn.setEnabled(len(boards) > 0)
        bl._bl_board_combo.blockSignals(False)
        self._status(f"✓ {len(boards)} boards loaded for {project_key}.")

    self._spawn(_do,
        on_result=_on_done,
        on_error=lambda e: (
            self._busy(False),
            self._status(f"✗ Failed to load boards: {e}"),
        ))
```

---

### Step 7 — Update `_on_backlog_load_requested`

Replace the existing method to sync by data value and pass board/project directly:

```python
def _on_backlog_load_requested(self):
    """User clicked Load Backlog from within BacklogWidget — sync selections and load."""
    kb = self.backlog_widget
    proj_key  = kb._bl_project_combo.currentData()
    board_id  = kb._bl_board_combo.currentData()

    if not board_id:
        self._status("Please select a board first.")
        return

    # Sync project back to Stories combo if it matches
    if proj_key:
        for i in range(self.project_combo.count()):
            if self.project_combo.itemData(i) == proj_key:
                self.project_combo.blockSignals(True)
                self.project_combo.setCurrentIndex(i)
                self.project_combo.blockSignals(False)
                break

    # Load backlog directly using the selected board_id
    self._load_backlog(board_id=board_id, project_key=proj_key)
```

---

### Step 8 — Update `_load_backlog`

Replace the method signature and `_do` function with the new version that excludes epics and has three JQL attempts:

```python
def _load_backlog(self, board_id=None, project_key=None):
    """Fetch issues not in any sprint for the current project."""
    project_key = project_key or self.project_combo.currentData()
    if not project_key or not self._client:
        return
    self._busy(True)
    self._status("Loading backlog…")

    def _fetch(jql: str) -> list:
        sp      = self._sp_field
        fields  = ",".join([
            "summary", "assignee", "status", "priority", "issuetype",
            "duedate", sp, "comment",
        ])
        encoded = urllib.parse.quote(jql)
        all_issues: list = []
        start = 0
        max_results = 100
        while True:
            url = (
                f"{self._client.base_url}/rest/api/{self._client.api_version}/search"
                f"?jql={encoded}&maxResults={max_results}&startAt={start}&fields={fields}"
            )
            req = urllib.request.Request(url, headers=self._client.headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            batch = data.get("issues", [])
            all_issues.extend(batch)
            if len(batch) < max_results:
                break
            start += max_results
        return all_issues

    def _do():
        # Exclude Epics and Sub-tasks — neither belongs in a sprint backlog view.
        type_filter = 'issuetype not in (Epic, Sub-task)'
        base = (
            f'project = "{project_key}" '
            f'AND statusCategory != Done '
            f'AND {type_filter}'
        )
        order = 'ORDER BY priority DESC, updated DESC'

        # Attempt 1: sprint is EMPTY (most concise, works on DC 8+)
        try:
            return _fetch(f"{base} AND sprint is EMPTY {order}")
        except Exception as e1:
            pass

        # Attempt 2: sprint not in openSprints() AND not in closedSprints()
        try:
            return _fetch(
                f"{base} AND sprint not in openSprints() "
                f"AND sprint not in closedSprints() {order}"
            )
        except Exception as e2:
            pass

        # Attempt 3: sprint not in openSprints() only
        try:
            return _fetch(
                f"{base} AND sprint not in openSprints() {order}"
            )
        except Exception as e3:
            raise RuntimeError(
                f"Could not load backlog. All JQL attempts failed.\n"
                f"Attempt 1 (sprint is EMPTY): {e1}\n"
                f"Attempt 2 (not in openSprints/closedSprints): {e2}\n"
                f"Attempt 3 (not in openSprints): {e3}"
            )

    def _on_done(issues):
        self._busy(False)
        self._status(f"✓ Loaded {len(issues)} backlog items.")
        self.backlog_widget.populate(issues, self._sp_field)

    self._spawn(
        _do,
        on_result=_on_done,
        on_error=lambda e: (
            self._busy(False),
            self._status("✗ Failed to load backlog."),
            QMessageBox.critical(self, "Backlog Load Failed", str(e)),
        ),
    )
```

---

## 2.27.0 — UX Improvements

### Step 1 — Add `_add_escape_shortcut` module-level helper

Add this near the top of the file, before any class definitions (e.g. just before `SprintReportDialog`):

```python
def _add_escape_shortcut(dialog):
    """Add Escape key to close/reject a QDialog."""
    from PyQt6.QtWidgets import QShortcut
    from PyQt6.QtGui import QKeySequence
    QShortcut(QKeySequence("Escape"), dialog).activated.connect(dialog.reject)
```

Then call it in every dialog's `__init__` right after `self.setWindowTitle(...)`:

```python
self.setWindowTitle("New Story")
_add_escape_shortcut(self)
```

Apply to: `NewStoryDialog`, `BulkCreateDialog`, `ImportCommentsDialog`, `SettingsDialog`, `ExportStoriesDialog`, `SprintManagerDialog`, `VelocityHistoryDialog`, and all inline edit dialogs (`_inline_edit_pts`, `_inline_edit_assignee`, `_inline_edit_due_date`, bulk edit dialog).

---

### Step 2 — Add `ToastNotification` class

Add this class just before `class MainWindow`:

```python
class ToastNotification(QFrame):
    """Slide-in toast notification shown in the bottom-right corner of the window."""

    def __init__(self, message: str, kind: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        bg = {
            "success": ACCENT_GREEN,
            "error":   ACCENT_ORANGE,
            "warn":    "#E3B341",
            "info":    ACCENT_BLUE,
        }.get(kind, ACCENT_BLUE)
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border-radius: 8px;
                padding: 0px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        icon = {"success": "✓", "error": "✗", "warn": "⚠", "info": "ℹ"}.get(kind, "ℹ")
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(icon_lbl)
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("color: white; font-size: 12px;")
        msg_lbl.setWordWrap(False)
        layout.addWidget(msg_lbl)
        self.adjustSize()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self._timer.start(3000)

    def show_at(self, parent_widget):
        self.setParent(parent_widget)
        pr = parent_widget.rect()
        self.adjustSize()
        x = pr.right()  - self.width()  - 16
        y = pr.bottom() - self.height() - 48
        self.move(x, y)
        self.raise_()
        self.show()
```

---

### Step 3 — Add `_toast` and update `_status` in `MainWindow`

Add `_toast` as a new method, and update the existing `_status` method:

```python
def _toast(self, message: str, kind: str = "info"):
    """Show a slide-in toast notification in the bottom-right corner."""
    t = ToastNotification(message, kind, self)
    t.show_at(self)

def _status(self, msg: str):
    self.status_bar.showMessage(msg, 6000)
    if msg.startswith("✓"):
        self._toast(msg, "success")
    elif msg.startswith("✗"):
        self._toast(msg, "error")
    elif msg.startswith("⚠"):
        self._toast(msg, "warn")
```

---

### Step 4 — Update `_on_quick_add_done` and add `_show_quick_add_undo_toast`

Replace `_on_quick_add_done`:

```python
def _on_quick_add_done(self, result):
    self._busy(False)
    self.quick_add_edit.setEnabled(True)
    key = result.get("key", "") if isinstance(result, dict) else ""
    if key:
        self._status(f"✓ Created {key}.")
        self._last_quick_add_key = key
        self._load_sprint_issues(reselect_key=key)
        self._show_quick_add_undo_toast(key)
    else:
        errors = result.get("errorMessages", []) if isinstance(result, dict) else []
        QMessageBox.critical(self, "Quick Add Failed", "\n".join(errors) or "Unknown error.")
```

Add `_show_quick_add_undo_toast` immediately after:

```python
def _show_quick_add_undo_toast(self, key: str):
    """Show a brief toast with an Undo button to archive the just-created story."""
    toast = QFrame(self)
    toast.setStyleSheet(
        f"QFrame {{ background: {PANEL_BG}; border: 1px solid {BORDER}; "
        f"border-radius: 8px; }}"
    )
    toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
    tl = QHBoxLayout(toast)
    tl.setContentsMargins(14, 8, 14, 8)
    tl.setSpacing(10)
    lbl = QLabel(f"✓ Created {key}")
    lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-weight: 600;")
    tl.addWidget(lbl)
    undo_btn = QPushButton("Undo")
    undo_btn.setObjectName("toolbar_btn")
    undo_btn.setFixedHeight(24)

    def _do_undo():
        toast.hide()
        if self._client:
            self._busy(True)
            self._status(f"Archiving {key}…")
            self._spawn(
                self._client.archive_issue, key,
                on_result=lambda _: (
                    self._busy(False),
                    self._status(f"✓ {key} archived (quick-add undone)."),
                    self._load_sprint_issues(),
                ),
                on_error=lambda e: (
                    self._busy(False),
                    self._status(f"✗ Could not undo: {e}"),
                )
            )

    undo_btn.clicked.connect(_do_undo)
    tl.addWidget(undo_btn)
    toast.adjustSize()
    pr = self.rect()
    toast.resize(toast.sizeHint())
    toast.move(pr.right() - toast.width() - 16, pr.bottom() - toast.height() - 48)
    toast.raise_()
    toast.show()
    QTimer.singleShot(5000, toast.hide)
```

Also add `self._last_quick_add_key = ""` to `MainWindow.__init__` with the other state variables.

---

### Step 5 — Add `_show_command_palette` and wire `Ctrl+K`

In `_setup_shortcuts`, add:

```python
QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(
    self._show_command_palette
)
```

Then add the full method (it's long — copy from the file at line 9533). The key structure is:

```python
def _show_command_palette(self):
    COMMANDS = [
        ("Load Stories",   self.load_btn.click,  "load sprint refresh"),
        # ... 21 more entries ...
    ]
    dlg = QDialog(self)
    dlg.setWindowTitle("Command Palette")
    _add_escape_shortcut(dlg)
    # search box + list widget + fuzzy filter + Enter/Up/Down shortcuts
    dlg.exec()
```
