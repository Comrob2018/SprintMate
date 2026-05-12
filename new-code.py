try:
    issue_types = self._client.get_issue_types(key)
except Exception:
    issue_types = [{"name": self.edit_panel.issuetype_combo.itemText(i),
                    "id": self.edit_panel.issuetype_combo.itemData(i)}
                   for i in range(self.edit_panel.issuetype_combo.count())]
