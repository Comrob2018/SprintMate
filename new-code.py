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

    print(f"PENDING ASSIGNEE: {getattr(self, '_pending_assignee', 'NOT SET')}")
    print(f"COMBO ITEMS: {[self.assignee_combo.itemData(i) for i in range(self.assignee_combo.count())]}")

    if getattr(self, "_pending_assignee", None):
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == self._pending_assignee:
                self.assignee_combo.setCurrentIndex(i)
                print(f"MATCHED AT INDEX {i}")
                break
        else:
            print("NO MATCH FOUND")
