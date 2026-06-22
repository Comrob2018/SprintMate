# SprintMate  ◈  v2.17.0

A Python desktop app for managing your team's Jira Data Center sprint stories — update assignees, story points, priorities, descriptions, post comments, edit and delete comments, transition statuses, attach files, archive stories, clone stories to any project or instance, import bulk comments, bulk-create stories from CSV, export sprint data, generate sprint and people reports with burndown charts, view your sprint as a Kanban board with drag-and-drop, and browse the project backlog — all from one panel.

---

## Setup

### 1. Generate your Personal Access Token

* Log in to JIRA.
* Open Profile ▶ Personal Access Tokens.
* Click Create token, give it a name, set an expiry, pick the required scopes, and Create.
* **Copy the generated token** – you'll see it only once.

### 2. Install Python

* Go to the appropriate place to get the latest version of Python.
* **If using this on a company PC, you may need to get permission — check your approved software listing or internal process.**

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **`keyring` is recommended** for secure PAT storage. If installed, tokens are stored in your OS native credential store (Windows Credential Manager, macOS Keychain, Linux Secret Service) instead of encoded in application settings. If `keyring` is not installed the app falls back to legacy storage automatically.

### 4. Run the app

```bash
python sprintmate.py
```

---

## Configuration

On first launch, click **⚙ Configure** in the top bar. SprintMate supports two Jira Data Center instances — **Primary** and **Secondary** — each configured independently. You can set a custom **Display Name** for each instance to replace the Primary/Secondary labels throughout the app.

Use the **PRIMARY / SECONDARY** toggle at the top of the settings dialog to switch between them.

| Field | Value |
|---|---|
| **Display Name** | Optional. Replaces "Primary" / "Secondary" labels throughout the app (e.g. "Production", "Staging") |
| **Jira URL** | Base URL of the instance, e.g. `https://jira.yourcompany.com` |
| **PAT Token** | Personal Access Token generated in Jira → Profile → Personal Access Tokens |
| **Token Expiry** | Optional expiry date — SprintMate will warn you when it is approaching |
| **Default Project** | Project key to auto-select on connect, e.g. `project1` |
| **Default Board** | Board name to auto-select on connect, e.g. `project1 board` |
| **Filter Projects** | Comma-separated substrings — only matching projects appear in the dropdown. Leave blank to show all. |
| **Filter Boards** | Comma-separated substrings — only matching boards appear in the dropdown. Leave blank to show all. |

Click **Test Connection** to verify credentials before saving. Click **Save** to apply.

> SprintMate will warn you in the status bar if a token has expired or is within 14 days of expiry — on launch, after saving settings, and every 4 hours while the app is running.

---

## Workflow

### Views

SprintMate has three views, switchable via the top bar buttons or keyboard shortcuts:

| View | Button | Shortcut | Description |
|---|---|---|---|
| **◈ Stories** | ◈ Stories | `Alt+1` | The main sortable/filterable story table with edit panel |
| **⊞ Kanban** | ⊞ Kanban | `Alt+2` | Drag-and-drop board with one column per status |
| **☰ Backlog** | ☰ Backlog | `Alt+3` | All open stories not assigned to any sprint |

### Navigating stories

1. On launch, the last-used instance connects automatically if credentials are saved.
2. **Select a project** from the PROJECT dropdown — boards and members auto-load.
3. **Select a board** — sprints auto-load.
4. **Select a sprint** and click **Load Stories** (or press `Ctrl+L`).
5. Use the **filter box** (top-right of the filter bar) to search live across all columns. Matching cells are highlighted.
6. **Click any story row** to open it in the edit panel on the right.

The currently loaded project, board, and sprint are shown in a label above the story table for reference while you work in the edit panel.

### Table columns

By default the table shows KEY, SUMMARY, ASSIGNEE, STATUS, and DUE DATE. **Right-click the column header** to open a toggle menu and show or hide any of the following columns: ASSIGNEE, STATUS, DUE DATE, PTS, PRIORITY, TYPE, FEATURE LINK. KEY and SUMMARY are always visible. Column visibility resets to defaults each time stories are loaded.

The table supports **click-to-sort** on any column header.

**Right-clicking any story row** opens a context menu with the following actions:

| Action | Description |
|---|---|
| **⎋ Open in Jira** | Opens the story in your browser |
| **⎘ Copy Key** | Copies the issue key to the clipboard |
| **⎘ Copy Row** | Copies the visible columns as a comma-separated line |
| **⎘ Copy Full Issue** | Copies all fields as a CSV-ready row matching the export format |
| **⎘ Copy as Markdown** | Copies the story as a Markdown-formatted block |
| **⧉ Duplicate Story** | Creates a copy of the story in the current project |
| **→ To Do / In Progress / In Review / Done / Blocked** | Transition this story (or all selected stories) to the chosen status — see [Bulk status transitions](#bulk-status-transitions) |

### Bulk status transitions

Select one or more rows in the table (hold `Shift` or `Ctrl` to multi-select), then right-click. The context menu shows either "Transition N stories to…" (for multi-selection) or single-story transition options. Click the target status to apply.

Each story's available transitions are fetched individually from Jira. After all transitions complete, a summary reports how many succeeded, how many had no matching transition available, and any errors. The sprint reloads automatically on completion.

### Editing a story

The **▶ SAVE CHANGES** button is disabled until you make a change. Fields available for editing:

| Field | Notes |
|---|---|
| **Assignee** | Picked from all users on the instance |
| **Feature Link** | URL or ID for the linked feature |
| **Issue Type** | Loaded from the project's configured types |
| **Priority** | Highest / High / Medium / Low / Lowest |
| **Story Points** | Fibonacci dropdown: 0, 1, 2, 3, 5, 8, 13, 21. Values 13 and 21 are highlighted in amber with a "consider splitting" label. |
| **Sprint** | Move the story to a different sprint on save |
| **Due Date** | Calendar picker; use Clear to remove |
| **Status Transition** | Apply a workflow transition on save |
| **Description** | Full plain-text edit |
| **Add Comment** | Optional comment posted to the story on save |

The **RECENT COMMENTS** panel shows the five most recent comments on the selected story. Each entry displays the author's name, the date, and a truncated preview in the format `[2026-06-10] Jane Smith: Comment text…`. Click **⤢ Expand** to view a comment in full. Use **✎ Edit** or **✕ Delete** to modify or remove a posted comment.

The edit panel header includes five controls:

| Control | Action |
|---|---|
| **⎘** | Copies the current issue key to the clipboard |
| **⎋ Open in Jira** | Opens the current story in your browser |
| **⎘ Clone** | Clone this story to a project or instance |
| **📎 Attach File** | Opens a file picker to attach one or more files to the current story |

Click **▶ SAVE CHANGES** (or press `Ctrl+S`) — the app updates Jira and re-selects the saved story automatically.

> If Jira rejects the story points field on save (e.g. because it is read-only for the issue type), a warning dialog will explain that all other changes were saved but points were not.

> If you attempt to reload stories or close the app while there are unsaved changes in the edit panel, SprintMate will prompt you before discarding them. It will also warn if background operations are still in flight when you close.

### Inline editing

You can update story points and assignee directly from the table without opening the full edit panel:

- **Double-click the PTS cell** — a Fibonacci combo pop-up appears. Select a new value and click **Save**. The change is written to Jira immediately and the sprint reloads.
- **Double-click the ASSIGNEE cell** — a team-member combo pop-up appears. Select a new assignee (or "— Unassigned —") and click **Reassign**. The change is written to Jira immediately and the sprint reloads.

### Creating a story

Click **＋ New Story** (or press `Ctrl+N` or the `N` key with the table focused) in the filter bar to open the creation dialog. Fill in summary (required), issue type, priority, story points, assignee, sprint, due date, and description, then click **＋ Create Story**.

The story points dropdown includes: 0, 1, 2, 3, 5, 8, 13, 21. Values 13 and 21 are highlighted in amber with a "consider splitting" label.

### Bulk-creating stories from CSV

Click **＋＋ Bulk Create** in the filter bar to create multiple stories at once from a CSV file.

**CSV format — header row required, column order does not matter:**

```
summary,issue_type,priority,story_points,assignee,sprint,due_date,description
```

| Column | Required | Notes |
|---|---|---|
| `summary` | **Yes** | Rows with a blank summary are skipped |
| `issue_type` | No | Falls back to the first available type if blank or unrecognised |
| `priority` | No | Highest / High / Medium / Low / Lowest — defaults to Medium |
| `story_points` | No | Integer; left unset if blank or invalid |
| `assignee` | No | Display name, matched case-insensitively; left unassigned if not found |
| `sprint` | No | Sprint name, matched case-insensitively; left unassigned if not found |
| `due_date` | No | `yyyy-MM-dd` format; defaults to today if blank or invalid |
| `description` | No | Plain text |

A preview dialog shows all parsed rows with their resolved values and any warnings (unknown assignee, unrecognised type, etc.) before anything is posted. Invalid rows (missing summary) are highlighted and excluded from creation. Click **▶ Create Stories** to proceed.

### Switching instances

Click **⇄ Switch Instance** in the top bar to toggle between Primary and Secondary without opening settings. The app swaps credentials, clears the current view, and reloads projects automatically. A warning is shown if the target instance has no saved credentials.

### Importing comments

Click **📄 Import** (or press `Ctrl+I`) to bulk-post comments from a text, Markdown, or CSV file.

**Text / Markdown format — one entry per line:**

```
KEY-123 - Task Summary - Assignee Name: Comment text here
KEY-456 | Another Task | Jane Smith: Another comment here
```

Accepted field separators: `-`, `|`, `~`, `;`

**CSV format — header row required:**

```
key,summary,assignee,comment
```

A preview dialog shows all parsed entries with their match status before anything is posted:

- **Matched** entries (key found in the current sprint) are posted to the active instance.
- **Unmatched** entries are skipped.
- **Cross-post** — if a story with the same summary and assignee is found on the other instance, the comment is posted there too. Cross-post targets are highlighted in cyan in the preview.

Progress is shown per-comment in the progress bar. Any failures are reported in the status bar at completion without aborting the rest of the batch.

### Cloning a story

Click **⎘ Clone** in the edit panel header to open the clone dialog. The dialog has three sections:

- **Target Instance** — defaults to the current instance. If the other instance has saved credentials, it appears as a second option.
- **Target Project** — a dropdown populated from the selected instance's project list, sorted alphabetically.
- **Fields to clone** — Summary (pre-filled as `[Clone] Original summary`), Description, and Assignee, all editable before committing.

Click **⎘ Clone** to create the issue. On success, a dialog shows the new issue key with **Copy Key** and **Open in Jira** action buttons.

### Attaching files to a story

Click **📎 Attach File** in the edit panel header to upload one or more files directly to the current Jira issue. A file picker opens that accepts any file type and allows selecting multiple files at once. Each file is uploaded via the Jira REST API — a single failure does not stop the rest of the batch.

### Archiving stories

Click **🗄 Archive** in the filter toolbar (enabled once stories are loaded) to archive one or more stories. A searchable, sortable picker dialog lists all stories in the sprint. Check the stories to archive and click **🗄 Archive Selected**. A confirmation dialog explains the consequences before anything is sent.

You can also press **Delete** with a story selected in the table to quick-archive it with a single confirm prompt.

Archived issues become read-only and are removed from boards, backlogs, and search results. All data is preserved and issues can be restored from Jira administration. Requires Jira Data Center 8.1 or later.

### Editing and deleting comments

The RECENT COMMENTS panel includes two additional buttons when a story with comments is loaded:

- **✎ Edit** — opens a pre-filled text editor. If the story has more than one comment, a picker dialog lets you choose which one to edit.
- **✕ Delete** — shows a preview in a confirmation dialog before permanently deleting. Jira's permission rules apply — you can only delete comments you authored unless you have admin rights.

Both actions reload the story immediately so the comment panel reflects the change.

### Generating a sprint report

Click **📊 Sprint Report** in the filter toolbar to open the report dialog. The dialog has two tabs.

**Sprint Report tab** — choose a scope then click **▶ Generate Sprint Report**:

- **Sprint** — select any sprint from the dropdown (pre-selected to the currently loaded sprint).
- **Date Range** — enter From and To dates in `YYYY-MM-DD` format to fetch all issues updated within that window.

The report includes stat cards (total stories, done count, total/done points, velocity %), a **burndown chart** showing ideal vs. actual remaining points across the sprint, a status breakdown table, a per-assignee summary with progress bars, and a full story table with keys hyperlinked to Jira. Overdue due dates are highlighted in red; dates within 3 days are highlighted in amber.

**People Report tab** — generate an instance-wide report filtered by person:

- **Scope** — choose a sprint or a date range.
- **People** — multi-select from the list of assignees on the current sprint, and/or type additional usernames (comma-separated) in the free-text box.

The People Report shows a summary comparison table (stories, done, story progress, total points, done points, points progress, average cycle time, status breakdown per person), followed by a per-person detail section.

Both reports can be saved as HTML via **⬇ Save as HTML**.

### Kanban board

Click **⊞ Kanban** in the top bar (or press `Alt+2`) to switch to the Kanban board view. Stories are displayed as cards in five columns: **To Do**, **In Progress**, **In Review**, **Done**, and **Blocked**.

Each card shows the issue key, summary, assignee, and story points. The left border colour corresponds to the story's status.

**Drag a card** to a different column to trigger a Jira status transition. The app fetches available transitions for that issue, applies the matching one, and refreshes the board. If no matching transition is available, an error is shown and the card returns to its original column.

**Click a card** to switch back to the Stories tab with that story selected in the table.

Stories with statuses not in the five canonical columns are placed in **To Do** and noted in the board status bar.

The board is populated automatically when you switch to it (if stories are already loaded) and refreshes after any drag-and-drop transition.

### Backlog view

Click **☰ Backlog** in the top bar (or press `Alt+3`) to switch to the Backlog view. Click **↺ Load Backlog** to fetch all open issues for the current project that have no sprint assigned (`sprint is EMPTY AND statusCategory != Done`).

Results display in a sortable, filterable table with columns for KEY, SUMMARY, ASSIGNEE, PRIORITY, PTS, TYPE, and DUE DATE. Use the filter box at the top to search live across all columns.

Clicking a backlog story that is also present in the currently loaded sprint switches to the Stories tab and selects that row.

### Exporting stories

Click **⬇ Export** (or press `Ctrl+E`) to export the current sprint's stories to a CSV file. You can choose to export all stories or select specific ones using a basket-style picker.

The exported CSV includes:

```
key, summary, assignee, status, issue_type, priority, story_points,
feature_link, due_date, sprint, description, comments
```

Comments are exported as a pipe-separated list in the format `[Author]: body text`.

---

## Keyboard Shortcuts

### Global

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save changes (when save button is enabled) |
| `Ctrl+N` | New Story |
| `Ctrl+L` | Load Stories |
| `Ctrl+I` | Import Comments |
| `Ctrl+E` | Export Stories |
| `Ctrl+F` | Focus the filter/search box |
| `Ctrl+Shift+C` | Copy full issue as a CSV-ready row |
| `Ctrl+Shift+M` | Copy selected row as Markdown |
| `Alt+1` | Switch to Stories view |
| `Alt+2` | Switch to Kanban view |
| `Alt+3` | Switch to Backlog view |

### Table (when the story table has focus)

| Shortcut | Action |
|---|---|
| `N` | New Story |
| `R` | Refresh (reload current sprint) |
| `S` | Save changes |
| `Escape` | Clear table selection |
| `Delete` | Quick-archive the selected story (with confirm prompt) |
| `↑` / `↓` | Navigate to previous / next story row |
| `Ctrl+↑` / `Ctrl+↓` | Navigate to previous / next story row |
| `Ctrl+C` | Copy visible columns of the selected row (comma-separated) |

---

## Top Bar

| Button | Action |
|---|---|
| **⚙ Configure** | Open the settings dialog |
| **⇄ Switch Instance** | Toggle between Primary and Secondary |
| **↺ Refresh** | Reload the current sprint |
| **◈ Stories** | Switch to the Stories table view |
| **⊞ Kanban** | Switch to the Kanban board view |
| **☰ Backlog** | Switch to the Backlog view |

---

## User Guide

### How to set up and connect for the first time

1. Install dependencies with `pip install -r requirements.txt`, then run `python sprintmate.py`.
2. Click **⚙ Configure** in the top bar.
3. Use the **PRIMARY / SECONDARY** toggle to select the instance you want to set up first.
4. Enter the **Jira URL** and your **PAT Token**. Optionally set a **Token Expiry** date, a **Default Project**, and a **Default Board** so the app pre-selects them on every launch.
5. Click **Test Connection** — you should see a green "Connected as …" confirmation.
6. Click **Save**. Repeat steps 3–5 for the other instance if needed.
7. The app will connect automatically and load your projects. Select a project, board, and sprint, then click **Load Stories**.

---

### How to edit and save a story

1. Load a sprint (see above).
2. Click any row in the table to open it in the edit panel on the right.
3. Change any fields you need — assignee, priority, story points, due date, description, etc.
4. Optionally select a **Status Transition** to move the story through its workflow, and/or type a comment in **Add Comment**.
5. Press `Ctrl+S` or click **▶ SAVE CHANGES**. The story is updated in Jira and the table refreshes automatically.

---

### How to quickly update story points or assignee

1. Load a sprint.
2. Make sure the PTS or ASSIGNEE column is visible (right-click any column header to toggle it on).
3. **Double-click the PTS cell** to open a Fibonacci selector, or **double-click the ASSIGNEE cell** to open a team-member selector.
4. Make your selection and click **Save** / **Reassign**. The change is written to Jira and the sprint reloads — no need to open the full edit panel.

---

### How to update multiple stories quickly

1. Load a sprint.
2. Use the **filter box** (`Ctrl+F`) to narrow the table to the stories you want.
3. Click the first story, make your changes, and press `Ctrl+S`.
4. Click the next story in the table and repeat. Or use `↑` / `↓` to navigate rows and `S` to save.

---

### How to transition multiple stories at once

1. Load a sprint.
2. Select the stories to transition — click the first row, then `Shift`+click or `Ctrl`+click additional rows.
3. Right-click and choose a status from the **"Transition N stories to…"** section of the context menu.
4. SprintMate applies the matching Jira transition to each story and reports a summary on completion.

---

### How to move a story to a different sprint

1. Click the story in the table to open it in the edit panel.
2. In the **Sprint** dropdown (under STORY FIELDS), select the destination sprint.
3. Press `Ctrl+S` or click **▶ SAVE CHANGES**. The story disappears from the current sprint view after the table refreshes.

---

### How to use the Kanban board

1. Load a sprint.
2. Click **⊞ Kanban** in the top bar (or press `Alt+2`).
3. Stories appear as cards in their current status column.
4. **Drag a card** to a new column to trigger a Jira status transition.
5. **Click a card** to jump back to the Stories tab with that story selected.

---

### How to browse the backlog

1. Select a project and board (stories don't need to be loaded first).
2. Click **☰ Backlog** in the top bar (or press `Alt+3`).
3. Click **↺ Load Backlog** to fetch all unsprinted open stories for the current project.
4. Use the filter box to search, or click any column header to sort.
5. Click a story to select it — if it also exists in the active sprint, the app switches to the Stories tab and highlights it.

---

### How to bulk-create stories from a spreadsheet

1. Prepare a CSV file with a header row. The only required column is `summary`; all others are optional:
   ```
   summary,issue_type,priority,story_points,assignee,sprint,due_date,description
   ```
2. Load a sprint so that issue types, members, and sprints are available for validation.
3. Click **＋＋ Bulk Create** and select your CSV file.
4. Review the preview dialog — each row shows its resolved values and any warnings. Rows with a blank summary are highlighted and will be skipped.
5. Click **▶ Create Stories**.

---

### How to export a sprint to CSV

1. Load the sprint you want to export.
2. Click **⬇ Export** (or press `Ctrl+E`).
3. Choose **Yes** to export all stories, or **No** to open the selection picker.
4. Choose a save location — the filename is pre-filled based on the project, board, sprint, and today's date.

---

### How to import comments in bulk

1. Prepare a file with one comment per entry (text/Markdown or CSV format — see [Importing comments](#importing-comments) above).
2. Load the sprint that contains the stories you want to comment on.
3. Click **📄 Import** (or press `Ctrl+I`) and select your file.
4. Review the preview dialog and click **OK** to post.

---

### How to clone a story

1. Load a sprint and click the story you want to clone.
2. Click **⎘ Clone** in the edit panel header.
3. Select a target instance and target project.
4. Review and edit the summary, description, and assignee as needed.
5. Click **⎘ Clone**. On success, a dialog shows the new issue key with options to **Copy Key** or **Open in Jira**.

---

### How to attach a file to a story

1. Load a sprint and click the story you want to attach a file to.
2. Click **📎 Attach File** in the edit panel header.
3. Select one or more files in the file picker — any file type is accepted.
4. SprintMate uploads each file to the Jira issue and reports success or failure per file.

---

### How to archive stories

1. Load the sprint containing the stories you want to archive.
2. Either:
   - Click **🗄 Archive** in the filter toolbar, tick the stories to archive, and click **🗄 Archive Selected**; or
   - Select a single story in the table and press **Delete** for a quick confirm-and-archive.
3. Archived stories are removed from the sprint view immediately.

---

### How to edit or delete a posted comment

1. Click the story whose comment you want to change.
2. In the **RECENT COMMENTS** panel, click **✎ Edit** or **✕ Delete**.
3. If the story has more than one comment, a picker dialog appears — select the comment you want to act on.
4. **Edit** — modify the text and click **Save Comment**. **Delete** — review the preview and click **Yes**.
5. The story reloads automatically.

---

### How to generate a sprint report

1. Load a sprint and click **📊 Sprint Report** in the filter toolbar.
2. Select a scope — choose a sprint from the dropdown or switch to Date Range.
3. Click **▶ Generate Sprint Report**. The report renders with stat cards, a burndown chart, status breakdown, assignee summary, and a full story table.
4. Optionally click **⬇ Save as HTML** to save to a file.

---

### How to generate a people report

1. Load a sprint and click **📊 Sprint Report** in the filter toolbar.
2. Switch to the **👤 People Report** tab.
3. Select a scope — a sprint or date range.
4. Select people from the list and/or type additional usernames in the free-text box.
5. Click **▶ Generate People Report**. Optionally click **⬇ Save as HTML**.

---

### How to set a custom instance display name

1. Click **⚙ Configure** in the top bar.
2. Select the instance using the **PRIMARY / SECONDARY** toggle.
3. Enter a name in the **Display Name** field (e.g. "Production", "Staging").
4. Click **Save**. The name replaces "Primary" / "Secondary" everywhere in the app. Leave it blank to revert to the default label.

---

### How to switch between instances

1. Click **⇄ Switch Instance** in the top bar at any time.
2. The app swaps to the other instance, clears the current view, and reloads your projects automatically.
3. If the target instance has no saved credentials, you will be prompted to configure it first.

---

### How to copy a story to the clipboard

- **`Ctrl+C`** (with the table focused) — copies the visible columns of the selected row as a comma-separated line.
- **`Ctrl+Shift+C`** — copies the full story as a CSV-ready row matching the export format.
- **`Ctrl+Shift+M`** — copies the selected row as a Markdown-formatted block.
- The **⎘** button in the edit panel header copies just the issue key (e.g. `PROJECT1-123`).

---

## Notes

- The app targets **Jira Data Center** exclusively and uses the **REST API v2** and the **Agile API v1.0** for boards and sprints.
- All API calls run on background threads — the UI stays responsive during loads. A maximum of 5 background operations can run concurrently.
- Settings (URLs, default project/board, token expiry, project/board filters) are stored via `QSettings` (registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). PAT tokens are stored in the OS keychain when `keyring` is available.
- On first save with `keyring` present, any token previously stored as base64 in QSettings is automatically migrated to the keychain and the legacy entry is removed.
- The Kanban board is populated from the currently loaded sprint — switch to Stories, load a sprint, then switch to Kanban.
- The Backlog view fetches stories with `sprint is EMPTY AND statusCategory != Done`. Stories that are Done but unsprinted (e.g. subtasks closed outside a sprint) are excluded by design.
- Archiving requires Jira Data Center 8.1 or later.
