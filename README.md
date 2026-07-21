# SprintMate  ◈  v2.27.1

A Python desktop app for managing your team's Jira Data Center sprint stories — update assignees, story points, priorities, descriptions, post comments, edit and delete comments, transition statuses, attach files, archive stories, clone stories to any project or instance, import bulk comments, bulk-create or bulk-edit stories, export sprint data, generate professional sprint and people reports with burndown charts, view your sprint as a Kanban board with drag-and-drop, browse and groom the project backlog, track velocity history across sprints, and create, start, rename, and close sprints — all from one panel.

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

> The velocity history chart requires `PyQt6-Qt6-Svg` for SVG rendering. Install it with `pip install PyQt6-Qt6-Svg`. If it is not present, a text prompt will be shown instead of the chart.

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

SprintMate has four views, switchable via the top bar buttons or keyboard shortcuts:

| View | Button | Shortcut | Description |
|---|---|---|---|
| **◈ Stories** | ◈ Stories (N) | `Alt+1` | The main sortable/filterable story table with edit panel — tab shows story count when loaded |
| **⊞ Active Sprint** | ⊞ Active Sprint | `Alt+2` | Drag-and-drop board with one column per status |
| **☰ Backlog** | ☰ Backlog | `Alt+3` | All open stories not assigned to any sprint |
| **📊 Reports** | 📊 Reports | `Alt+4` | Sprint report, people report, velocity history, and sprint compare |

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

Each story's available transitions are fetched individually from Jira. SprintMate uses a fuzzy matching strategy to find the right transition — exact status name first, then starts-with, then contains, then transition name match — so non-standard Jira workflow names (e.g. "Start Progress" for an "In Progress" target) are handled automatically. If no match is found at all, the error message lists every available transition for that issue.

After all transitions complete, a summary reports how many succeeded, how many had no matching transition, and any errors. The sprint reloads automatically on completion.

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

The edit panel header includes the following controls:

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

You can update four fields directly from the table without opening the full edit panel:

- **Double-click the PTS cell** — a Fibonacci combo pop-up appears. Select a new value and click **Save**. The change is written to Jira immediately and the sprint reloads.
- **Double-click the ASSIGNEE cell** — a team-member combo pop-up appears. Select a new assignee (or "— Unassigned —") and click **Reassign**. The change is written to Jira immediately and the sprint reloads.
- **Double-click the STATUS cell** — a combo of the issue's available Jira transitions appears. Select one and click **Apply** to transition the issue immediately.
- **Double-click the DUE DATE cell** — a calendar date-picker appears. Click **Save** to update the date, or **Clear Date** to remove it entirely.

All four inline edits write directly to Jira and reload the sprint on confirmation.

### Story ranking

The quick-add bar below the stories table includes **↑ Rank Up** and **↓ Rank Down** buttons. With a story selected in the table, clicking either moves it one position relative to its neighbour by calling `PUT /rest/agile/1.0/issue/rank`. The sprint reloads after a successful rank change.

If the board's ranking field is not writable (e.g. it uses a manual or external ranking scheme), a dialog explains the reason rather than failing silently.

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

A preview dialog shows all parsed rows with their resolved values and any warnings before anything is posted. Click **▶ Create Stories** to proceed.

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

### Reports tab

Click **📊 Reports** in the top bar (or press `Alt+4`) to open the Reports tab. All reporting features are consolidated here and render inline — no separate dialog windows.

The Reports toolbar contains:

| Control | Action |
|---|---|
| **SPRINT** dropdown | Select which sprint to report on (pre-filled with all board sprints; active sprint pre-selected) |
| **📊 Sprint Report** | Switch to Sprint Report sub-tab (select sprint or date range, then click ▶ Generate) |
| **👤 People Report** | Switch to People Report sub-tab (select sprint or date range, choose people, then click ▶ Generate) |
| **📈 Velocity** | Generate the velocity history bar chart and table |
| **📉 Burndown** | Generate a standalone burndown chart for the active sprint |
| **COMPARE** dropdown + **⇆ Compare** | Compare the loaded sprint against another sprint |
| **⬇ Save HTML** | Save the currently displayed report to an HTML file (enabled after generation) |

Each button switches to its own sub-tab and generates into it. Sub-tabs persist their content — switching between them does not lose a generated report. The **⬇ Save HTML** button always saves whichever sub-tab is currently visible.

**📊 Sprint Report** — each sub-tab has its own scope bar. Choose **Sprint** to select any sprint from the dropdown, or **Date Range** and enter From / To dates. Click **▶ Generate** to run the report. The report itself is a full dashboard HTML with a dark header, stat cards (including a circular velocity ring), a burndown chart with an ahead/behind callout, a proportional status stacked bar, a team card grid with per-person progress bars, and a story table with sticky headers, status badges, and overdue row highlighting.

**👤 People Report** — the sub-tab scope bar offers **Sprint** or **Date Range** selection, a multi-select people list (populated from the sprint's assignees, all selected by default), and an extra usernames field for people not in the current sprint. Click **▶ Generate**. The report shows a per-assignee summary table (stories, done, story progress, total points, done points, points progress, status breakdown) followed by a per-person detail section.

**📈 Velocity** — a native SVG bar chart (committed vs completed per sprint, scales with the window) above a summary table of the last 8 closed sprints. Requires `PyQt6-Qt6-Svg` for the chart; the table is always available.

**📉 Burndown** — a standalone burndown chart for the active sprint, showing the ideal line vs actual remaining points with an ahead/behind callout. Below the chart, a stat strip shows total points, done, remaining, completion %, and stories done. The burndown inside Sprint Report is unchanged — this sub-tab gives it a dedicated view.

**⇆ Compare** — after comparing, results render here as an HTML summary with added/changed/removed stat pills and a colour-coded diff table. SprintMate switches to this sub-tab automatically after the comparison completes.

All reports can be saved as HTML via **⬇ Save HTML**. The sprint report HTML includes print CSS for clean printing or PDF export from the browser.

**Finding text in a report** — press `Ctrl+F` while on the Reports tab to open a find bar at the bottom. Type to search, use ▲ / ▼ to move between matches, and press `Escape` or click ✕ to close. Available on all HTML-based sub-tabs (Sprint Report, People Report, Compare, Burndown).

### Command palette

Press `Ctrl+K` anywhere in the app to open the command palette. Type to fuzzy-search across all 22 available actions — loading, creating, editing, switching views, generating reports, and more. Use `↑` / `↓` to navigate the list, `Enter` to run the selected command, and `Escape` to dismiss.

---

### Command palette

Press `Ctrl+K` anywhere in the app to open the command palette. Type to fuzzy-search across all 22 available actions — loading, creating, editing, switching views, generating reports, and more. Use `↑` / `↓` to navigate, `Enter` to run, `Escape` to dismiss.

---

### Sprint progress bar

A 4px coloured bar sits directly below the story count row, visible whenever a sprint is loaded. It reflects the percentage of story points completed:

- **Green** — 80% or more done
- **Amber** — 40–79% done  
- **Red** — under 40% done

Hovering the bar shows "X of Y pts done (Z%) · N of M stories done". The bar hides when the sprint view is cleared.

### Column persistence

Visible column preferences are saved per board. Once you toggle columns on or off for a board, SprintMate remembers them and restores the same layout the next time you load stories from that board. Right-click any column header to change which columns are visible.

### Bulk editing stories

Click **✎ Bulk Edit** in the Stories toolbar (enabled when stories are loaded) to edit multiple stories at once. Select the stories you want to change first (hold `Shift` or `Ctrl` to multi-select), then click Bulk Edit. The dialog has three fields — Assignee, Priority, and Story Points — all defaulting to "No change". Only fields you explicitly set are updated. A summary reports successes and failures per story.

### Story hover preview

Hovering over the KEY or SUMMARY cell of any story row shows a tooltip with the description excerpt (up to 140 characters) and the most recent comment with the author's name. This lets you check context without clicking into the full edit panel.

### Recent stories

A **🕐** button in the quick-add bar below the story table opens a popup menu of the last 10 story keys you viewed, with their summaries. Clicking any entry scrolls the table to that story and selects it. A "Clear history" item at the bottom resets the list.

### Duplicate detection

When typing in the quick-add bar, SprintMate checks whether a similar story already exists in the sprint before creating it. If more than 60% of the words in the summary match an existing story, a dialog lists the matches and asks you to confirm before proceeding.

### Story links panel

When a story has Jira issue links (blocks / is blocked by / relates to), a read-only **LINKED ISSUES** panel appears in the edit panel below the comments section. It shows the relationship type, linked issue key, status, and a summary excerpt. The panel is hidden when there are no links.

### Keyboard shortcut reference

Click the **?** button in the toolbar or press `?` anywhere in the app to open the keyboard shortcut reference card. It lists all shortcuts grouped into Global, Table (when focused), and Inline editing sections.

Select a sprint in the **Compare** dropdown in the filter toolbar and click **Compare**. SprintMate highlights rows that have changed (blue background) or are new since the comparison sprint (green background). Hovering the KEY cell shows a tooltip with a summary of what changed (status, assignee, story points).

After the comparison completes, SprintMate offers to export the diff as a CSV. The export includes one row per changed, added, or removed story with columns for key, change_type, and diffs. You can also trigger the export manually from the prompt that appears.

### Managing sprints

Click **⊕ Sprint** in the filter toolbar (enabled once a board is loaded) to open the Sprint Manager dialog. It has two tabs.

**＋ Create tab** — fill in a sprint name (required), optional goal, start date, and end date. Choose whether to create the sprint as a future sprint or to create-and-start it immediately, then click **＋ Create Sprint**. Status is shown inline.

**⚙ Manage tab** — select any sprint from the board in the dropdown. Its current name, goal, and dates are pre-filled. Three actions are available:

| Button | Action | When available |
|---|---|---|
| **💾 Save Changes** | Rename, reschedule, or update the sprint goal | Always |
| **▶ Start Sprint** | Starts the sprint (confirms dates; warns that only one sprint can be active at a time) | Future sprints only |
| **■ Close Sprint** | Closes the sprint (confirms that incomplete stories remain on the board) | Active sprints only |

After any successful operation the sprint dropdown in the main window reloads automatically so the new state is reflected immediately.

> Starting a sprint requires **Manage Sprints** permission on the board. Only one sprint can be active per board at a time — Jira enforces this. If another sprint is already active, the start will fail with a clear error message.

### Kanban board

Click **⊞ Active Sprint** in the top bar (or press `Alt+2`) to switch to the active sprint board view. The board heading and tab label both reflect the loaded sprint name (e.g. `⊞  Sprint 42`). They reset to `⊞  ACTIVE SPRINT` when no sprint is loaded.

**Loading from the Kanban tab** — if no stories are loaded yet, a compact load toolbar appears at the top of the board with PROJECT, BOARD, and SPRINT dropdowns and a **↺ Load** button. The dropdowns are pre-filled to match whatever is selected on the Stories tab. Select a sprint and click **↺ Load** to populate the board directly, without switching to the Stories tab first. The toolbar auto-hides once stories are loaded.

Stories are displayed as cards in five columns: **To Do**, **In Progress**, **In Review**, **Done**, and **Blocked**. Each card shows the issue key, summary, assignee, and story points. The left border colour corresponds to the story's status.

**Filtering** — a filter bar sits below the board header with three controls that work together in real time:

| Control | Filters by |
|---|---|
| Text search | Issue key or summary substring |
| Assignee | Team member (populated from loaded issues; selection preserved on refresh) |
| Priority | Highest / High / Medium / Low / Lowest |

A **✕ Clear** button resets all three at once. A "Showing N of M" label appears whenever any filter is active.

**Drag a card** to a different column to trigger a Jira status transition. SprintMate uses fuzzy matching to find the correct transition — see [Bulk status transitions](#bulk-status-transitions) for the matching logic. If no match is found, the error message lists all available transitions and the card stays in its original column.

**Click a card** to switch back to the Stories tab with that story selected in the table.

The board header includes a **＋ New Story** button that opens the same story creation dialog as the Stories tab.

The board is populated from the currently loaded sprint and persists between tab switches — navigating away and back does not rebuild the cards unless the sprint data has changed.

### Backlog view

Click **☰ Backlog** in the top bar (or press `Alt+3`) to switch to the Backlog view.

A load bar at the top of the tab contains PROJECT and BOARD dropdowns and a **↺ Load Backlog** button. The dropdowns are pre-filled to match whatever is selected on the Stories tab. Select a project and board, then click **↺ Load Backlog** to fetch all open issues that have no sprint assigned. The load bar works the same way as the Active Sprint board's load toolbar — you can load a backlog without visiting the Stories tab first.

Results display in a sortable, filterable table with columns for KEY, SUMMARY, ASSIGNEE, PRIORITY, PTS, TYPE, and DUE DATE. Use the filter box at the top to search live across all columns. Epics and sub-tasks are excluded — the backlog only shows stories, bugs, tasks, and other sprint work items.

**Right-clicking any row** opens a context menu. Menu items adapt for single vs multi-selection:

| Action | Single selection | Multi-selection |
|---|---|---|
| **⎋ Open in Jira** | Opens the issue in your browser | Disabled |
| **⎘ Copy Key** | Copies the key to the clipboard | Copies N keys comma-separated |
| **⇧ Move to Sprint** | Moves the story to the selected sprint | Moves all selected stories |

**Move to Sprint** — you can also select one or more backlog stories, choose a target sprint from the dropdown (the active sprint is pre-selected), and click **⇧ Move**. Moved stories are removed from the backlog table immediately.

**Export CSV** — click **⬇ Export CSV** to save all loaded backlog items to a CSV file (key, summary, assignee, priority, story points, issue type, due date).

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
| `Alt+2` | Switch to Active Sprint board view |
| `Alt+3` | Switch to Backlog view |
| `Alt+4` | Switch to Reports tab |
| `Ctrl+K` | Open command palette |
| `Ctrl+K` | Open command palette |
| `?` | Open keyboard shortcut reference card |

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
| **⊞ Active Sprint** | Switch to the active sprint board view |
| **☰ Backlog** | Switch to the Backlog view |
| **📊 Reports** | Switch to the Reports tab (sprint report, people report, velocity, compare) |
| **⊕ Sprint** | Open the Sprint Manager (create, start, rename, close) |
| **✎ Bulk Edit** | Bulk-edit assignee, priority, or story points for selected stories |

---

## User Guide

### How to set up and connect for the first time

1. Install dependencies with `pip install -r requirements.txt`, then run `python sprintmate.py`.
2. Click **Menu → Configure…** in the menu bar.
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

### How to quickly update a field inline

1. Load a sprint.
2. Make sure the column you want to edit is visible (right-click any column header to toggle columns).
3. **Double-click the cell** for the field you want to change:
   - **PTS** — Fibonacci combo; click **Save**.
   - **ASSIGNEE** — team-member combo; click **Reassign**.
   - **STATUS** — available transitions combo; click **Apply**.
   - **DUE DATE** — calendar picker; click **Save** or **Clear Date**.
4. The change is written to Jira immediately and the sprint reloads.

---

### How to re-rank a story

1. Load a sprint.
2. Click the story you want to move in the table.
3. Click **↑ Rank Up** or **↓ Rank Down** in the bar below the table.
4. The sprint reloads with the updated order. If the board doesn't support ranking, a dialog will explain why.

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
4. SprintMate applies the best-matching Jira transition to each story and reports a summary on completion.

---

### How to move a story to a different sprint

1. Click the story in the table to open it in the edit panel.
2. In the **Sprint** dropdown (under STORY FIELDS), select the destination sprint.
3. Press `Ctrl+S` or click **▶ SAVE CHANGES**. The story disappears from the current sprint view after the table refreshes.

---

### How to bulk-edit multiple stories

1. Load a sprint.
2. Select the stories to edit — click the first row, then `Shift`+click or `Ctrl`+click additional rows.
3. Click **✎ Bulk Edit** in the toolbar.
4. Set any combination of Assignee, Priority, or Story Points. Fields left at "No change" are untouched.
5. Click **Apply to All**. A summary reports how many were updated and any failures.

---

### How to use the active sprint board

1. Click **⊞ Active Sprint** in the top bar (or press `Alt+2`).
2. If no stories are loaded, a load toolbar appears. Select a project, board, and sprint, then click **↺ Load**. If stories are already loaded from the Stories tab, the board populates immediately.
3. The tab and board heading show the sprint name.
4. **Filter cards** using the filter bar: type in the search box to match by key or summary, choose an assignee, or choose a priority. All three filters work together in real time. Click **✕ Clear** to reset.
5. **Drag a card** to a new column to trigger a Jira status transition.
6. **Click a card** to jump back to the Stories tab with that story selected.
7. Use **＋ New Story** in the board header to create a story without leaving the board.

---

### How to view recently visited stories

Click the **🕐** button in the quick-add bar below the story table. A popup menu shows the last 10 stories you viewed with their summaries. Click any entry to jump to it. Click "Clear history" to reset the list.

---

### How to open the keyboard shortcut reference

Press `?` anywhere in the app, or click the **?** button in the toolbar. A scrollable dialog lists all shortcuts grouped into Global, Table, and Inline editing sections.

---

### How to browse and groom the backlog

1. Click **☰ Backlog** in the top bar (or press `Alt+3`).
2. In the load bar at the top, select a PROJECT and BOARD (pre-filled from the Stories tab).
3. Click **↺ Load Backlog** to fetch all unsprinted open stories for the selected project.
4. Use the filter box to search, or click any column header to sort.
5. **Right-click any row** for quick actions: Open in Jira, Copy Key, or Move to Sprint.
6. To move stories into a sprint: select one or more rows, choose a sprint from the **Move to sprint** dropdown, and click **⇧ Move** (or use the right-click menu).
7. To export the backlog: click **⬇ Export CSV**.
8. Clicking a story that also exists in the active sprint switches to the Stories tab and highlights it.

---

### How to view velocity history

1. Load a sprint (so the board ID is known).
2. Click **📈 Velocity** in the Stories toolbar.
3. Select the number of sprints to include (3–10) and click **▶ Load**.
4. The dialog shows a bar chart of committed vs completed points per sprint and a summary table.
5. Click **⬇ Export CSV** to save the data.

---

### How to compare sprints and export the diff

1. Click **📊 Reports** in the top bar (or press `Alt+4`).
2. In the Reports toolbar, choose a sprint from the **COMPARE** dropdown and click **⇆ Compare**.
3. Changed rows are highlighted blue; new rows are highlighted green. Hover any KEY cell for a tooltip showing what changed.
4. When the comparison finishes, SprintMate offers to export the diff as CSV. Accept to save, or dismiss to skip.

---

### How to create a sprint

1. Select a project and board.
2. Click **⊕ Sprint** in the filter toolbar.
3. Switch to the **＋ Create** tab.
4. Enter a sprint name, optional goal, start date, and end date.
5. Choose **Create as future sprint** or **Create and immediately start**.
6. Click **＋ Create Sprint**. The sprint dropdown reloads automatically.

---

### How to start, rename, or close a sprint

1. Select a project and board.
2. Click **⊕ Sprint** in the filter toolbar.
3. Switch to the **⚙ Manage** tab and select the sprint from the dropdown.
4. To rename or reschedule: edit the name, goal, or dates and click **💾 Save Changes**.
5. To start a future sprint: click **▶ Start Sprint**, confirm the dates and the warning, then click **Yes**.
6. To close an active sprint: click **■ Close Sprint**, confirm that incomplete stories will remain on the board, then click **Yes**.
7. The sprint dropdown reloads after each successful action.

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

1. Click **📊 Reports** in the top bar (or press `Alt+4`).
2. Click **📊 Sprint Report** or switch to the **📊 Sprint Report** sub-tab.
3. In the scope bar, choose **Sprint** and select a sprint from the dropdown, or choose **Date Range** and enter From / To dates.
4. Click **▶ Generate**. The report renders inline with a dark header, stat cards, burndown chart, status stacked bar, team card grid, and full story table.
5. Click **⬇ Save HTML** to save the report to a file. The exported HTML includes print CSS for clean printing or PDF export from the browser.

---

### How to view the burndown chart

1. Load a sprint.
2. Click **📊 Reports** in the top bar (or press `Alt+4`).
3. Click **📉 Burndown**. The chart renders in its own sub-tab showing the ideal vs actual burndown with an ahead/behind callout and a stat strip.
4. The burndown is also available inside the full Sprint Report — the dedicated sub-tab just gives it more space.

---

### How to generate a people report

1. Click **📊 Reports** in the top bar (or press `Alt+4`).
2. Click **👤 People Report** or switch to the **👤 People Report** sub-tab.
3. Choose **Sprint** or **Date Range** in the scope bar and select the scope.
4. In the People list, select the team members to include (all are selected by default). Add extra usernames in the free-text field if needed.
5. Click **▶ Generate**.
6. Click **⬇ Save HTML** to save to a file.

---

### How to set a custom instance display name

1. Click **Menu → Configure…** in the menu bar.
2. Select the instance using the **PRIMARY / SECONDARY** toggle.
3. Enter a name in the **Display Name** field (e.g. "Production", "Staging").
4. Click **Save**. The name replaces "Primary" / "Secondary" everywhere in the app. Leave it blank to revert to the default label.

---

### How to switch between instances

1. Click **⇄ Switch Instance** in the top bar (or **Menu → Configure…** to change settings).
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

- The app targets **Jira Data Center** exclusively and uses the **REST API v2** and the **Agile API v1.0** for boards, sprints, and ranking.
- **Toast notifications** appear in the bottom-right corner for successes (✓), errors (✗), and warnings (⚠). After creating a story via the quick-add bar, the toast includes an **Undo** button that archives the story if clicked within 5 seconds.
- **Toast notifications** appear in the bottom-right corner for successes (✓), errors (✗), and warnings (⚠). After creating a story via quick-add, the toast includes an **Undo** button that archives the story if clicked within 5 seconds.
- All API calls run on background threads — the UI stays responsive during loads. A maximum of 5 background operations can run concurrently. Failed operations show a **↩ Retry** button in the error dialog where supported.
- Settings (URLs, default project/board, token expiry, project/board filters) are stored via `QSettings` (registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). PAT tokens are stored in the OS keychain when `keyring` is available.
- **Recent stories history** and **per-board column visibility preferences** are also persisted to `QSettings` and restored on the next launch. Both are saved automatically when the app closes cleanly.
- On first save with `keyring` present, any token previously stored as base64 in QSettings is automatically migrated to the keychain and the legacy entry is removed.
- The Kanban board persists between tab switches and only rebuilds cards when the sprint data actually changes.
- The burndown chart uses the sprint's real `startDate` and `endDate` from Jira when available. If the sprint has no dates set (e.g. it hasn't been started formally), the chart falls back to a 14-day estimate based on the proportion of points completed.
- The Backlog view tries `sprint is EMPTY` first and automatically falls back to `sprint not in openSprints() AND sprint not in closedSprints()` if the first form is not supported by the instance.
- Story ranking requires the board to have ranking enabled and the Agile rank field to be writable. Boards without ranking will show a clear error; the rest of the app is unaffected.
- The velocity history chart requires `PyQt6-Qt6-Svg`. If it is not installed, a text prompt appears in place of the chart and the summary table and CSV export still work normally.
- Archiving requires Jira Data Center 8.1 or later.
- Sprint management (create/start/close) requires the **Manage Sprints** permission on the board. Only one sprint can be active per board at a time — Jira enforces this server-side. The update endpoint uses `POST /rest/agile/1.0/sprint/{id}` and falls back to `PUT` automatically for older DC instances that require it.
