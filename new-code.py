[2.1.0] — 2026-05-12
Improvements
	•	Sprint view clears on instance/project switch. Added _clear_sprint_view() helper that resets the board, sprint, and story table plus the edit panel state. Called from _switch_instance and _on_project_changed to prevent stale data from a previous context remaining visible after navigation.
	•	Board change clears sprint and story table. _on_board_changed now clears the sprint combo and story table (with signals blocked to prevent cascading loads) before fetching new sprints.
	•	Project load always triggers board fetch. _on_projects_loaded now calls _on_project_changed unconditionally instead of only when a default_key match is found, fixing the case where the target project lands on index 0 and currentIndexChanged never fires.
Bug Fixes
	•	Instance switch no longer stalls on index-0 projects. Switching to an instance whose default project is the first list item now correctly loads boards and sprints since the trigger is explicit rather than signal-driven.
	•	Restricted project membership no longer shows error dialogs. get_project_members and get_issue_types failures (HTTP 401/400) in _on_project_changed are now caught with a custom on_error handler that writes a soft warning to the status bar instead of raising a modal, allowing boards and sprints to load normally for projects the user can view but not fully administer.​​​​​​​​​​​​​​​​