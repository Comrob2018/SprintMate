set_members in StoryEditPanel:

# Before
for m in members:
    uid = m.get("name") or m.get("accountId")
    self.assignee_combo.addItem(m.get("displayName", "?"), uid)

# After
for m in members:
    uid = m.get("name") or m.get("key") or m.get("accountId")
    display = m.get("displayName") or m.get("name") or "?"
    self.assignee_combo.addItem(display, uid)


load_issue — assignee matching:

# Before
aid = assignee.get("name") or assignee.get("accountId")

# After
aid = assignee.get("name") or assignee.get("key") or assignee.get("accountId")


Removed all debug prints from get_project_members and _on_members_loaded.​​​​​​​​​​​​​​​​