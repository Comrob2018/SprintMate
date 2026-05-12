The cleanest approach is to add a _clear_sprint_view() helper and call it at the right moments.
Here’s what to add/change:
1. Add the helper method to MainWindow:

def _clear_sprint_view(self):
    """Reset boards, sprints, story table, and edit panel."""
    self.board_combo.blockSignals(True)
    self.board_combo.clear()
    self.board_combo.blockSignals(False)

    self.sprint_combo.blockSignals(True)
    self.sprint_combo.clear()
    self.sprint_combo.blockSignals(False)

    self.table.setRowCount(0)
    self.story_count_lbl.setText("No stories loaded")
    self._issues = []

    self.edit_panel.current_key = None
    self.edit_panel.title_lbl.setText("Select a story to edit")
    self.edit_panel.key_lbl.setText("")
    self.edit_panel.status_badge.setText("")
    self.edit_panel.save_btn.setEnabled(False)
    self.edit_panel._snapshot = {}


2. Call it in three places:
In _switch_instance, right before self._load_projects():

self._clear_sprint_view()
self._load_projects()


In _on_project_changed, at the very top of the method:

def _on_project_changed(self):
    key = self.project_combo.currentData()
    if not key or not self._client:
        return
    self._clear_sprint_view()   # ← add this
    self._busy(True)
    ...


In _on_board_changed, at the top similarly:

def _on_board_changed(self):
    bid = self.board_combo.currentData()
    if bid is None or not self._client:
        return
    self.sprint_combo.clear()   # only need to clear sprint here
    self.table.setRowCount(0)
    self.story_count_lbl.setText("No stories loaded")
    self._issues = []
    ...


Why this structure:
	•	_switch_instance and _on_project_changed need the full clear (boards + sprints + table + edit panel) since everything downstream is stale
	•	_on_board_changed only needs sprints + table cleared, since the board combo itself is still valid
	•	Blocking signals on the combos during .clear() prevents currentIndexChanged from firing mid-clear and triggering cascading loads with None data​​​​​​​​​​​​​​​​