# SprintMate Changelog

## [1.0.0] — 2026-05-12

Features

* **Cross-instance comment posting via file import.** Comments imported from a file are now automatically cross-posted to the other Jira instance (Sentinel ↔ ACyD) when a story with a matching summary and assignee is found. The active instance uses the issue key directly; the other instance is matched via JQL (`summary` + `assignee`) using the values provided in the import file.

* **Rich preview table for imported comments.** The import comments dialog now displays five columns — KEY, SUMMARY, ASSIGNEE, CROSS-POST TO, and COMMENT — giving a full picture of what will be posted and where before confirming. Cross-post targets are highlighted in cyan; unmatched entries show a dimmed dash.

* **Detail pane for import preview.** Clicking any row in the import preview table expands a detail panel below showing the full untruncated comment, story summary, assignee, and cross-post target. The panel is hidden when no row is selected.

* **Flexible field separators in comment import files.** The comment file parser now accepts `|`, `~`, `;`, and `-` as field separators, allowing teams to use whichever character suits their workflow.

Improvements

* **Extended comment file format.** Import files now carry three fields per entry — issue key, task summary, and assignee name — in addition to the comment text (e.g. `MDT-123 | Fix login bug | John Smith: comment here`). This allows cross-instance matching to be driven entirely by the file without requiring the story to be loaded in the current sprint view.

* **Import preview counts moved before label construction.** `matched_count` and `unmatched_count` are now calculated before the summary label is created, eliminating a `NameError` that would occur when opening the import dialog.

* **Simplified matched/unmatched counting.** Preview dialog now derives `matched_count` and `unmatched_count` directly from `len(matched)` and `len(unmatched)` rather than re-iterating over `parsed`, removing a redundant loop.

* **story_info passed into ImportCommentsDialog.** The main window now forwards the sprint table's summary and assignee data into the dialog, allowing the preview table to display story details sourced from either the file or the loaded sprint.

---

## [0.12.0] — 2026-05-12

Improvements

* **Token expiry field repositioned below PAT Token.** Moved the Token Expiry `QDateEdit` row to appear immediately after the PAT Token field in the settings form, grouping all credential-related fields together for clarity.

---

## [0.11.0] — 2026-05-12

Features

* **Token expiration date per instance.** Added a `QDateEdit` field to `SettingsDialog` for both Sentinel and ACYD instances, allowing a token expiry date to be recorded alongside each PAT. Includes a Clear button that resets the date to one year from today. Expiry values are carried through `_data`, `_set_mode`, `_save_and_accept`, and `get_settings` so they round-trip correctly when switching between instances.

* **Startup and post-save expiry warnings.** `MainWindow` now calls `_check_token_expiry` on launch and after every settings save. A warning is surfaced in the status bar if any token has already expired or is within 14 days of expiry.

---

## [0.10.0] — 2026-05-12

Features

* **Persistent settings across sessions.** Introduced `_save_settings` and `_load_settings` on `MainWindow` using `QSettings` (platform-native storage — registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). Mode, URLs, default project, default board, and token expiry dates are stored in plain text; PAT tokens are base64-encoded before writing to disk to avoid casual plaintext exposure.

* **Auto-connect on startup.** If valid credentials are found in saved settings, `MainWindow.__init__` now constructs the `JiraClient` and triggers `_load_projects` automatically, eliminating the need to re-open settings on every launch.

* **Save settings on dialog accept.** `_open_settings` now calls `_save_settings` immediately after the settings dialog is accepted, ensuring any change is persisted without requiring a separate save step.

---

## [0.9.0] — 2026-05-12

Bug Fixes

* **Assignee not carrying over to story edit panel.** `_on_story_selected` was routing transition results to `_on_members_loaded`, which called `set_members` and overwrote the assignee combo with transition data. Fixed by routing directly to `set_panel.set_transitions`.

* **Assignee selection lost when member list reloads.** `set_members` was rebuilding the assignee combo after `load_issue` had already set the selection, clearing it. Fixed by storing `_pending_assignee` in `load_issue` and reapplying it after the combo is rebuilt in `set_members`. If the assignee is not in the project member list they are inserted manually so they always appear.

* **Description update returning HTTP 400.** The description field was being sent as an ADF document object, which is only valid for Jira Cloud API v3. Jira Data Center API v2 expects a plain string. Fixed by changing `fields["description"]` to the raw text string.

* **Board not loading automatically when switching to ACYD.** `_on_project_changed` was only triggered in `_on_projects_loaded` when a default project key was configured. If no default was set the board combo stayed empty until the user manually changed the project. Fixed by always calling `_on_project_changed` after projects load.

* **New story creation failing with HTTP 400 invalid issue type.** The issue type combo in `NewStoryDialog` was storing the issue type name as its data instead of the ID. The API requires the ID. Fixed by changing `it.get("name")` to `it.get("id")` in the combo item data.

* **New story creation failing with HTTP 400 on priority and required custom fields.** Priorities were hardcoded and not valid for all projects. Three required custom fields (Activity Type, Sub-Category, Element) were missing from the create payload. Fixed by fetching valid priorities and allowed values for each custom field from the API via `createmeta` before opening the dialog.

Features

* **Token expiry warnings.** Added a Token Expiry Date field to the Settings dialog for each instance. On startup and after saving settings, `_check_token_expiry` compares the stored date against the current date and shows a warning dialog at 30, 7, and 1 day out, and a critical dialog if the token has already expired.

* **Assignee lookup by name on new story creation.** Replaced the assignee dropdown in `NewStoryDialog` with a free-text input. On save, the entered name is validated against the Jira user search API via `find_user`. If no match is found the story is not created and a warning is shown. If a match is found the story is created and the user is assigned via a follow-up `update_issue` call.

Improvements

* **Assignee list pagination.** `get_project_members` previously made a single request capped at 50 results. Replaced with a paginated loop using `startAt` and `maxResults=200` that continues fetching until a partial batch is returned, ensuring all project members are available in the assignee dropdown.

* **Equal split between story list and edit panels.** Changed `splitter.setSizes([680, 480])` to `splitter.setSizes([1, 1])` so both panels always occupy 50% of the available width regardless of window size.

* **Edit panel horizontal scrolling removed.** Set `ScrollBarAlwaysOff` on the edit panel scroll area and removed hardcoded `setMinimumWidth` calls from combo boxes inside `StoryEditPanel`. Fields now expand to fill available width using `FieldGrowthPolicy.ExpandingFieldsGrow` instead of overflowing the panel.

---

## [0.8.0] — 2026-05-12

Features

* **Default project and board per instance.** Added Default Project and Default Board fields to the settings dialog for both Sentinel and ACYD. On connect, the app auto-selects the configured project and board, triggering the full load chain without manual scrolling.

Bug Fixes

* **401 errors on connect caused by inaccessible projects.** `_on_project_changed` was firing immediately on the first project in the list before the default selection could take effect. Changed the auto-trigger condition so it only fires when a default project is configured, preventing API calls to projects the user doesn't have access to.

---

## [0.7.0] — 2026-05-12

Bug Fixes

* **Assignee dropdown showing workflow transitions instead of users.** `set_members` had no guard against receiving transitions data, which has a `to` key on each item. Added a check at the top of `set_members` to silently ignore any list that looks like transitions data.

* **Assignee showing `?` for all members.** Data Center user objects use `name` and `key` fields, not `accountId`. Updated `set_members`, `load_issue`, and `_on_save` to use a `name → key → accountId` fallback chain, and `displayName → name` for display text.

* **Assignee unassigned on save.** `_on_save` was sending `{"accountId": aid}` which Data Center rejects. Changed to `{"name": aid}` to match the DC API format.

Improvements

* **Removed assignee filter dropdown from filter bar.** The dropdown was receiving transitions data and showing incorrect values. Removed in favour of the text search box which already filters by assignee name across all columns.

---

## [0.6.0] — 2026-05-12

Features

* **Import comments from a text or markdown file.** Added a `📄 Import Comments` button that parses a file formatted as `KEY: comment text` and posts each comment to the matching story. A preview dialog shows matched vs unmatched entries before posting.

* **Cross-instance comment posting.** When importing comments, the app searches the other instance (Sentinel or ACYD) for stories with the same summary and assignee. If a match is found, the comment is posted to both instances automatically. Preview dialog shows `✓ Both instances` in cyan for cross-posted entries.

* **JQL issue search added to `JiraClient`.** Added `search_issues_jql` method for searching issues by JQL query, used for cross-instance story matching by summary and assignee.

---

## [0.5.0] — 2026-05-12

Features

* **Per-instance custom field mapping.** Added `_FIELD_MAP` class variable to `JiraClient` with story point and feature link field IDs for each instance. Sentinel uses `customfield_10106` / `customfield_10100`, ACYD uses `customfield_10006` / `customfield_10000`. All hardcoded `customfield_10016` references replaced with dynamic lookups.

* **Feature link field added to story edit panel.** Added a Feature Link text field to the Story Fields group in the edit panel. Loads and saves the correct custom field ID based on the active instance.

Bug Fixes

* **Story points field rejected on save.** `_do_save` now catches `RuntimeError` containing the story points field ID and retries the save without that field, preventing a failed save from blocking other field updates.

---

## [0.4.0] — 2026-05-12

Features

* **Sentinel and ACYD dual-instance support.** Replaced the Cloud/Data Center toggle in settings with a Sentinel/ACYD toggle. Each instance stores its own URL and PAT token independently. Switching instances saves the current fields before loading the other set. The active instance is shown in the top bar.

* **Removed Cloud-specific code paths.** Both instances are Data Center so ADF comment bodies, `accountId` assignees, and API v3 references were removed. All API calls now use Bearer PAT auth and REST API v2.

---

## [0.3.0] — 2026-05-12

Features

* **New story creation.** Added `＋ New Story` button to the filter bar. Opens a dialog with summary, issue type, priority, story points, assignee, sprint, due date, and description fields. After creation the story table refreshes automatically.

* **Status transitions.** When a story is selected, available workflow transitions are loaded from Jira and shown in a Status Transition dropdown. Applying a transition on save calls the Jira transitions endpoint separately from the field update.

* **Sprint move.** Added a Sprint dropdown to the edit panel. Selecting a different sprint and saving moves the issue to that sprint via the Agile API.

* **Due date field.** Added a calendar picker with a Clear button to the edit panel. Supports setting or removing a due date on save.

* **Priority and issue type fields.** Added Priority (Highest/High/Medium/Low/Lowest) and Issue Type dropdowns to the edit panel, populated from the project's configured types on connect.

Improvements

* **Fibonacci story points.** Replaced the free-entry spinner with a dropdown of standard Fibonacci values: 0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89.

---

## [0.2.0] — 2026-05-12

Bug Fixes

* **HTTP 404 `No project could be found with key 'search'`.** Several API methods were passing query-string paths through `_request()`, causing Jira to interpret `search` as a project key. Fixed `get_projects`, `get_project_members`, `search_users`, and `get_priorities` to build full URLs manually, bypassing the router issue.

* **`'list' object has no attribute 'get'`** on project load. The `/project` endpoint returns a plain list but the code called `.get("values", [])` on it. Added an `isinstance` check to handle both list and dict responses.

* **`'dict' object is not callable`** on connect. `_FIELD_MAP` was defined as a dict but called as a function in `__init__`. Fixed by accessing it with `.get()`.

Improvements

* **Error messages include the full URL.** All `HTTPError` handlers now include the HTTP method and URL in the error string, making it much easier to identify which API call is failing.

---

## [0.1.0] — 2026-05-12

Features

* **Initial release.** Dark-themed PyQt6 desktop app for managing Jira Data Center sprint stories. Connects via Bearer PAT token. Loads projects, boards, and sprints from the Agile API. Story table shows key, summary, assignee, story points, and status. Edit panel supports updating assignee, story points, description, and posting comments. Live text filter across all table columns.
