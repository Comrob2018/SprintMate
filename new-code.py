def _on_members_loaded(self, members: list):
    self.edit_panel.set_members(members)
    self.assignee_filter.blockSignals(True)
    self.assignee_filter.clear()
    self.assignee_filter.addItem("— All —", None)
    for m in members:
        self.assignee_filter.addItem(m.get("displayName", "?"), m.get("displayName", ""))
    self.assignee_filter.blockSignals(False)
