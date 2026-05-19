The _undo_save method is also missing — only the _pre_save_snapshot clear in load_issue made it in. Let me check what other undo-related pieces are present:

Now I have everything I need. Three things are missing: _pre_save_snapshot in __init__, the snapshot capture in _on_save, and the _undo_save method itself. Here’s all the code:

Good. _pre_save_snapshot is only set in load_issue (line 1733) but never declared in __init__, and _on_save never captures it before emitting. Here’s all the code that needs to be added:

1. In __init__ — add the attribute declaration (after line 1444):

        self._pre_save_snapshot: dict | None = None


2. In _on_save — capture snapshot before emitting (before the self.saved.emit(...) line):

        self._pre_save_snapshot = self._snapshot_state()
        self.saved.emit(self.current_key, fields, comment, transition_id, target_sprint)


3. New _undo_save method — add it anywhere in StoryEditPanel, e.g. just before _open_in_jira:

    def _undo_save(self):
        if not self._pre_save_snapshot:
            return
        snap = self._pre_save_snapshot
        self.blockSignals(True)
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == snap.get("assignee"):
                self.assignee_combo.setCurrentIndex(i)
                break
        self.feature_link_edit.setText(snap.get("feature_link", ""))
        for i in range(self.issuetype_combo.count()):
            if self.issuetype_combo.itemData(i) == snap.get("issuetype"):
                self.issuetype_combo.setCurrentIndex(i)
                break
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == snap.get("priority"):
                self.priority_combo.setCurrentIndex(i)
                break
        for i in range(self.points_combo.count()):
            if self.points_combo.itemData(i) == snap.get("points"):
                self.points_combo.setCurrentIndex(i)
                break
        for i in range(self.sprint_combo.count()):
            if self.sprint_combo.itemData(i) == snap.get("sprint"):
                self.sprint_combo.setCurrentIndex(i)
                break
        if snap.get("due_set") and snap.get("due_date"):
            self._due_set = True
            self.due_date.setDate(QDate.fromString(snap["due_date"], "yyyy-MM-dd"))
        else:
            self._due_set = False
            self.due_date.setDate(QDate.currentDate())
        self.desc_edit.setPlainText(snap.get("desc", ""))
        self.blockSignals(False)
        self._snapshot = self._snapshot_state()
        self._pre_save_snapshot = None
        self.undo_btn.setEnabled(False)
        self.save_btn.setEnabled(False)


4. In _on_saved in MainWindow — enable the undo button after a successful save (wherever save_btn.setEnabled(False) is called post-save):

        self.edit_panel.undo_btn.setEnabled(True)
