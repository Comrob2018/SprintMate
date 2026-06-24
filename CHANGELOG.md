# SprintMate Changelog
## [2.24.0] — 2026-06-23
### Features
* **Configure moved to Help menu.** The **⚙ Configure** button has been removed from the top bar. Configure is now the first item in the **Help** menu alongside Keyboard Shortcuts, Check for Updates, and About SprintMate. The top bar is now: Switch Instance · Stories · Active Sprint · Backlog · Reports · Refresh.
* **Reports tab.** A new **📊 Reports** tab (fourth tab, `Alt+4`, top-bar **📊 Reports** button) replaces the Sprint Report, Velocity, and Compare controls that were scattered across the Stories toolbar. The tab contains:
  * A **SPRINT** dropdown pre-populated with all sprints on the board, with the active sprint pre-selected.
  * **📊 Sprint Report** — generates the full dashboard-style HTML report inline in a `QTextBrowser` inside the tab. No separate dialog window.
  * **👤 People Report** — generates the people report inline, using all assignees from the currently loaded sprint.
  * **📈 Velocity** — generates a clean velocity history table inline (last 8 closed sprints by default).
  * **⇆ Compare** dropdown and button — moved from the Stories toolbar row 1.
  * **⬇ Save HTML** button (right-aligned) — enabled after any report is generated, saves the current report to a file.
  * Reports render directly into the tab browser; `SprintReportDialog` is reused internally for its `_build_report` and `_build_people_report` methods without showing the dialog.
* **? help button removed from toolbar.** The keyboard shortcut reference is now accessible via **Help → Keyboard Shortcuts…** or the `?` key. The button is no longer needed in the toolbar.
* **Stories toolbar decluttered.** Row 2 now contains: New Story, Bulk Create, Import, Export, Archive, Bulk Edit, Assignee filter, and search box. Sprint Report, Velocity, and ? have been removed; Compare has moved to the Reports tab.

---

## [2.23.1] — 2026-06-23
### Bug Fixes & Polish
* **`_copy_key` and `_undo_save` restored.** Both methods were lost during a prior edit that merged the body of `_undo_save` into `_copy_key` with no `def` header, causing an `AttributeError` on startup. Both are now separate, correctly-defined methods.
* **Recent stories list persists across sessions.** `_recent_keys` is now written to `QSettings` as a JSON array in `_save_settings` and restored in `_load_settings`. The list is also saved on every clean app close via `closeEvent`. Previously it reset to empty on every launch.
* **Column visibility preferences persist across sessions.** `_column_prefs` (a `dict[board_id -> set[col_indices]]`) is now serialised to JSON and saved to `QSettings` on settings save and on app close. It is restored on launch, so per-board column preferences survive restarts.
* **Settings (including new persistence fields) now saved on close.** `closeEvent` now calls `_save_settings()` before accepting, ensuring recent keys and column prefs are written even when the user closes without changing any connection settings.
* **Removed dead `_get_issue_links` method.** This method was added as a helper but was never called — the story links panel reads directly from the `issuelinks` field already fetched with each sprint load. The dead code has been removed.
* **About dialog GitHub link fixed.** `_show_about` previously hardcoded `YOUR_USERNAME/YOUR_REPO` as the repository URL. It now derives the link from `GITHUB_RAW_URL` using the same logic as the update checker, so both always point to the same repo and a URL change only needs to be made in one place.
* **Improved duplicate detection in quick-add.** `_check_quick_add_duplicate` was rewritten with three improvements: (1) case-insensitive, punctuation-stripped word comparison instead of raw `str.split()`; (2) a stop-word list (articles, prepositions, conjunctions) is excluded before comparing, preventing false positives like "Add a button to the form" vs "Add a field to the form"; (3) a minimum of 3 meaningful words is required before the check runs, avoiding false positives on very short summaries. Threshold raised from 60% to 65%.

---

## [2.23.0] — 2026-06-23
### Features
* **Kanban board load toolbar.** The Active Sprint board now shows a compact load toolbar at the top when no stories are loaded, instead of just showing an empty board. The toolbar contains PROJECT, BOARD, and SPRINT dropdowns and a **↺ Load** button, with a hint label reading "Select a sprint and click Load to populate the board."
  * `sync_combos()` mirrors the Stories tab's three selectors into the Kanban toolbar whenever sprints finish loading and whenever the user switches to the Kanban tab, so if a sprint is already selected on the Stories tab the toolbar is pre-filled automatically.
  * Clicking **↺ Load** calls `_on_kanban_load_requested`, which syncs the selected values back to the Stories tab combos (without triggering cascade signals) and then fires the same load path as the Stories tab Load button. Both views end up in sync.
  * The toolbar auto-hides once `populate()` is called with stories, and reappears when `clear()` is called (board change, instance switch, sprint clear).

---
 
## [2.22.0] — 2026-06-23
### Features
* **Sprint progress bar.** A 4px coloured bar sits below the story count row, always visible when a sprint is loaded. It fills green (≥80% of points done), amber (40–79%), or red (<40%). Hovering shows "X of Y pts done (Z%) · N of M stories done". Hides and resets to zero on sprint clear.
* **Column persistence.** Visible column preferences are now saved per board ID in `_column_prefs`. `_show_column_menu` saves the current visible set after every toggle. `_populate_table` restores saved prefs for the current board on load instead of always resetting to defaults.
* **Bulk edit dialog.** A **✎ Bulk Edit** button in the Stories toolbar (enabled when stories are loaded) opens a dialog with three independent fields: Assignee, Priority, and Story Points — all defaulting to "No change". Only fields explicitly set are updated. Results summarise successes and failures per story; the sprint reloads after.
* **Unsaved changes indicator.** `StoryEditPanel` now emits a `changed` signal the first time any field is modified. `_mark_unsaved_row` appends ` ●` to the KEY cell of the currently edited row and turns it amber. Selecting a different row clears the previous row's indicator. Saving also clears it.
* **Story detail preview on hover.** `_populate_table` now builds a rich tooltip for both the KEY and SUMMARY cells: the description excerpt (up to 140 chars, ADF-flattened) and the most recent comment with author name.
* **Recent stories sidebar.** A **🕐** button in the quick-add bar opens a popup menu of the last 10 viewed issue keys with their summaries. Selecting one scrolls the table to that row. A "Clear history" item resets the list. The MRU list is updated on every row selection.
* **Duplicate detection on quick-add.** Before creating a story via the quick-add bar, `_check_quick_add_duplicate` computes word-overlap between the typed summary and every existing sprint story. If >60% of words match, a "Possible Duplicate" dialog lists the matches and asks for confirmation.
* **Story links panel.** A read-only "LINKED ISSUES" panel is now shown in the edit panel when the selected story has Jira issue links (blocks / is blocked by / relates to). The panel shows the relationship type, linked key, status, and summary excerpt. It is hidden when there are no links. `issuelinks` is now included in the sprint issues fetch.
* **Keyboard shortcut reference card.** A **?** button in the toolbar and the `?` key open a scrollable reference dialog listing all shortcuts grouped into three sections: Global, Table (when focused), and Inline editing. Each entry shows a monospace key badge and description.

---

## [2.21.1] — 2026-06-23
### Bug Fixes
* **Quick-add issue type selection.** The quick-add bar previously always created issues using the first type returned by Jira (`types[0]`), with no way for the user to choose. A type combo is now placed to the right of the summary field. It is populated from the same issue type list as the edit panel when a project loads, with "Story" pre-selected if present, otherwise the first available type. The status message during creation now reflects the chosen type (e.g. "Creating Bug…"). The combo is disabled and cleared when the sprint view resets. A fallback to the edit panel's first type is retained if the combo is somehow empty.

---

## [2.21.0] — 2026-06-23
### Features
* **Professional sprint report redesign.** `_build_report` and `_build_burndown_svg` were fully rewritten. The report is now a dashboard-style HTML document rendered on a light grey background with white card surfaces, subtle box shadows, and a consistent font stack (`-apple-system`, `Segoe UI`, `Helvetica`, `Arial`).
* **Report header** — a dark gradient panel (`#1c2128 → #2d333b`) contains the report title, sprint name as a subtitle, and a meta row with the sprint date range (when available), generation date, and a story/points count.
* **Stat cards** — five white cards in a flex row, each with a coloured left-border accent, an emoji icon, a large metric, a label, and a contextual sub-line (e.g. "12 remaining"). The velocity card replaces the number with an inline SVG circular progress ring with the percentage overlaid in the centre.
* **Section headings** — small all-caps labels with a horizontal rule extending to the right edge, providing clear visual separation between report sections.
* **Burndown chart** — rebuilt with a proper background grid (vertical day lines and horizontal point lines), a green-tinted ideal-region shading, a blue-tinted actual-region shading, a thicker actual line with a rounded dot at the current position, and an ahead/behind callout label (`▲ N pts ahead` / `▼ N pts behind` / `On track`) positioned above the day marker. The callout anchor shifts left or right at chart edges to prevent clipping.
* **Status breakdown** — replaced the plain count table with a proportional horizontal stacked bar (one segment per status, coloured to match the app's status colour map) and a flex legend row below showing a colour swatch, name, count, and percentage. Zero-count statuses are omitted.
* **Team section** — replaced the assignee table with a responsive CSS grid of per-person cards. Each card shows an avatar circle with initials, name and story/points count, two inline progress bars (stories complete and points complete with percentages), and a footer row showing done / pts done / remaining as coloured numbers.
* **Story table** — sticky column headers, full-row hover highlight, pill-shaped status badges (coloured background matching status), directional priority symbols with colour coding (▲▲ Highest red → ▼▼ Lowest grey), and overdue rows highlighted with a full red-tinted row background (previously only the due date cell was coloured).
* **Print/export CSS** — a `@media print` block ensures the dark header prints correctly (`-webkit-print-color-adjust: exact`), removes box shadows, prevents cards from breaking across pages, and un-sticks table headers for pagination.

---

## [2.20.0] — 2026-06-23
### Features
* **Kanban filter bar.** A filter bar now sits below the board header with three controls that work together in real time — no button press required.
  * **Text search** — filters cards by issue key or summary substring.
  * **Assignee** — a combo populated automatically from the loaded issues. Signals are blocked during rebuild so a filter pass isn't triggered mid-load. The selected assignee is preserved across sprint reloads if the same person is still present.
  * **Priority** — Highest / High / Medium / Low / Lowest.
  * A **✕ Clear** button resets all three at once (blocking all signals during the reset to avoid redundant render passes).
  * A "Showing N of M" label appears in the bar whenever any filter is active and disappears when all filters are cleared.
* **Kanban board title and tab label reflect the active sprint.** The board heading (previously the static text "◈  KANBAN BOARD") now displays the loaded sprint name in uppercase (e.g. `◈  SPRINT 42`). The tab label updates to match (e.g. `⊞  Sprint 42`). Both reset to `◈  ACTIVE SPRINT` / `⊞  ACTIVE SPRINT` when the sprint view is cleared. The top-bar navigation button was also renamed from "⊞ Kanban" to "⊞ Active Sprint".
* **Backlog right-click context menu with Open in Jira.** Right-clicking any row in the Backlog table now opens a context menu. Menu items adapt for single vs multi-selection.
  * **⎋ Open in Jira** — opens the issue in the browser. Only enabled for single-row selection; disabled when no base URL is available.
  * **⎘ Copy Key / Copy N Keys** — copies the key (or a comma-separated list of keys) to the clipboard.
  * **⇧ Move to Sprint / Move N Stories to Sprint** — moves the selected stories to whichever sprint is chosen in the Move to Sprint dropdown. Disabled if no sprint is selected. This duplicates the toolbar Move button for convenience when right-clicking.

---
 
## [2.19.0] — 2026-06-22
### Features
* **Sprint management — create, start, rename, and close sprints.** A new **⊕ Sprint** button appears in the filter toolbar once a board is loaded. Clicking it opens the Sprint Manager dialog, which has two tabs.
  * **＋ Create** — enter a name (required), optional goal, start date, and end date, then choose whether to create the sprint as a future sprint or create-and-start it immediately. Status messages appear inline without a separate popup.
  * **⚙ Manage** — a dropdown lists every sprint on the board. Selecting one pre-fills its current name, goal, and dates. Three action buttons are available: **💾 Save Changes** (rename, reschedule, update goal), **▶ Start Sprint** (confirms dates and warns that only one sprint can be active at a time), and **■ Close Sprint** (confirms that incomplete stories stay on the board). Start and Close are only enabled when the selected sprint is in the correct state (future / active respectively).
  * After any successful operation the sprint dropdown in the main window reloads automatically.
* **`JiraClient.create_sprint`** — calls `POST /rest/agile/1.0/sprint` with name, originBoardId, startDate, endDate, and optional goal. Returns the full created sprint dict including its `id`.
* **`JiraClient.update_sprint`** — calls `POST /rest/agile/1.0/sprint/{id}` and automatically falls back to `PUT` on HTTP 405 (some older DC instances require PUT). Accepts any combination of name, state, startDate, endDate, goal, and completeDate. Passing `state="active"` starts the sprint; `state="closed"` closes it.

---
 
## [2.18.0] — 2026-06-22
### Features
* **Kanban board persists between tab switches.** `KanbanBoardWidget.populate()` now skips a full re-render when the issues list identity and sp_field are unchanged. Switching away from Kanban and back no longer rebuilds all cards. A `refresh(force=True)` call is used after drag-and-drop transitions to force an update only when the data has actually changed.
* **Burndown chart uses real sprint dates.** `_open_sprint_report` now calls `JiraClient.get_sprint_detail(sprint_id)` (a new `GET /rest/agile/1.0/sprint/{id}` endpoint) to fetch the sprint's `startDate` and `endDate`, and passes them to `SprintReportDialog` as `sprint_detail`. The burndown chart now derives its x-axis from the real sprint calendar rather than a fixed 14-day estimate. The footnote shows the actual sprint date range. Falls back to the estimate-based approach if dates are unavailable.
* **Inline status editing.** Double-clicking the **STATUS** cell in the story table opens a combo populated with the issue's available Jira transitions. Selecting one and clicking **Apply** transitions the issue immediately and reloads the sprint.
* **Inline due date editing.** Double-clicking the **DUE DATE** cell opens a calendar date-picker. Clicking **Save** updates the due date; clicking **Clear Date** removes it entirely.
* **New Story button on Kanban board.** The Kanban board header now includes a **＋ New Story** button that delegates to the Stories toolbar's New Story flow.
* **Backlog: Move to Sprint.** The Backlog view now includes a sprint selector and a **⇧ Move** button. Select one or more backlog stories, choose a target sprint, and click Move. The active sprint is pre-selected. Moved stories are removed from the backlog table immediately.
* **Backlog: Export CSV.** An **⬇ Export CSV** button in the Backlog toolbar exports all loaded backlog items (key, summary, assignee, priority, story points, issue type, due date) to a CSV file.
* **Velocity history chart.** A new **📈 Velocity** button in the Stories toolbar opens a velocity history dialog. It fetches up to N recent closed sprints (configurable 3–10), computes committed vs completed points per sprint from the actual sprint issues, and renders an SVG bar chart. A summary table and **⬇ Export CSV** button are included.
* **Story ranking.** Two **↑ Rank Up** / **↓ Rank Down** buttons appear in the quick-add bar below the stories table. Clicking either calls `PUT /rest/agile/1.0/issue/rank` with `rankBeforeIssue` or `rankAfterIssue` to re-order the selected story within the sprint. If the board's ranking field is not writable, a clear error message explains why instead of silently failing.
* **Kanban transition fuzzy name matching.** Dragging a card to a new column now uses a four-tier matching strategy: (1) exact target-status name, (2) starts-with, (3) contains, (4) transition name match. This handles boards where Jira workflows use non-standard transition names (e.g. "Start Progress" instead of naming the target "In Progress"). If no match is found, the error message lists all available transitions.
* **Backlog JQL fallback.** `_load_backlog` now tries `sprint is EMPTY` first and automatically falls back to `sprint not in openSprints() AND sprint not in closedSprints()` if the first form is rejected by the server. Both errors are surfaced if both forms fail.
* **Retry button on failed background operations.** The default error handler in `_spawn` now opens a dialog with a **↩ Retry** button when `retry_fn` is provided. Callers that pass `retry_fn` get one-click retry without re-navigating. The button is omitted when no retry function is available, preserving the previous behaviour.
* **Sprint comparison CSV export.** After a sprint comparison completes, SprintMate offers to export the diff as a CSV (key, change_type, diffs). The change types are `added`, `changed`, and `removed`. The dialog appears automatically after the compare finishes; the export can also be triggered via the prompt.

---

## [2.17.0] — 2026-06-22
### Features
* **Bulk status transitions.** Right-click one or more selected rows to reveal a "Transition N stories to…" submenu with all five canonical statuses. Each story's available transitions are fetched individually, the matching transition is applied, and a summary reports successes, failures, and any stories that had no matching transition available.
* **Keyboard shortcuts — full set.** In addition to the existing Ctrl shortcuts, the stories table now responds to single-key bindings when focused: `N` (New Story), `R` (Refresh), `S` (Save edit panel), `Escape` (clear selection), `Delete` (quick-archive the selected row with a confirm dialog), and `↑`/`↓` arrows (navigate rows). Tab switching: `Alt+1` (Stories), `Alt+2` (Kanban), `Alt+3` (Backlog).
* **Inline editing of story points and assignee.** Double-clicking the **PTS** column opens a Fibonacci combo pop-up; double-clicking the **ASSIGNEE** column opens a team-member combo. Both save immediately to Jira and reload the sprint on confirmation, without opening the full edit panel.
* **Burndown chart in Sprint Report.** The Sprint Report HTML now includes an SVG burndown chart above the status breakdown table. The chart shows an ideal straight-line burndown and an actual remaining-points line, with a shaded area and a remaining-points marker at the estimated current sprint day.
* **Kanban board view with drag-and-drop.** A new **⊞ Kanban** tab shows all loaded stories as cards in five status columns (To Do / In Progress / In Review / Done / Blocked). Cards display the issue key, summary, assignee, and story points. Dragging a card to a new column triggers a Jira status transition. Clicking a card switches back to the Stories tab and selects that row. Accessible via `Alt+2` or the top bar **⊞ Kanban** button.
* **Backlog view.** A new **☰ Backlog** tab with a **Load Backlog** button fetches all open issues for the current project that have no sprint assigned (`sprint is EMPTY AND statusCategory != Done`). Results display in a sortable, filterable table. Clicking a story that is also in the active sprint switches to the Stories tab and selects it. Accessible via `Alt+3` or the top bar **☰ Backlog** button.

---

## [2.16.1] — 2026-06-22
### Bug Fixes
* **Fixed story points mismatch between the left panel and edit panel.** The `_FIELD_MAP` correctly maps `customfield_10006` (Primary) and `customfield_10106` (Secondary) as the story point field IDs per instance, but eleven places throughout the code fell back to the hardcoded `customfield_10016` when the detected field returned no value. On instances where `customfield_10016` holds a different or stale value, the left panel and edit panel would read from different fields and show different numbers. Fixed by adding `JiraClient._SP_FALLBACKS` — an ordered list of all known story point field IDs across Jira DC configurations — and replacing all hardcoded `or f.get("customfield_10016")` fallback chains with a consistent `next(...)` expression that walks `_SP_FALLBACKS` in order, always trying the detected field first. Also added `JiraClient.get_story_points(fields)` as a reusable helper for the same logic. The default `_sp_field` initialisation was updated from the hardcoded `"customfield_10016"` to `JiraClient._FIELD_MAP[MODE_SECONDARY]["story_point"]` so the default is always in sync with the field map. The save error handler was also updated to exclude all known SP fields when retrying a save without story points, not just `customfield_10016`.

---

## [2.16.0] — 2026-06-22
### Features
* **Sprint Report tab now supports filtering by sprint or date range.** The Sprint Report tab has been refactored to match the People Report tab pattern. A SCOPE control group replaces the static title — choose a sprint from the dropdown (pre-selected to the currently loaded sprint) or switch to Date Range and enter From/To dates in `YYYY-MM-DD` format. Clicking **▶ Generate Sprint Report** fetches the relevant issues and renders the report. The **⬇ Save as HTML** button is disabled until the first successful generate. Sprint scope calls `get_sprint_issues(board_id, sprint_id)`; date range scope builds a JQL query with `updated >=` / `updated <=` bounds and fetches via the search API with pagination.
* **Sprint and People Report tabs now share a single sprint fetch.** `_load_sprints_for_people_tab` has been replaced by `_load_sprints_for_tabs`, which fetches all sprints once on dialog open and populates both the Sprint Report combo and the People Report combo in a single background call, reducing redundant API requests.
* **`_build_report` now accepts issues and a scope label as parameters.** The method signature changed from `_build_report(self)` to `_build_report(self, issues, scope_label)`, allowing it to render any set of issues with any title rather than always using `self._issues` and `self._sprint_label`. The HTML `<title>` and meta line reflect the scope label passed in.
### Bug Fixes
* **Fixed `TypeError: setStyleSheet argument has unexpected type 'ellipsis'`.** The `self._browser.setStyleSheet(...)` call had a literal `...` ellipsis placeholder instead of the stylesheet string, causing a crash on dialog open. Replaced with the correct f-string stylesheet.
* **Fixed `TypeError: _build_report() takes 1 positional argument but 3 were given`.** The local `_build_report` signature had not been updated to accept `issues` and `scope_label`, causing a crash when `_generate_sprint_report` called `self._build_report(issues, scope_label)`.
* **Fixed Pylance false positives for `sprint_btn_row`, `scope_label`, and `all_issues`.** `scope_label` and `all_issues` were only defined inside `if`/`else` branches, making them unresolvable to Pylance at the point `_on_done` referenced them. Fixed by hoisting all variable assignments to the top of `_generate_sprint_report` and collapsing the two branch-scoped `_do` closures into a single `_do` that branches internally. Also replaced `__import__` and inline `import` statements with the already-imported top-level `urllib.parse`, `urllib.request`, and `json` modules.

---

## [2.15.1] — 2026-06-22
### Features
* **Custom display names for instances.** Added a "Display Name" field to the settings dialog for each instance. When set, the name replaces "Primary" / "Secondary" everywhere it appears in the app — the top bar mode indicator, the Switch Instance status message, the sprint load status, and the clone dialog instance selector. Falls back to "PRIMARY" / "SECONDARY" if left blank. Values are persisted via `QSettings` as `primary_display_name` and `secondary_display_name`. A new `_instance_label(mode)` helper on `MainWindow` centralises the fallback logic so all call sites stay consistent.

---

## [2.15.0] — 2026-06-22
### Features
* **Clone stories to any project or instance.** Added a "⎘ Clone" button to the story edit panel header. Opens a dialog with three sections: a target instance selector (current instance, or the other saved instance if credentials exist), a target project dropdown populated lazily from the selected instance, and editable fields for Summary (pre-filled as `[Clone] Original summary`), Description, and Assignee. Executes via `POST /rest/api/2/issue` against the target `JiraClient`. On success, shows the new issue key with **Copy Key** and **Open in Jira** action buttons.

---

## [2.14.2] — 2026-06-19
### Bug Fixes
* **Archive dialog checkboxes were rendering as slivers.** Replaced `QCheckBox` widgets wrapped in a centred `QHBoxLayout` cell widget with native `QTableWidgetItem` check states. The checkbox now fills the full row height and responds to a click anywhere in the first column. Count updates are now driven by `table.itemChanged` instead of per-widget `stateChanged` signals.

### Improvements
* **Added assignee column to the archive dialog.** The picker table now shows KEY, SUMMARY, ASSIGNEE, and STATUS, making it easier to identify stories by owner before archiving. The search box also matches against assignee name.
* **Added sortable column headers to the archive dialog.** Clicking any column header sorts the table ascending or descending, consistent with the main sprint table.

---

## [2.14.1] — 2026-06-19
### Features
* **Archive stories from the sprint view.** Added a "🗄 Archive" button to the filter toolbar. Opens a searchable picker dialog with checkboxes to select which stories to archive, followed by a confirmation dialog. Calls `POST /rest/api/2/issue/archive` (Jira Data Center 8.1+). Archived issues become read-only and are removed from boards and search results but remain restorable from Jira administration. `unarchive_issues` (`PUT /rest/api/2/issue/unarchive`) is also implemented in `JiraClient` for future use.
* **Edit posted comments.** Added a "✎ Edit" button to the RECENT COMMENTS panel in the story edit panel. If the story has more than one comment, a picker dialog lets the user select which to edit. Opens a pre-filled text editor and calls `PUT /rest/api/2/issue/{key}/comment/{id}` on save. Comment IDs are now stored when a story is loaded to support this.
* **Delete posted comments.** Added a "✕ Delete" button to the RECENT COMMENTS panel. Shows a comment preview in a confirmation dialog before calling `DELETE /rest/api/2/issue/{key}/comment/{id}`. Jira's own permission rules apply — users can only delete comments they authored unless they have admin rights.

### Bug Fixes
* **Fixed HTTP 406 error on archive requests.** The `archive_issues` and `unarchive_issues` methods were routing through `_request()`, which sends `Accept: application/json` on every call. Jira's archive endpoint returns `text/plain`, causing the server to reject the request with 406 Not Acceptable before any archiving occurred. Both methods now bypass `_request()` and set `Accept: text/plain` directly, then parse the plain-text response for any error lines.
* **Fixed HTTP 400 error on archive requests.** The request body was being sent as `{"issueIdsOrKeys": [...]}` but the Jira Data Center archive endpoint expects a bare JSON array of strings. Jackson was rejecting the object wrapper with a `START_OBJECT` deserialization error. Both `archive_issues` and `unarchive_issues` now serialize the key list directly as `["KEY-1", "KEY-2"]`.
* **Archived stories now disappear from the board immediately.** After a successful archive, `_on_done` was calling `_load_sprint_issues()`, which re-fetches from Jira. Because Jira's search index can lag behind the archive operation, archived issues were returning in the response and reappearing in the table. The fix removes archived keys directly from `self._issues` in memory and repopulates the table locally, with no round-trip to Jira. If the currently selected story was archived, the edit panel is also cleared.

---

## [2.14.0] — 2026-06-19
### Features
* **File attachments for stories.** Added a "📎 Attach File" button to the story edit panel header. Clicking it opens a multi-file picker (any file type) and uploads each file to the selected Jira issue via the REST API (`POST /rest/api/2/issue/{key}/attachments`) using `multipart/form-data` with the required `X-Atlassian-Token: no-check` header. Per-file success and failure are reported individually.
* **Sprint report generator.** Added a "📊 Sprint Report" button to the filter toolbar, enabled once stories are loaded. Generates an HTML report containing: a summary stat card row (total stories, done count, total/done points, velocity %), a status breakdown table with colour-coded badges, a per-assignee table with story counts, points, and a visual progress bar, and a full story table with keys hyperlinked to Jira. The report renders inline and can be saved as an HTML file via a save dialog.

---

## [2.13.2] — 2026‑05‑19
### Bug Fixes
* **Fixed row‑change handling errors.** The previous implementation connected to a non‑existent `currentRowChanged` signal and processed the wrong argument types, resulting in AttributeError and TypeError. The slot now receives the correct QModelIndex objects, extracts row numbers safely, and prevents invalid‑index crashes.
### Features
* **Added previous‑row tracking.** Initialized `_current_row` and `_previous_row` attributes before the signal connection and updated them on each selection change. This makes it possible to react to both the newly selected row and the row that was selected before.
### Improvements
* **Enhanced slot robustness and API clarity.** The `_on_row_changed` method signature now matches the signal (`(current, previous)`), includes validity checks (`isValid()`), and stores row indices as integers. This improves code readability and reduces the risk of future type‑related bugs.
* **Streamlined signal connection.** Utilized a lambda wrapper to forward only the needed row numbers, keeping the rest of the dialog logic unchanged while still providing access to the previous row when needed.

---

## [2.13.1] — 2026-05-19
### Features
* **Check for Updates via Help menu.** A native Help menu has been added to the menu bar containing `“Check for Updates…”` and `“About SprintMate”`. The update check fetches the raw script from the URL defined in `GITHUB_RAW_URL`, reads it line-by-line until it finds the APP_VERSION assignment, and compares it against the running version — without loading the full file into memory. The fetch runs in a background thread via the existing _spawn mechanism so the UI never blocks. If a newer version is found, a dialog prompts the user to open the repository page in their browser; the repo URL is derived automatically from `GITHUB_RAW_URL` by replacing raw.githubusercontent.com with github.com.
* **Two-row filter bar.** The single filter bar row has been split into two. Row 1 contains the board/sprint selection controls (PROJECT, BOARD, SPRINT, Load Stories, COMPARE). Row 2 contains the action buttons (＋ New Story, ＋＋ Bulk Create, 📄 Import, ⬇ Export) on the left and the ASSIGNEE filter and text search on the right. Both rows share the same horizontal padding. The fb_layout QHBoxLayout has been replaced with a QVBoxLayout (fb_outer) containing two QHBoxLayout children (fb_row1, fb_row2).
### Improvements
* **`GITHUB_RAW_URL` module-level constant.** The remote URL used for update checks is defined as a single constant near `APP_VERSION`, making it straightforward to update when the repository is moved or renamed without searching through method bodies.

---

## [2.13.0] — 2026-05-18
### Features

* **Undo last save.** A "↩ Undo Save" button added alongside the Save button restores all edit-panel fields (assignee, feature link, issue type, priority, story points, sprint, due date, description) to their exact pre-save state. The button is enabled only after a successful save and cleared automatically when a different story is loaded.
* **Sprint velocity summary bar.** A centred label in the count row shows X pts total · Y in progress · Z done (N pts), computed from the loaded issues on every sprint load. Points are read from the configured story-point field with the standard customfield_10016 fallback.
* **Keyboard story navigation.** Ctrl+↑ and Ctrl+↓ step through visible table rows from anywhere in the main window. Rows hidden by the text search or assignee filter are skipped.
* **Token expiry banner.** An amber banner (#5A3E00 background, ACCENT_ORANGE border) now appears below the progress bar when a token is expired or within 14 days of expiry, replacing the status-bar-only warning that was easy to miss. The banner is dismissable with a ✕ button and hides automatically when no warnings are active.
* **Inline quick-add story bar.** A text field at the bottom of the story table creates a story in the current sprint on Enter, using the first available issue type. The table reloads and auto-selects the new issue on success; the bar is disabled while no sprint is loaded.
* **Comment templates.** A "Template:" dropdown above the comment text box populates the field from five built-in templates (Blocked by:, Ready for review., Carried to next sprint., In progress — ETA:, Merged to main.). The combo resets to "— select —" after selection so the same template can be reapplied. Templates are defined in the new COMMENT_TEMPLATES module-level constant.
* **Duplicate story.** A "⧉ Duplicate Story" item in the row context menu creates a copy of the selected story in the current sprint, inheriting summary (suffixed " (copy)"), issue type, priority, story points, assignee, due date, and description. ADF descriptions are converted to plain text before submission. The table reloads and auto-selects the new issue on success.
* **Sprint comparison view.** A COMPARE dropdown and "⇆ Compare" button in the filter bar highlight differences between the loaded sprint and a selected comparison sprint. Stories new to the current sprint are tinted green (#1A3A1A); stories with changed status, assignee, or story points are tinted blue (#1A2A3A). Hovering the KEY cell of a changed row shows a tooltip listing each diff. The status bar reports counts of added, removed, and changed stories. Highlights persist until the sprint is reloaded.
* **Copy row as Markdown.** Ctrl+Shift+M and a new "⎘ Copy as Markdown" context menu item copy the selected row as | [KEY](url) | summary | assignee | status | pts |. The KEY is hyperlinked to Jira when a base URL is configured.
* **Due date warning highlights.** Overdue due dates are shown in ACCENT_ORANGE with an "Overdue by X day(s)" tooltip; dates within three days are shown in amber (#E3B341) with a "Due in X day(s)" tooltip. Applied at populate time using the existing date import.
* **Assignee filter dropdown.** An ASSIGNEE combo in the filter bar restricts the table to a single assignee's stories. The list is built from the loaded sprint on every load, resets when the sprint view is cleared, and is ANDed with the existing text search so both filters can be active simultaneously. _filter_table updated to respect the assignee selection.
Remember last sprint per board. The selected sprint ID is written to QSettings as last_sprint_{board_id} when stories are loaded and restored automatically the next time sprints are loaded for the same board.

---

## [2.12.1] - 2026-05-18

### Bug Fixes

* **`_parse_comments_csv` no longer silently discards read errors.** A bare except Exception: pass meant any file permission error, encoding failure, or malformed CSV was indistinguishable from an empty file, causing the caller to show a misleading "no valid entries found" warning. The exception is now re-raised as a RuntimeError and the caller shows a specific "File Error" dialog with the underlying reason.
* **`_load_sprint_issues` network and API failures now surface to the user.** The `_spawn` call had no `on_error` handler, so any exception from `get_sprint_issues` — HTTP error, network failure, or non-JSON response — fell through to the default worker error path without clearing the busy indicator. Added an explicit `on_error` handler consistent with all other spawn call sites in MainWindow.
* **Cross-instance JQL search errors no longer crash the comment import flow.** `_import_comments` called `other_client.search_issues_jql` directly in the main thread without error handling. Since `search_issues_jql` now raises on HTTP and network failures, any connectivity issue with the other instance would abort the entire import. Both the fuzzy and exact-match calls are now wrapped in a try/except RuntimeError that falls back to an empty match list, allowing the import to continue with unmatched entries skipped.

### Improvements

* **`STATUS_COLORS` extracted to a module-level constant.** The status-to-colour mapping was defined as a local dict inside _populate_table and rebuilt on every sprint load. Moved to module level alongside `FIBONACCI` and the other colour globals; no behaviour change.
* **`_reselect_key` initialised in `__init__`.** The attribute was set ad-hoc in `_load_sprint_issues` and accessed via `getattr(self, "_reselect_key", None)` in `_on_issues_loaded`. It is now declared in `__init__` with the other instance variables, and the getattr fallback replaced with a direct attribute access.
* **CSV comment files no longer opened twice.** `_import_comments` previously read the entire file into a string before branching on extension, leaving the read result unused for CSV paths (which `_parse_comments_csv` re-opened by path internally). The two branches now each handle their own file I/O independently, eliminating the redundant read.

---

## [2.12.0] — 2026-05-18

### Features

* **CSV comment import now supports comma-separated keys in the key column.** Previously a CSV row could target at most two Jira keys via the separate key2 column. The key column now accepts any number of comma-separated keys (e.g. `PROJECT1-123`, `PROJECT2-456`, `PROJECT3-789`), each of which receives the comment. All keys are validated against the standard Jira key pattern; invalid tokens are silently skipped. The legacy key2 column (and its aliases `key_2`, `second_key`, `other_key`) continues to work as a fallback when only a single key appears in the key column, so existing CSVs require no changes.

### Improvements

* **Cross-post targets unified to a list throughout the import pipeline.** paired_key (a single string) has been replaced with paired_keys (a list) in the parsed entry dict for both the CSV and text/markdown parsers, making the data model consistent across formats. cross_map values are now lists of target keys rather than a single string, and `_post_imported_comments` iterates the list so a comment is posted to every explicit target. The import preview table and detail pane join the list with ", " for display.

---

## [2.11.9] — 2026-05-18

### Bug Fixes

* **`_parse_comments_csv` no longer silently discards read errors.** A bare `except Exception: pass` meant any file permission error, encoding failure, or malformed CSV was indistinguishable from an empty file, causing the caller to show a misleading "no valid entries found" warning. The exception is now re-raised as a `RuntimeError` and the caller shows a specific "File Error" dialog with the underlying reason.

* **`_load_sprint_issues` network and API failures now surface to the user.** The `_spawn` call had no `on_error` handler, so any exception from `get_sprint_issues` — HTTP error, network failure, or non-JSON response — fell through to the default worker error path without clearing the busy indicator. Added an explicit `on_error` handler consistent with all other spawn call sites in `MainWindow`.

* **Cross-instance JQL search errors no longer crash the comment import flow.** `_import_comments` called `other_client.search_issues_jql` directly in the main thread without error handling. Since `search_issues_jql` now raises on HTTP and network failures, any connectivity issue with the other instance would abort the entire import. Both the fuzzy and exact-match calls are now wrapped in a `try/except RuntimeError` that falls back to an empty match list, allowing the import to continue with unmatched entries skipped.

### Improvements

* **`STATUS_COLORS` extracted to a module-level constant.** The status-to-colour mapping was defined as a local dict inside `_populate_table` and rebuilt on every sprint load. Moved to module level alongside `FIBONACCI` and the other colour globals; no behaviour change.

* **`_reselect_key` initialised in `__init__`.** The attribute was set ad-hoc in `_load_sprint_issues` and accessed via `getattr(self, "_reselect_key", None)` in `_on_issues_loaded`. It is now declared in `__init__` with the other instance variables, and the `getattr` fallback replaced with a direct attribute access.

* **CSV comment files no longer opened twice.** `_import_comments` previously read the entire file into a string before branching on extension, leaving the read result unused for CSV paths (which `_parse_comments_csv` re-opened by path internally). The two branches now each handle their own file I/O independently, eliminating the redundant read.

---

## [2.11.8] — 2026-05-18

### Bug Fixes

* **`_do_save` network and API failures now surface to the user.** The `_spawn` call in `_on_save_story` had no `on_error` handler, so any exception raised during a save — network failure, HTTP error, or Jira rejection — fell through to the default worker error path without clearing the busy indicator or showing a contextual dialog. Added an explicit `on_error` handler that clears the progress indicator, updates the status bar with a failure message, and shows a critical dialog, consistent with every other spawn call in `MainWindow`.

* **`search_issues_jql` no longer silently discards errors.** The method caught all exceptions and returned an empty list, making HTTP failures and network errors indistinguishable from a genuine zero-result search. Replaced the broad `except Exception` with specific `HTTPError` and `URLError`/`OSError` handlers that raise descriptive `RuntimeError`s, consistent with the rest of `JiraClient`.

* **Hardcoded internal Jira URLs removed from settings defaults.** `SettingsDialog` initialised both instance URL fields with specific corporate hostnames as fallback defaults. These have been replaced with empty strings; fields now start blank and are populated entirely from saved `QSettings` or user input.

### Improvements

* **`_adf_to_text` recursion depth capped at 50.** The method recursed through Atlassian Document Format node trees without a depth limit, leaving it vulnerable to a stack overflow on pathologically nested content. Added a `_depth` parameter that increments on each recursive call and returns an empty string beyond depth 50.

* **`cell()` colour capture in `BulkCreateDialog._build_preview` made explicit.** The inner `cell()` function referenced `fg` from the enclosing loop scope rather than binding it at definition time. Changed the signature to `def cell(text, align=..., _fg=fg)` so the correct colour is captured regardless of when or how the function is called.

* **`ACCENT_ORG` constant renamed to `ACCENT_ORANGE`.** The name was a truncation inconsistent with all other `ACCENT_*` colour constants. Renamed across all 10 call sites; no behaviour change.

* **Dead `_on_assignees_load_error` method removed.** The method was extracted alongside `_on_boards_load_error` and `_on_issue_types_load_error` in v2.11.6, but its call site in `_refresh_users_cache` was never updated from the original inline lambda, leaving it with no callers. Removed; the inline lambda on `_refresh_users_cache` remains the active error handler.

---

## [2.11.7] — 2026-05-16

### Bug Fixes

* **`on_done` callback in `_refresh_users_cache` evaluated eagerly.** The tuple lambda `(self._busy(False), _show_dialog(members))` caused `_busy(False)` to fire immediately rather than after the fetch completed, leaving the progress bar in an incorrect state. Replaced with a named inner function that sequences the calls correctly.

* **"Open in Jira" button remained enabled after project or instance change.** The button was not included in the `_clear_sprint_view` reset, leaving it active with no issue loaded. Now disabled alongside all other edit panel controls on clear.

### Features

* **Right-click context menu added to the story table.** Right-clicking any row now offers "Open in Jira", "Copy Key", "Copy Row", and "Copy Full Issue" without requiring the story to be loaded in the edit panel first.

* **Persistent sprint label added to the story table header.** A label now shows the currently loaded project, board, and sprint above the story list, remaining visible while working in the edit panel so context is never lost.

### Improvements

* **Token expiry check now runs periodically.** Previously the check only ran on startup, meaning a token could expire silently during a long session. A `QTimer` now repeats the check every 4 hours while the app is open. 

---

## [2.11.6] — 2026-05-16
### Bug Fixes
* **Story points silently dropped on save.** If Jira rejected the story points field, the app would retry without them and report success — the user had no indication their points weren’t saved. Now surfaces a warning dialog explaining which fields were and weren’t saved.
* **Assignee dropdown cleared on empty user fetch.** If search_users returned an empty list due to a permissions issue or network hiccup, set_members would wipe the existing dropdown. The existing member list is now preserved as a fallback when the result is empty.
### Features
* **Open in Jira button added to the edit panel.** A new button in the story header opens the current issue directly in the browser using the configured Jira base URL, removing the need to manually navigate to the issue.
### Improvements
* **User list now cached per session. Previously, selecting any story triggered a full paginated search_users API call. The result is now cached on project load and reused for all subsequent story selections, clearing only on project or instance change.
* **New Story dialog user fetch moved off the main thread.** The dialog previously called search_users synchronously, freezing the UI on slow networks. It now fetches users asynchronously and opens the dialog only once the fetch completes.
* **Removed dead get_project_members method from JiraClient.** The method was made redundant in v2.11.5 when search_users was adopted everywhere, but was not removed at the time.
* **Complex error lambdas in _on_project_changed extracted into named methods.** Inline error-handling lambdas for boards, issue types, and assignees were difficult to read and test. Replaced with _on_boards_load_error, _on_assignees_load_error, and _on_issue_types_load_error.

---

## [2.11.5] - 2026-05-15
### Bug Fix
* **Removed redundant get_project_members API call on project change** — superseded by the search_users call introduced in the same update.​​​​​​​​​​​​​​​​
### Improvements
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
