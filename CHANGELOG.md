# SprintMate Changelog
## [2.11.5] - 2026-05-15
### Bug Fix
* **Removed redundant get_project_members API call on project change** — superseded by the search_users call introduced in the same update.​​​​​​​​​​​​​​​​
### Improvement
* **Edit panel assignee dropdown now populates using the full paginated user search** (matching New Story dialog behavior) instead of the project-scoped member list, ensuring all assignable users are available regardless of project access restrictions.​​​​​​​​​​​​​​​​
* **Story points 13 and 21 are now highlighted** in amber with a “consider splitting” label in the edit panel dropdown, nudging teams toward smaller stories without blocking selection.

---

## [2.11.4] — 2026-05-15
### Improvement
* **Changed Instance layout in configuration setting menu** Primary instance is in the left position, and secondary is now on the right, also primary is first in the code and secondary is second. Putting everything in standard enlish reading order.​​

---

## [2.11.3] — 2026-05-15
### Bug Fixes
* **Filter Projects, Filter Boards, Default Project, and Default Board settings now work correctly.** The mode value stored in settings ("Primary" / "Secondary") is capitalised, but the settings keys are all lowercase (primary_filter_projects, secondary_default_board, etc.). Building the lookup key without lowercasing the mode produced keys like "Primary_filter_projects" which never matched anything, causing all four fields to silently fall back to empty. Fixed by calling .lower() on the mode value in _on_projects_loaded and _on_boards_loaded before using it to construct the settings key.​​​​​​​​​​​​​​​​

---

## [2.11.2] — 2026-05-15
### Bug Fixes
* **Export dialog buttons now have descriptive labels.** The export confirmation dialog previously used the generic Yes / No / Cancel buttons, making it unclear what each option would do. The buttons are now labelled All, Select, and Cancel, matching the actions they perform.​​​​​​​​​​​​​​​​

---

## [2.11.1] — 2026-05-15

### Bug Fixes

* **New Story dialog story points now match the edit panel.** The New Story dialog had a different Fibonacci list (`0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89`) from the edit panel (`0, 1, 3, 5, 8, 13, 21`). Both now use the same values, preventing a story from being created with a point value that cannot be re-selected when editing.

---

## [2.11.0] — 2026-05-15

### Features

* **Bulk story creation from CSV.** A new "＋＋ Bulk Create" button (next to New Story) lets users create multiple stories in one operation. The flow is: optionally download a pre-filled CSV template, select a CSV file, review a full preview table showing every row's resolved values and any validation warnings, then confirm to create all valid rows sequentially. The template includes columns for `summary`, `issue_type`, `priority`, `story_points`, `assignee`, `sprint`, `due_date`, and `description`. Rows with no summary are flagged invalid and skipped; rows with unrecognised assignees, sprint names, issue types, or malformed dates are created with fallback values and flagged with a warning in the preview. A results dialog after creation reports how many succeeded and lists any failures with their error messages, and the sprint view reloads automatically on completion.

---

## [2.10.2] — 2026-05-15

### Bug Fixes

* **`get_sprint_issues` paginated loop now handles errors correctly.** The method previously had no try/except, so any HTTP error or non-JSON response mid-pagination would crash the worker silently. It now raises a descriptive `RuntimeError` consistent with the rest of the client.

* **Filter highlights no longer linger after a new sprint is loaded.** `_populate_table` now clears the search field (with signals blocked) before populating, ensuring no stale cell backgrounds appear on freshly loaded rows.

* **Token expiry "Clear" button now actually clears the field.** Previously it reset the date to one year from today, making it impossible to leave the field empty. The field is now a plain text input that can be genuinely blank; Clear sets it to an empty string.

* **`_cancel_workers` now waits for threads to finish before returning.** `w.quit()` was called without `w.wait()`, meaning the thread could still be running when the caller created a new client, causing stale result callbacks to fire against the wrong data.

### Features

* **New Story dialog due date is now a plain calendar picker.** The "Set due date" toggle button has been removed; the picker is always visible and defaults to today. Every new story will have a due date set.

* **Active sprint is now visually distinct in the sprint dropdown.** The active sprint entry is rendered in bold cyan so it stands out immediately from future sprints.

* **Window close is now guarded.** A `closeEvent` override checks for in-flight background workers and unsaved edit-panel changes before allowing the window to close, prompting the user to confirm in either case.

### Improvements

* **`_test` connection in Settings now runs on a background thread.** Previously it ran on the main thread and would freeze the dialog for up to 15 seconds if the server was slow or unreachable. The button is disabled during the test and re-enabled when it completes.

* **`_sp_field` and `_fl_field` are now properly initialised attributes.** Both `MainWindow` and `StoryEditPanel` set these in `__init__` with correct defaults, eliminating all `getattr(..., "customfield_...")` fallback calls scattered across the codebase.

* **All stdlib imports moved to top level.** `re`, `csv`, `io`, `ssl`, `time`, and `QMenu` were previously imported inline inside method bodies. They are now declared at the top of the file alongside all other imports.

---

## [2.10.1] — 2026-05-15

### Improvements

* **Settings dialog now shows hint text beneath each project/board field.** Each of the four fields (Default Project, Default Board, Filter Projects, Filter Boards) has a short description clarifying what it does, making the distinction between auto-selection and dropdown filtering immediately clear without having to experiment.

* **Placeholder text in settings fields simplified.** Now that dedicated hint labels carry the explanatory text, the placeholder text in each field is reduced to a plain example value only.

---

## [2.10.0] — 2026-05-15

### Bug Fixes

* **`_do_save` no longer detects story-point errors via string-matching.** `_request` already extracts structured Jira error detail from the JSON response body; `_do_save` now reads the resulting `RuntimeError` message directly instead of re-doing its own fragile string search. The story-point fallback path continues to work correctly.

* **Non-JSON Jira responses now produce a clear, actionable error.** Previously a `json.JSONDecodeError` from `_request` surfaced to the user as a cryptic parse failure. `_request` now catches the decode failure, inspects the raw response body, and raises a `RuntimeError` explicitly noting that Jira returned non-JSON (typically an HTML login-redirect caused by session expiry or a misconfigured URL), including a short preview of the response.

* **SSL failures now show a helpful message instead of a raw exception.** `_request` catches `ssl.SSLError` and raises a `RuntimeError` explaining that certificate verification failed and advising the user to ensure their system trusts the server's CA — a common situation with corporate Jira Data Center installs that use an internal CA.

### Features

* **Filter box now highlights matching text in the story table.** When a search term is active, every cell whose text contains the term receives a subtle background tint. Clearing the filter removes all highlights. This makes it much easier to see exactly why a row matched.

* **Comment history panel now has an Expand button.** Clicking "⤢ Expand" opens a resizable dialog showing the full, untruncated text of all recent comments (up to five) for the selected issue. The button is disabled when no comments are loaded.

* **`_load_sprint_issues` now shows which instance and sprint are being queried.** The status bar message reads "Loading stories from SECONDARY — [ACTIVE] Sprint 42…" instead of the generic "Loading stories…", giving users immediate context during the progress spinner.

### Improvements

* **Unsaved-changes guard added to Load Stories.** If the edit panel's Save button is enabled when the user clicks Load Stories (or presses Ctrl+L / Refresh), a confirmation dialog is shown before discarding the in-progress edits. Previously the panel was cleared silently.

* **`_spawn` now caps concurrent background workers at 5.** Rapidly clicking Load, switching instances, or triggering other async operations could previously queue an unbounded number of threads. Workers beyond the cap are rejected with a status-bar warning rather than queuing silently.

* **`_request` retries once on transient network errors.** A single automatic retry with a one-second delay is attempted for `URLError` and `OSError` failures (timeouts, connection resets). HTTP error responses (4xx/5xx) are not retried. This makes the app meaningfully more resilient on flaky corporate VPN connections.

* **Stale inline comments removed.** Three comments that referenced superseded behaviour — `# ← Fix: route directly` on the `get_issue_transitions` call, `# New method` on `_expand_comment`, and `# Updated to also check assignee column` on `_filter_table` — have been removed to keep the codebase accurate.

---

## [2.9.1] — 2026-05-14

### Improvements

* **Dead code removed.** Eight methods with no call sites were identified and removed. `get_priorities` on `JiraClient` was replaced by `createmeta` in an earlier version and never cleaned up. The entire user management block — `get_project_roles`, `get_role_members`, `add_user_to_role`, `remove_user_from_role`, and `invite_user` — was left over from a removed feature and had no call sites in the current codebase. `get_cross_posts` on `ImportCommentsDialog` was superseded by direct `_cross_map` access in `_import_comments`. `_on_members_loaded` on `MainWindow` was a leftover from a signal routing refactor that was never wired up. No behaviour changes.

---

## [2.9.0] — 2026-05-14

### Features

* **Toggleable table columns via right-click header menu.** The story table now has nine columns — KEY, SUMMARY, ASSIGNEE, STATUS, DUE DATE, PTS, PRIORITY, TYPE, and FEATURE LINK. Right-clicking any column header shows a checklist of all seven togglable columns with checkmarks next to currently visible ones; clicking any item toggles its visibility. KEY and SUMMARY are always visible and do not appear in the menu. The default view shows KEY, SUMMARY, ASSIGNEE, STATUS, and DUE DATE. Column visibility resets to default on each new sprint load, project change, and instance switch. All nine columns are populated in `_populate_table` and all column references use named constants (`COL_KEY` through `COL_FEATURE_LNK`) defined at module level to eliminate magic number indexing. `Ctrl+C` row copy skips hidden columns so only visible data is included.

---

## [2.8.0] — 2026-05-14

### Features

* **Keyboard shortcuts.** Added window-level shortcuts for all primary actions. `Ctrl+S` triggers Save Changes only when unsaved changes are present (Save button enabled). `Ctrl+N` opens the New Story dialog. `Ctrl+L` loads stories for the selected sprint. `Ctrl+I` opens Import and `Ctrl+E` opens Export, both only when active. `Ctrl+F` focuses the search box from anywhere in the window. `Ctrl+C` copies the selected table row as a comma-separated line of the visible columns (key, summary, assignee, points, status) — scoped to the table widget so it does not interfere with normal text copying in input fields. `Ctrl+Shift+C` copies the full issue as a single CSV-ready row matching the export column order (`key, summary, assignee, status, issue_type, priority, story_points, feature_link, due_date, sprint, description, comments`), with proper CSV quoting handled via `csv.writer` so fields containing commas or newlines paste correctly.

---

## [2.7.0] — 2026-05-14

### Features

* **Copy key button on the story edit panel.** A `⎘` button now sits inline in the edit panel header next to the issue key label. Clicking it copies the current story's Jira key to the clipboard and briefly shows `✓` before resetting after 1.5 seconds. The button is disabled until a story is loaded and re-disables when the panel is cleared.

* **Sortable story table columns.** Clicking any column header in the story table now sorts by that column, with a second click toggling to descending order. Sorting is disabled during table population to prevent mid-insert row reordering, then re-enabled once all rows are set. The sort indicator resets to unsorted on each new sprint load so sort state does not carry over between sprints. Story points use a numeric data role so values sort correctly (e.g. 8 before 13) rather than lexicographically.

---

## [2.6.0] — 2026-05-14

### Features

* **Story export to CSV.** Added an `⬇ Export` button to the filter bar (positioned between Import and the search box). Clicking it prompts the user to export all loaded stories or select specific ones. Export All writes every story in `self._issues` regardless of any active search filter. Export Selected opens a basket-style picker with a live search box (filters by key and summary as you type) — stories start empty and are added individually or in bulk, with double-click support in both directions. The save dialog pre-suggests a filename based on the active project, board, sprint, and date (e.g. `project-board-sprint-2026-05-14.csv`) with special characters replaced by hyphens. The exported CSV contains one row per story with columns: `key`, `summary`, `assignee`, `status`, `issue_type`, `priority`, `story_points`, `feature_link`, `due_date`, `sprint`, `description`, and `comments`. Comments are pipe-separated oldest to newest in `[Author]: text` format; ADF descriptions and comment bodies are flattened to plain text. A completion dialog confirms the export with the file path, or shows an error if writing failed.

---

## [2.5.0] — 2026-05-14

### Features

* **Dual-key support for comment import across all file formats.** Lines and rows can now specify two Jira keys for a single comment, causing the comment to be posted to both keys. In text/Markdown files, include both keys comma-separated at the start of the line (e.g. `PROJECT1-123,PROJECT2-456 - Summary - Assignee: Comment`). In CSV files, add an optional `key2` column (also accepted: `key_2`, `second_key`, `other_key`). Order does not matter — the parser extracts all keys first using regex, then determines which belongs to the active instance by matching against the loaded sprint stories, with the other treated as the cross-post target. When both keys are explicitly provided, the cross-instance mapping is built directly from them, bypassing JQL lookup entirely. Unpaired entries continue to use JQL summary/assignee matching as before.

---

## [2.4.0] — 2026-05-14

### Features

* **CSV files accepted for comment import.** The import comments file dialog now accepts `.csv` files in addition to `.txt` and `.md`. CSV files require a header row with columns named `key`, `summary`, `assignee`, and `comment` (case-insensitive; extra columns are ignored). `key` and `comment` are the minimum required columns — `summary` and `assignee` are optional but enable cross-instance matching when present. Excel-exported CSVs with a BOM are handled automatically via `utf-8-sig` encoding.

### Improvements

* **Comment import shows a completion popup.** After batch posting finishes, a dialog now summarises the outcome rather than updating only the status bar. Full success shows an information dialog with the posted count. Partial success shows a warning dialog listing primary and cross-post failures (capped at five per category with an overflow count). Total failure shows a critical dialog listing all failed keys. The status bar is also updated in all cases for reference after the dialog is dismissed.

* **New story creation shows a completion popup.** `_on_story_created` now shows an information dialog on success and a critical dialog on failure, mirroring the comment import completion behaviour for a consistent feel across the app. Network-level failures now also surface via a critical dialog through a previously missing `on_error` handler on the spawn call, rather than falling through to the default unhandled error modal.

---

## [2.3.0] — 2026-05-14

### Features

* **Per-instance project and board filtering.** Added "Filter Projects" and "Filter Boards" fields to the settings dialog for each instance. Accepts a comma-separated list of terms (e.g. `PROJECT1, PROJECT2`) and filters the respective combo down to entries whose key or display name contains any of the terms (case-insensitive substring match). If the filter produces zero matches, the full list is shown with a `⚠` warning in the status bar. When a filter is active, the status bar shows the filtered count alongside the total (e.g. `Loaded 42 projects, filtered to 2`). Each instance stores its own filter values independently.

### Improvements

* **Default project auto-selection uses substring matching.** Previously matched the project combo by exact key comparison (e.g. `PROJECT1` had to be entered exactly). Now uses the same case-insensitive substring logic as the other fields, matching against both the project key and display name, so entries like `project1` or `mission` correctly auto-select `PROJECT1 — Special Project 1`.

* **Default project and board selection now consistent.** Default Board already used case-insensitive substring matching; Default Project did not. Both now use the same matching strategy, and both are consistent with the new filter field behaviour.

---

## [2.2.1] — 2026-05-13

### Improvements

* **Settings dialog confirm button renamed to "Save".** The OK button in the connection settings dialog now reads "Save" to better reflect its action and stay consistent with the save-oriented language used elsewhere in the app.

---

## [2.2.0] — 2026-05-13

### Bug Fixes

* **`move_to_sprint` always suppressed HTTP errors.** The `except urllib.error.HTTPError` block guarded the re-raise with `if e.code not in (200, 201, 204)`, but `urlopen` only raises `HTTPError` for non-2xx responses, so success codes can never appear there. The condition was always true, meaning every failure was silently swallowed. The guard has been removed; any `HTTPError` caught here is now unconditionally re-raised.

* **`remove_user_from_role` always suppressed HTTP errors.** Same inverted guard pattern as above (`if e.code != 204`). Removed for the same reason — any `HTTPError` in this block is a genuine failure and is now always re-raised.

* **Comment import batch aborted on first primary post failure.** `_post_imported_comments` called `self._client.add_comment` without a `try/except`, so a single failure raised an unhandled exception and returned no result dict, leaving the progress bar stuck and cross-failures unreported. The call is now wrapped; failures are recorded in `cross_failures` and the loop continues. Cross-posting is skipped for entries whose primary post failed.

* **Story creation falsely reported success on Jira error payloads.** `_on_story_created` called `result.get("key", "")` unconditionally, so when Jira returned a 2xx error payload (`{"errorMessages": [...], "errors": {...}}`) the UI displayed "✓ Created  successfully." The result is now checked for `errorMessages` and `errors` keys before reporting success; a `QMessageBox.critical` is shown if either is present.

* **`MODE_DC` and `MODE_CLOUD` class constants were both set to `"secondary"`.** These two constants were dead scaffolding whose identical values made them indistinguishable from each other and from `MODE_SECONDARY`. Both have been removed; all instance-mode comparisons in the codebase already used `MODE_SECONDARY` and `MODE_PRIMARY`.

### Features

* **OS keychain storage for PATs via `keyring`.** Tokens are now stored in the platform-native credential store (Windows Credential Manager, macOS Keychain, Linux Secret Service) instead of base64-encoded in `QSettings`. The `keyring` package is imported with a `try/except` so the app continues to work without it, falling back to the previous base64 behaviour. On first save with `keyring` present, the token is written to the keychain and the legacy `QSettings` entry is removed, migrating existing installs automatically. Requires `pip install keyring`.

### Improvements

* **`get_sprint_issues` now paginates.** The previous implementation fetched a single page of 100 issues and returned silently, dropping any remainder. The method now uses the same `while True` / `startAt` pagination loop used by `get_project_members` and `search_users`, ensuring all issues in a sprint are loaded regardless of count.

* **Story point values are safely coerced from floats.** Jira commonly returns story points as floats (e.g. `5.0`). `load_issue` previously called `int(pts)` directly, which raises `ValueError` on a float string. The conversion is now `int(float(pts))` wrapped in a `try/except (TypeError, ValueError)`, with a graceful fallback to leaving the combo at "— Not set —".

* **Due dates parsed with `QDate.fromString` instead of manual splitting.** Both `load_issue` and `_set_mode` used `duedate.split("-")` with direct `int()` casts, which raises `IndexError` or produces an invalid `QDate` if the string is malformed (e.g. a Jira datetime with a `T`). Both sites now use `QDate.fromString(value[:10], "yyyy-MM-dd")` with an `.isValid()` check and a safe fallback.

* **`set_members` guard is now explicit.** The previous check `if members and "to" in members[0]` would silently discard any member list whose first entry happened to contain a `"to"` key. The condition is tightened to `"to" in members[0] and "displayName" not in members[0]` with a comment explaining its purpose: filtering out invite-response payloads mistakenly routed to this method.

* **Dirty-state signals blocked during `load_issue`.** All dirty-tracking widget signals (`currentIndexChanged`, `textChanged`, `dateChanged`, etc.) fired during `load_issue` while `self._snapshot` still held the previous issue's values, which could spuriously enable the Save button before the new baseline was captured. `load_issue` now calls `blockSignals(True)` on all tracked widgets, delegates population to a new `_load_issue_fields()` helper, then unblocks signals and captures the snapshot in a `finally` block.

* **`_best_match` hoisted out of the cross-instance matching loop.** The function was re-defined on every iteration of `for key, entry in parsed.items()`, allocating a new function object each time. It is now defined once above the loop.

* **JQL sanitisation covers wildcards and backslashes.** The previous implementation only escaped double-quotes in summary and assignee values before embedding them in JQL queries. The new `_sanitise_jql()` helper also escapes backslashes (which must be escaped first) and strips the JQL wildcard characters `%`, `*`, and `?`, preventing malformed or unintended queries when issue summaries contain these characters.

* **In-flight workers are cancelled on instance switch and settings change.** `_switch_instance` and `_open_settings` replaced `self._client` without stopping active workers, leaving in-flight threads that would emit `result` signals back into UI slots referencing the old client. A new `_cancel_workers()` helper disconnects `result` and `error` signals from all active workers and calls `quit()` on each before the client is replaced. It is called at the start of both methods.

* **Comment import uses `self._issues` as the source of truth for loaded keys.** `_import_comments` previously built `loaded_keys` by iterating table widget rows, so issues hidden by an active search filter were incorrectly treated as unmatched. The method now iterates `self._issues` directly, which always contains the full loaded set regardless of any active filter.

---

## [2.1.3] — 2026-05-12

### Bug Fixes
* **Both assignee lists now show all instance users including project members.** get_project_members now calls both the project-scoped user/assignable/search endpoint and the instance-wide user/search wildcard endpoint, merging and deduplicating results by username so no users are missing from either list.
* **Assignee list now sorted alphabetically in both edit panel and new story dialog.** Members are sorted by displayName before being passed to either the edit panel or NewStoryDialog.
* **New story creation no longer fails with invalid issue type error.** NewStoryDialog was storing the issue type name as the combo data instead of the id, causing create_issue to send an invalid payload. Fixed to store id as the combo data.
* **New story issue types now fetched fresh on dialog open.** _open_new_story was building the issue types list from the edit panel combo, which may be empty if get_issue_types failed due to access restrictions on project change. Now calls get_issue_types directly when the dialog opens, falling back to the combo contents only if that fails.​​​​​​​​​​​​​​​​

---

## [2.1.2] — 2026-05-12

### Bug Fixes
* **Remaining HTTP 400 errors on instance switch suppressed.** get_sprints was missing error handling and would raise through _request to the default modal handler on restricted projects. Wrapped in try/except to return an empty list on failure.
* **New story assignee list no longer limited to project members.** _open_new_story was using self.edit_panel._members which is populated by the project-scoped get_project_members call and may be empty or restricted. Now always calls search_users directly, falling back to the cached members list only if that fails.
* **New story assignee list now fully paginated.** search_users was capped at 200 results with no pagination, cutting off users whose names appear later alphabetically. Refactored to paginate in batches of 200 using startAt until the full user list is retrieved, consistent with the existing get_project_members pagination pattern.
### Improvements
* **New story assignee list sorted alphabetically.** Members returned from search_users are now sorted by displayName before being passed to NewStoryDialog, making it easier to locate assignees regardless of the order the API returns them.​​​​​​​​​​​​​​​​

---

## [2.1.1] — 2026-05-12

### Bug Fixes
* **Restricted project boards no longer raise error dialogs.** get_boards was missing error handling and would raise through _request to the default modal handler. Wrapped in try/except to return an empty list on failure.
* **Restricted project issue types no longer raise error dialogs.** get_issue_types had the same issue. Wrapped in try/except to return an empty list on failure, keeping the combo at its default state without alerting the user.

---

## [2.1.0] — 2026-05-12

### Improvements
* **Sprint view clears on instance/project switch.** Added _clear_sprint_view() helper that resets the board, sprint, and story table plus the edit panel state. Called from _switch_instance and _on_project_changed to prevent stale data from a previous context remaining visible after navigation.
* **Board change clears sprint and story table.** _on_board_changed now clears the sprint combo and story table (with signals blocked to prevent cascading loads) before fetching new sprints.
* **Project load always triggers board fetch.** _on_projects_loaded now calls _on_project_changed unconditionally instead of only when a default_key match is found, fixing the case where the target project lands on index 0 and currentIndexChanged never fires.
### Bug Fixes
* **Instance switch no longer stalls on index-0 projects.** Switching to an instance whose default project is the first list item now correctly loads boards and sprints since the trigger is explicit rather than signal-driven.
* **Restricted project membership no longer shows error dialogs.** get_project_members and get_issue_types failures (HTTP 401/400) in _on_project_changed are now caught with a custom on_error handler that writes a soft warning to the status bar instead of raising a modal, allowing boards and sprints to load normally for projects the user can view but not fully administer.​​​​​​​​​​​​​​​​

---

## [2.0.0] — 2026-05-12

### Bug Fixes

* **`create_issue` argument order causing HTTP 400 on new story creation.** The call site in `_open_new_story` passed `issuetype_id` as the third positional argument and `description` as the fourth, but the `JiraClient.create_issue` signature expected them in the opposite order, so the description string was being sent as the issue type ID. Fixed by rewriting the signature to match the call site exactly (`summary`, `issuetype_id`, `description`, `assignee_id`, `priority`, `story_points`, `sprint_id`, `due_date`). Assignee and sprint assignment are now also handled inside `create_issue` directly, eliminating the need for separate follow-up calls.

* **Default board setting overwritten with project key on every settings save.** `_save_and_accept` was reading `self.default_project_edit.text()` for both the `default_project` and `default_board` keys, so any saved board name was silently replaced with the project key on every dialog accept. Fixed by reading `self.default_board_edit.text()` for `default_board`.

### Features

* **Instance switch button in the topbar.** Added a `⇄ Switch Instance` button that toggles between Secondary and Primary without opening the settings dialog. Swaps the active `JiraClient`, updates field-map IDs on the edit panel, saves settings, checks token expiry, and triggers a full project/board/sprint reload. The button is disabled until credentials are loaded and shows a warning dialog if the target instance has no saved credentials.

* **Dirty-state tracking on the story edit panel.** The Save button is now disabled when a story is first selected and only enables when at least one field has actually changed from its loaded value. `_snapshot_state()` captures a hashable dict of all editable field values when `load_issue` runs; `_check_dirty()` is connected to every input widget and compares the current state against the snapshot. After a successful save the snapshot is reset and Save disables again, preventing accidental re-posts.

* **Comment history panel in the story edit panel.** Added a `RECENT COMMENTS` read-only section above the `ADD COMMENT` input that displays the five most recent comments on the selected story, showing author, date, and truncated body text. Populated directly from `fields["comment"]["comments"]`, which is already fetched as part of `get_sprint_issues` — no additional API calls required.

### Improvements

* **Post-save row selection preserved after sprint reload.** Previously `_on_saved` called `_load_sprint_issues()` unconditionally, which repopulated the table and cleared the selection, leaving the user at an empty edit panel after every save. `_load_sprint_issues` now accepts a `reselect_key` parameter; after `_populate_table` completes, `_on_issues_loaded` scans for that key and re-selects and scrolls to the matching row. `_on_saved` passes the saved issue key so the just-edited story is always restored.

* **Per-comment progress during batch import posting.** The progress bar now switches to bounded mode (0–N) when import posting begins and advances after each comment rather than showing a static spinner for the entire batch. `_post_imported_comments` accepts a `progress_cb(done, total)` callable and calls it after each successful post. Cross-post failures are collected per-comment and surfaced in the status bar at completion rather than silently discarded.

* **Fuzzy JQL matching for cross-instance comment cross-posting.** The cross-instance story lookup previously used `summary = "..."` (exact match), which silently failed on any casing difference, trailing whitespace, or minor punctuation mismatch. The query now uses `summary ~ "..."` (contains search) and scores all returned candidates by summary closeness and assignee match before selecting the best result. Falls back to an exact-match query only if the contains search returns no results.

* **Version badge in the status bar.** Added a permanent `◈ v2.0.0` label pinned to the right side of the status bar via `addPermanentWidget`, keeping it visible regardless of status messages. The version is defined as a single `APP_VERSION` constant at the top of the module for easy future bumps.

---

## [1.0.0] — 2026-05-12

### Features

* **Cross-instance comment posting via file import.** Comments imported from a file are now automatically cross-posted to the other Jira instance (Secondary ↔ Primary) when a story with a matching summary and assignee is found. The active instance uses the issue key directly; the other instance is matched via JQL (`summary` + `assignee`) using the values provided in the import file.

* **Rich preview table for imported comments.** The import comments dialog now displays five columns — KEY, SUMMARY, ASSIGNEE, CROSS-POST TO, and COMMENT — giving a full picture of what will be posted and where before confirming. Cross-post targets are highlighted in cyan; unmatched entries show a dimmed dash.

* **Detail pane for import preview.** Clicking any row in the import preview table expands a detail panel below showing the full untruncated comment, story summary, assignee, and cross-post target. The panel is hidden when no row is selected.

* **Flexible field separators in comment import files.** The comment file parser now accepts `|`, `~`, `;`, and `-` as field separators, allowing teams to use whichever character suits their workflow.

### Improvements

* **Extended comment file format.** Import files now carry three fields per entry — issue key, task summary, and assignee name — in addition to the comment text (e.g. `PROJECT1-123 | Fix login bug | John Smith: comment here`). This allows cross-instance matching to be driven entirely by the file without requiring the story to be loaded in the current sprint view.

* **Import preview counts moved before label construction.** `matched_count` and `unmatched_count` are now calculated before the summary label is created, eliminating a `NameError` that would occur when opening the import dialog.

* **Simplified matched/unmatched counting.** Preview dialog now derives `matched_count` and `unmatched_count` directly from `len(matched)` and `len(unmatched)` rather than re-iterating over `parsed`, removing a redundant loop.

* **story_info passed into ImportCommentsDialog.** The main window now forwards the sprint table's summary and assignee data into the dialog, allowing the preview table to display story details sourced from either the file or the loaded sprint.

---

## [0.12.0] — 2026-05-11

### Improvements

* **Token expiry field repositioned below PAT Token.** Moved the Token Expiry `QDateEdit` row to appear immediately after the PAT Token field in the settings form, grouping all credential-related fields together for clarity.

---

## [0.11.0] — 2026-05-11

### Features

* **Token expiration date per instance.** Added a `QDateEdit` field to `SettingsDialog` for both Secondary and PRIMARY instances, allowing a token expiry date to be recorded alongside each PAT. Includes a Clear button that resets the date to one year from today. Expiry values are carried through `_data`, `_set_mode`, `_save_and_accept`, and `get_settings` so they round-trip correctly when switching between instances.

* **Startup and post-save expiry warnings.** `MainWindow` now calls `_check_token_expiry` on launch and after every settings save. A warning is surfaced in the status bar if any token has already expired or is within 14 days of expiry.

---

## [0.10.0] — 2026-05-11

### Features

* **Persistent settings across sessions.** Introduced `_save_settings` and `_load_settings` on `MainWindow` using `QSettings` (platform-native storage — registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). Mode, URLs, default project, default board, and token expiry dates are stored in plain text; PAT tokens are base64-encoded before writing to disk to avoid casual plaintext exposure.

* **Auto-connect on startup.** If valid credentials are found in saved settings, `MainWindow.__init__` now constructs the `JiraClient` and triggers `_load_projects` automatically, eliminating the need to re-open settings on every launch.

* **Save settings on dialog accept.** `_open_settings` now calls `_save_settings` immediately after the settings dialog is accepted, ensuring any change is persisted without requiring a separate save step.

---

## [0.9.0] — 2026-05-11

### Bug Fixes

* **Assignee not carrying over to story edit panel.** `_on_story_selected` was routing transition results to `_on_members_loaded`, which called `set_members` and overwrote the assignee combo with transition data. Fixed by routing directly to `set_panel.set_transitions`.

* **Assignee selection lost when member list reloads.** `set_members` was rebuilding the assignee combo after `load_issue` had already set the selection, clearing it. Fixed by storing `_pending_assignee` in `load_issue` and reapplying it after the combo is rebuilt in `set_members`. If the assignee is not in the project member list they are inserted manually so they always appear.

* **Description update returning HTTP 400.** The description field was being sent as an ADF document object, which is only valid for Jira Cloud API v3. Jira Data Center API v2 expects a plain string. Fixed by changing `fields["description"]` to the raw text string.

* **Board not loading automatically when switching to PRIMARY.** `_on_project_changed` was only triggered in `_on_projects_loaded` when a default project key was configured. If no default was set the board combo stayed empty until the user manually changed the project. Fixed by always calling `_on_project_changed` after projects load.

* **New story creation failing with HTTP 400 invalid issue type.** The issue type combo in `NewStoryDialog` was storing the issue type name as its data instead of the ID. The API requires the ID. Fixed by changing `it.get("name")` to `it.get("id")` in the combo item data.

* **New story creation failing with HTTP 400 on priority and required custom fields.** Priorities were hardcoded and not valid for all projects. Three required custom fields (Activity Type, Sub-Category, Element) were missing from the create payload. Fixed by fetching valid priorities and allowed values for each custom field from the API via `createmeta` before opening the dialog.

### Features

* **Token expiry warnings.** Added a Token Expiry Date field to the Settings dialog for each instance. On startup and after saving settings, `_check_token_expiry` compares the stored date against the current date and shows a warning dialog at 30, 7, and 1 day out, and a critical dialog if the token has already expired.

* **Assignee lookup by name on new story creation.** Replaced the assignee dropdown in `NewStoryDialog` with a free-text input. On save, the entered name is validated against the Jira user search API via `find_user`. If no match is found the story is not created and a warning is shown. If a match is found the story is created and the user is assigned via a follow-up `update_issue` call.

### Improvements

* **Assignee list pagination.** `get_project_members` previously made a single request capped at 50 results. Replaced with a paginated loop using `startAt` and `maxResults=200` that continues fetching until a partial batch is returned, ensuring all project members are available in the assignee dropdown.

* **Equal split between story list and edit panels.** Changed `splitter.setSizes([680, 480])` to `splitter.setSizes([1, 1])` so both panels always occupy 50% of the available width regardless of window size.

* **Edit panel horizontal scrolling removed.** Set `ScrollBarAlwaysOff` on the edit panel scroll area and removed hardcoded `setMinimumWidth` calls from combo boxes inside `StoryEditPanel`. Fields now expand to fill available width using `FieldGrowthPolicy.ExpandingFieldsGrow` instead of overflowing the panel.

---

## [0.8.0] — 2026-05-08

### Features

* **Default project and board per instance.** Added Default Project and Default Board fields to the settings dialog for both Secondary and PRIMARY. On connect, the app auto-selects the configured project and board, triggering the full load chain without manual scrolling.

### Bug Fixes

* **401 errors on connect caused by inaccessible projects.** `_on_project_changed` was firing immediately on the first project in the list before the default selection could take effect. Changed the auto-trigger condition so it only fires when a default project is configured, preventing API calls to projects the user doesn't have access to.

---

## [0.7.0] — 2026-05-08

### Bug Fixes

* **Assignee dropdown showing workflow transitions instead of users.** `set_members` had no guard against receiving transitions data, which has a `to` key on each item. Added a check at the top of `set_members` to silently ignore any list that looks like transitions data.

* **Assignee showing `?` for all members.** Data Center user objects use `name` and `key` fields, not `accountId`. Updated `set_members`, `load_issue`, and `_on_save` to use a `name → key → accountId` fallback chain, and `displayName → name` for display text.

* **Assignee unassigned on save.** `_on_save` was sending `{"accountId": aid}` which Data Center rejects. Changed to `{"name": aid}` to match the DC API format.

### Improvements

* **Removed assignee filter dropdown from filter bar.** The dropdown was receiving transitions data and showing incorrect values. Removed in favour of the text search box which already filters by assignee name across all columns.

---

## [0.6.0] — 2026-05-08

### Features

* **Import comments from a text or markdown file.** Added a `📄 Import Comments` button that parses a file formatted as `KEY: comment text` and posts each comment to the matching story. A preview dialog shows matched vs unmatched entries before posting.

* **Cross-instance comment posting.** When importing comments, the app searches the other instance (Secondary or PRIMARY) for stories with the same summary and assignee. If a match is found, the comment is posted to both instances automatically. Preview dialog shows `✓ Both instances` in cyan for cross-posted entries.

* **JQL issue search added to `JiraClient`.** Added `search_issues_jql` method for searching issues by JQL query, used for cross-instance story matching by summary and assignee.

---

## [0.5.0] — 2026-05-07

### Features

* **Per-instance custom field mapping.** Added `_FIELD_MAP` class variable to `JiraClient` with story point and feature link field IDs for each instance. Secondary uses `customfield_10106` / `customfield_10100`, PRIMARY uses `customfield_10006` / `customfield_10000`. All hardcoded `customfield_10016` references replaced with dynamic lookups.

* **Feature link field added to story edit panel.** Added a Feature Link text field to the Story Fields group in the edit panel. Loads and saves the correct custom field ID based on the active instance.

### Bug Fixes

* **Story points field rejected on save.** `_do_save` now catches `RuntimeError` containing the story points field ID and retries the save without that field, preventing a failed save from blocking other field updates.

---

## [0.4.0] — 2026-05-07

### Features

* **Secondary and PRIMARY dual-instance support.** Replaced the Cloud/Data Center toggle in settings with a Secondary/PRIMARY toggle. Each instance stores its own URL and PAT token independently. Switching instances saves the current fields before loading the other set. The active instance is shown in the top bar.

* **Removed Cloud-specific code paths.** Both instances are Data Center so ADF comment bodies, `accountId` assignees, and API v3 references were removed. All API calls now use Bearer PAT auth and REST API v2.

---

## [0.3.0] — 2026-05-07

### Features

* **New story creation.** Added `＋ New Story` button to the filter bar. Opens a dialog with summary, issue type, priority, story points, assignee, sprint, due date, and description fields. After creation the story table refreshes automatically.

* **Status transitions.** When a story is selected, available workflow transitions are loaded from Jira and shown in a Status Transition dropdown. Applying a transition on save calls the Jira transitions endpoint separately from the field update.

* **Sprint move.** Added a Sprint dropdown to the edit panel. Selecting a different sprint and saving moves the issue to that sprint via the Agile API.

* **Due date field.** Added a calendar picker with a Clear button to the edit panel. Supports setting or removing a due date on save.

* **Priority and issue type fields.** Added Priority (Highest/High/Medium/Low/Lowest) and Issue Type dropdowns to the edit panel, populated from the project's configured types on connect.

### Improvements

* **Fibonacci story points.** Replaced the free-entry spinner with a dropdown of standard Fibonacci values: 0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89.

---

## [0.2.0] — 2026-05-07

### Bug Fixes

* **HTTP 404 `No project could be found with key 'search'`.** Several API methods were passing query-string paths through `_request()`, causing Jira to interpret `search` as a project key. Fixed `get_projects`, `get_project_members`, `search_users`, and `get_priorities` to build full URLs manually, bypassing the router issue.

* **`'list' object has no attribute 'get'`** on project load. The `/project` endpoint returns a plain list but the code called `.get("values", [])` on it. Added an `isinstance` check to handle both list and dict responses.

* **`'dict' object is not callable`** on connect. `_FIELD_MAP` was defined as a dict but called as a function in `__init__`. Fixed by accessing it with `.get()`.

### Improvements

* **Error messages include the full URL.** All `HTTPError` handlers now include the HTTP method and URL in the error string, making it much easier to identify which API call is failing.

---

## [0.1.0] — 2026-05-07

### Features

* **Initial release.** Dark-themed PyQt6 desktop app for managing Jira Data Center sprint stories. Connects via Bearer PAT token. Loads projects, boards, and sprints from the Agile API. Story table shows key, summary, assignee, story points, and status. Edit panel supports updating assignee, story points, description, and posting comments. Live text filter across all table columns.
