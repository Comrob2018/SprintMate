Looking at the code, the difference is clear:
New Story dialog calls self._client.search_users("") (full paginated user search) before opening.
Edit panel only populates assignees from get_project_members(), which is called once when the project changes and can be incomplete/restricted.
Here’s the fix — change _on_story_selected to fetch the full user list before loading the issue into the edit panel:

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
    if not issue:
        return

    self.edit_panel.load_issue(issue)
    self._spawn(
        self._client.get_issue_transitions, key,
        on_result=self.edit_panel.set_transitions,
    )
    # Use the same full user search as New Story dialog
    self._spawn(
        self._client.search_users, "",
        on_result=lambda members: self.edit_panel.set_members(
            sorted(members, key=lambda m: m.get("displayName", "").lower())
        ),
    )


And in _on_project_changed, you can replace the get_project_members spawn with search_users too, so the initial population matches:

self._spawn(
    self._client.search_users, "",
    on_result=lambda members: self.edit_panel.set_members(
        sorted(members, key=lambda m: m.get("displayName", "").lower())
    ),
    on_error=lambda e: self._status(f"⚠ Could not load assignees (access restricted)"),
)


The search_users("") call does a paginated search with username=. which returns all users, matching exactly what the New Story dialog does. The set_members method already handles updating the combo and re-selecting the current assignee via _pending_assignee, so no other changes are needed.​​​​​​​​​​​​​​​​