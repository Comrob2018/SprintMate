# Change this:
for it in issue_types:
    self.type_combo.addItem(it.get("name", "?"), it.get("name"))

# To this:
for it in issue_types:
    self.type_combo.addItem(it.get("name", "?"), it.get("id"))
