# After
def _on_members_loaded(self, members: list):
    # Debug: print first member to see actual field names
    if members:
        print("DEBUG member keys:", list(members[0].keys()))
        print("DEBUG first member:", members[0])
    self.edit_panel.set_members(members)