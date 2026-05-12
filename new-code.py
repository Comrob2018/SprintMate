[2.1.1] — 2026-05-12
Bug Fixes
	•	Restricted project boards no longer raise error dialogs. get_boards was missing error handling and would raise through _request to the default modal handler. Wrapped in try/except to return an empty list on failure.
	•	Restricted project issue types no longer raise error dialogs. get_issue_types had the same issue. Wrapped in try/except to return an empty list on failure, keeping the combo at its default state without alerting the user.​​​​​​​​​​​​​​​​