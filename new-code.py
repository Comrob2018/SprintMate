The output confirms it — set_members fires first, then load_issue runs after. So _pending_assignee is never set when set_members runs.
Also notice M83906 (Briscoe) is not in the combo items list — meaning he’s not in the assignable users list returned by the API, probably because he’s not formally assigned to the project role but is assigned to the ticket anyway.
Two fixes needed:
1. In load_issue, immediately set the combo after members are loaded by calling the reapply logic directly:

assignee = fields.get("assignee")
if assignee:
    self._pending_assignee = (
        assignee.get("name") or assignee.get("key") or assignee.get("accountId")
    )
    # Try to set immediately in case members are already loaded
    for i in range(self.assignee_combo.count()):
        if self.assignee_combo.itemData(i) == self._pending_assignee:
            self.assignee_combo.setCurrentIndex(i)
            break
    else:
        # Not found — add them manually so they always appear
        display = assignee.get("displayName", self._pending_assignee)
        self.assignee_combo.insertItem(1, display, self._pending_assignee)
        self.assignee_combo.setCurrentIndex(1)
else:
    self._pending_assignee = None
    self.assignee_combo.setCurrentIndex(0)


2. In set_members, after rebuilding the list, re-add the pending assignee if they’re missing:

if getattr(self, "_pending_assignee", None):
    found = False
    for i in range(self.assignee_combo.count()):
        if self.assignee_combo.itemData(i) == self._pending_assignee:
            self.assignee_combo.setCurrentIndex(i)
            found = True
            break
    if not found:
        # Person assigned to ticket isn't in the project member list
        self.assignee_combo.insertItem(1, f"{self._pending_assignee} (current)", self._pending_assignee)
        self.assignee_combo.setCurrentIndex(1)


This handles both timing cases and the fact that Briscoe isn’t in your assignable users list.​​​​​​​​​​​​​​​​