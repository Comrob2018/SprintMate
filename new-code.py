def _on_story_selected(self):
    rows = self.table.selectedItems()
    if not rows:
        return
    row = self.table.currentRow()
    key_item = self.table.item(row, 0)
    if not key_item:
        return
    key = key_item.text()
    issue = next((i for i in self._issues if i["key"] == key), None)
    if issue:
        self.edit_panel.load_issue(issue)
        self._spawn(
            self._client.get_issue_transitions, key,
            on_result=self.edit_panel.set_transitions,  # ← Fix: route directly
        )
