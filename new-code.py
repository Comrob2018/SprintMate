def set_members(self, members: list):
    if members and "to" in members[0]:
        return
    self._members = members
    
    # Remember who's currently assigned before we rebuild the list
    current_aid = self.assignee_combo.currentData()
    
    self.assignee_combo.clear()
    self.assignee_combo.addItem("— Unassigned —", None)
    for m in members:
        uid = m.get("name") or m.get("key") or m.get("accountId")
        display = m.get("displayName") or m.get("name") or "?"
        self.assignee_combo.addItem(display, uid)
    
    # Reapply the selection after rebuilding
    if current_aid:
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == current_aid:
                self.assignee_combo.setCurrentIndex(i)
                break
