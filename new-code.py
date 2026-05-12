def _on_board_changed(self):
    bid = self.board_combo.currentData()
    if bid is None or not self._client:
        return
    
    self.sprint_combo.blockSignals(True)
    self.sprint_combo.clear()
    self.sprint_combo.blockSignals(False)
    
    self.table.setRowCount(0)
    self.story_count_lbl.setText("No stories loaded")
    self._issues = []
    
    self._busy(True)
    self._status("Loading sprints…")
    self._spawn(
        self._client.get_sprints, bid,
        on_result=self._on_sprints_loaded,
    )
