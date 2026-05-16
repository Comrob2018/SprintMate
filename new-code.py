

Loose end 1: on_done lambda bug in _refresh_users_cache

The problematic line in _open_new_story:

self._refresh_users_cache(on_done=lambda members: (self._busy(False), _show_dialog(members)))


Replace with:

def _on_users_ready(members):
    self._busy(False)
    _show_dialog(members)

self._refresh_users_cache(on_done=_on_users_ready)


Loose end 2: “Open in Jira” button not disabled on clear

In _clear_sprint_view, add alongside the other edit panel resets:

self.edit_panel.open_jira_btn.setEnabled(False)


Right-click context menu on the story table

In _build_ui, after the existing table setup, add:

self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
self.table.customContextMenuRequested.connect(self._show_row_context_menu)


Add the method to MainWindow:

def _show_row_context_menu(self, pos):
    row = self.table.rowAt(pos.y())
    if row < 0:
        return
    key_item = self.table.item(row, 0)
    if not key_item:
        return
    key = key_item.text()

    menu = QMenu(self)
    open_action   = menu.addAction("⎋  Open in Jira")
    copy_key      = menu.addAction("⎘  Copy Key")
    copy_row      = menu.addAction("⎘  Copy Row")
    menu.addSeparator()
    copy_full     = menu.addAction("⎘  Copy Full Issue")

    chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
    if chosen == open_action:
        if hasattr(self.edit_panel, "_base_url") and self.edit_panel._base_url:
            import webbrowser
            webbrowser.open(f"{self.edit_panel._base_url}/browse/{key}")
    elif chosen == copy_key:
        QApplication.clipboard().setText(key)
        self._status(f"✓ Copied {key} to clipboard.")
    elif chosen == copy_row:
        self.table.selectRow(row)
        self._copy_row_short()
    elif chosen == copy_full:
        self.table.selectRow(row)
        self._copy_row_full()


Periodic token expiry check

In __init__ of MainWindow, after self._check_token_expiry():

self._expiry_timer = QTimer(self)
self._expiry_timer.setInterval(4 * 60 * 60 * 1000)  # every 4 hours
self._expiry_timer.timeout.connect(self._check_token_expiry)
self._expiry_timer.start()


Persistent “currently loaded” sprint label

In _build_ui, add a label to the count row in the left panel, after self.story_count_lbl:

self.sprint_lbl = QLabel("")
self.sprint_lbl.setObjectName("dim")
self.sprint_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
count_row.addWidget(self.sprint_lbl)


Set it in _on_issues_loaded:

project  = self.project_combo.currentText().split("—")[0].strip()
board    = self.board_combo.currentText()
sprint   = self.sprint_combo.currentText()
self.sprint_lbl.setText(f"{project}  ◈  {board}  ◈  {sprint}")


Clear it in _clear_sprint_view:

self.sprint_lbl.setText("")


That covers all five. Want a changelog entry for these before moving on?