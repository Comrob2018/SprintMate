def _open_new_story(self):
    key = self.project_combo.currentData()
    if not key or not self._client:
        return

    # Always do a full paginated user search for the dialog
    # rather than using the project-scoped members list which
    # may be incomplete or restricted
    try:
        members = self._client.search_users("")
    except Exception:
        members = self.edit_panel._members  # fall back to whatever we have

    dlg = NewStoryDialog(
        project_key=key,
        members=members,
        issue_types=[{"name": self.edit_panel.issuetype_combo.itemText(i),
                      "id": self.edit_panel.issuetype_combo.itemData(i)}
                     for i in range(self.edit_panel.issuetype_combo.count())],
        sprints=self._sprints,
        parent=self,
    )
    if dlg.exec() == QDialog.DialogCode.Accepted:
        vals = dlg.get_values()
        self._busy(True)
        self._status("Creating story…")
        self._spawn(
            self._client.create_issue,
            key,
            vals["summary"],
            vals["issue_type"],
            vals["description"],
            vals["assignee_id"],
            vals["priority"],
            vals["story_points"],
            vals["sprint_id"],
            vals["due_date"],
            on_result=self._on_story_created,
        )
