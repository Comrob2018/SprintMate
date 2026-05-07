# Before
if projects:
    self._on_project_changed()

# After
if projects and default_key:
    self._on_project_changed()
