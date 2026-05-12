Then revert _on_project_changed back to using get_project_members, and revert _open_new_story to use self.edit_panel._members instead of calling search_users:
In _on_project_changed:

self._spawn(
    self._client.get_project_members, key,
    on_result=lambda members: self.edit_panel.set_members(
        sorted(members, key=lambda m: m.get("displayName", "").lower())
    ),
    on_error=lambda e: self._status(f"⚠ Could not load assignees (access restricted)"),
)


In _open_new_story:

members = sorted(
    self.edit_panel._members,
    key=lambda m: m.get("displayName", "").lower()
)


And remove the search_users call from _open_new_story entirely. Both will now use the same project-scoped paginated list that get_project_members already fetches.​​​​​​​​​​​​​​​​