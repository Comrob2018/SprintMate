def load_issue(self, issue: dict):
    self.current_key = issue["key"]
    fields = issue.get("fields", {})

    self.key_lbl.setText(self.current_key)
    self.title_lbl.setText(fields.get("summary", ""))
    status = fields.get("status", {}).get("name", "")
    self.status_badge.setText(f"◈  {status.upper()}")

    # Assignee
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

    # Issue type
    itype = fields.get("issuetype", {})
    itype_id = itype.get("id")
    self.issuetype_combo.setCurrentIndex(0)
    for i in range(self.issuetype_combo.count()):
        if self.issuetype_combo.itemData(i) == itype_id:
            self.issuetype_combo.setCurrentIndex(i)
            break

    # Priority
    priority = fields.get("priority", {})
    pname = priority.get("name") if priority else None
    self.priority_combo.setCurrentIndex(0)
    for i in range(self.priority_combo.count()):
        if self.priority_combo.itemData(i) == pname:
            self.priority_combo.setCurrentIndex(i)
            break

    # Story points
    pts = fields.get(getattr(self, "_sp_field", "customfield_10016")) or fields.get("customfield_10016") or fields.get("story_points")
    self.points_combo.setCurrentIndex(0)
    if pts is not None:
        pts_int = int(pts)
        for i in range(self.points_combo.count()):
            if self.points_combo.itemData(i) == pts_int:
                self.points_combo.setCurrentIndex(i)
                break

    fl_field = getattr(self, "_fl_field", "customfield_10100")
    fl_value = fields.get(fl_field) or ""
    if isinstance(fl_value, dict):
        fl_value = fl_value.get("url", "") or fl_value.get("id", "")
    self.feature_link_edit.setText(str(fl_value) if fl_value else "")

    # Sprint
    sprint_field = fields.get("customfield_10020") or []
    if isinstance(sprint_field, list) and sprint_field:
        current_sprint = sprint_field[-1]
        self._current_sprint_id = current_sprint.get("id")
    else:
        self._current_sprint_id = None
    self.sprint_combo.setCurrentIndex(0)

    # Due date
    duedate = fields.get("duedate")
    if duedate:
        self._due_set = True
        parts = duedate.split("-")
        self.due_date.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
        self.due_date.setStyleSheet(f"color: {TEXT_PRI};")
    else:
        self._due_set = False
        self.due_date.setDate(QDate.currentDate())
        self.due_date.setStyleSheet(f"color: {TEXT_DIM};")

    # Status transitions
    self.transition_combo.setCurrentIndex(0)

    # Description
    desc = fields.get("description") or {}
    plain = self._adf_to_text(desc) if isinstance(desc, dict) else (desc or "")
    self.desc_edit.setPlainText(plain)

    self.comment_edit.clear()
    self.save_btn.setEnabled(True)


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

    if getattr(self, "_pending_assignee", None):
        found = False
        for i in range(self.assignee_combo.count()):
            if self.assignee_combo.itemData(i) == self._pending_assignee:
                self.assignee_combo.setCurrentIndex(i)
                found = True
                break
        if not found:
            self.assignee_combo.insertItem(1, f"{self._pending_assignee} (current)", self._pending_assignee)
            self.assignee_combo.setCurrentIndex(1)
