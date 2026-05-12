    self._spawn(
        self._client.get_project_members, key,
        on_result=lambda members: self.edit_panel.set_members(members),
        on_error=lambda e: self._status(f"⚠ Could not load assignees for {key} (access restricted)"),
    )
    self._spawn(
        self._client.get_issue_types, key,
        on_result=lambda types: self.edit_panel.set_issue_types(types),
        on_error=lambda e: self._status(f"⚠ Could not load issue types for {key} (access restricted)"),
    )