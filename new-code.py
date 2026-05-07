# Added before search_edit
fb_layout.addWidget(QLabel("ASSIGNEE"))
self.assignee_filter = QComboBox()
self.assignee_filter.setMinimumWidth(160)
self.assignee_filter.setEnabled(False)
self.assignee_filter.addItem("— All —", None)
self.assignee_filter.currentIndexChanged.connect(lambda: self._filter_table(self.search_edit.text()))
fb_layout.addWidget(self.assignee_filter)


on_result=self._on_members_loaded,

# Added after new_story_btn.setEnabled(True)
self.assignee_filter.setEnabled(True)

# New method
def _on_members_loaded(self, members: list):
    self.edit_panel.set_members(members)
    self.assignee_filter.blockSignals(True)
    self.assignee_filter.clear()
    self.assignee_filter.addItem("— All —", None)
    for m in members:
        self.assignee_filter.addItem(m.get("displayName", "?"), m.get("displayName", ""))
    self.assignee_filter.blockSignals(False)

# Updated to also check assignee column
def _filter_table(self, text: str):
    text = text.lower()
    assignee_filter = self.assignee_filter.currentData()
    for row in range(self.table.rowCount()):
        text_match = any(
            text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
            for col in range(self.table.columnCount())
        ) if text else True
        assignee_item = self.table.item(row, 2)
        assignee_match = (
            assignee_filter is None or
            (assignee_item and assignee_filter.lower() in assignee_item.text().lower())
        )
        self.table.setRowHidden(row, not (text_match and assignee_match))

def _do_save(self, key, fields, comment, transition_id, target_sprint):
    try:
        self._client.update_issue(key, fields)
    except RuntimeError as e:
        if "customfield_10016" in str(e):
            # Story points field not on screen — retry without it
            fields_no_pts = {k: v for k, v in fields.items() if k != "customfield_10016"}
            self._client.update_issue(key, fields_no_pts)
        else:
            raise
    if transition_id:
        self._client.transition_issue(key, transition_id)
    if target_sprint is not None:
        self._client.move_to_sprint(key, target_sprint)
    if comment:
        self._client.add_comment(key, comment)
    return True
