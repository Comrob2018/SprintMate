def set_members(self, members: list):
    # Guard: ignore if this looks like transitions data not user data
    if members and "to" in members[0]:
        return
    self._members = members
    self.assignee_combo.clear()
    self.assignee_combo.addItem("— Unassigned —", None)
    for m in members:
        # DC uses 'name' as the username key for assignee updates
        uid = m.get("name") or m.get("key") or m.get("accountId")
        display = m.get("displayName") or m.get("name") or "?"
        self.assignee_combo.addItem(display, uid)
