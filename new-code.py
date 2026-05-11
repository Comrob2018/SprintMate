def load_issue(self, issue: dict):
    self.current_key = issue["key"]
    fields = issue.get("fields", {})
    # ... all existing code ...

    # Store the assignee ID so set_members can reapply it
    assignee = fields.get("assignee")
    if assignee:
        self._pending_assignee = (
            assignee.get("name") or assignee.get("key") or assignee.get("accountId")
        )
    else:
        self._pending_assignee = None

def set_members(self, members: list):
    if members and "to" in members[0]:
        return
    self._members = members
    self.assignee_combo.clear()
    self.assignee_combo.addItem("— Unassigned —", None)
    for m in members:
        uid = m.get("name") or m.get("key") or m.get("accountId")
        display = m.get("displayName") or m.get("name") or "?"
        self.assignee_combo.addItem(display, uid)

    # Reapply stored assignee after rebuild
    if getattr(self, "_pending_assignee", None):
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == self._pending_assignee:
                self.assignee_combo.setCurrentIndex(i)
                break
