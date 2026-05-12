try:
    members = self._client.search_users("")
    members.sort(key=lambda m: m.get("displayName", "").lower())
except Exception:
    members = self.edit_panel._members
