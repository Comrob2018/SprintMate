def load_issue(self, issue: dict):
        self.current_key = issue["key"]
        fields = issue.get("fields", {})
        print(f"ASSIGNEE FIELD: {assignee}\nMembers Sample: {self._members[:2] if self._members else 'EMPTY'}")

        self.key_lbl.setText(self.current_key)
        self.title_lbl.setText(fields.get("summary", ""))
        status = fields.get("status", {}).get("name", "")
        self.status_badge.setText(f"◈  {status.upper()}")

        # Store the assignee ID so set_members can reapply it
        assignee = fields.get("assignee")
        if assignee:
            self._pending_assignee = (
                assignee.get("name") or assignee.get("key") or assignee.get("accountId")
            )
        else:
            self._pending_assignee = None

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


        # Sprint — find current sprint from customfield_10020
        sprint_field = fields.get("customfield_10020") or []
        if isinstance(sprint_field, list) and sprint_field:
            current_sprint = sprint_field[-1]
            self._current_sprint_id = current_sprint.get("id")
        else:
            self._current_sprint_id = None
        self.sprint_combo.setCurrentIndex(0)  # default to "Keep current"

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

        # Status transitions — reset; caller will populate via set_transitions
        self.transition_combo.setCurrentIndex(0)

        # Description
        desc = fields.get("description") or {}
        plain = self._adf_to_text(desc) if isinstance(desc, dict) else (desc or "")
        self.desc_edit.setPlainText(plain)

        self.comment_edit.clear()
        self.save_btn.setEnabled(True)
