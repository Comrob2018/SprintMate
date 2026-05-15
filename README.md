# SprintMate  ◈  v2.11.1

A PyQt6 desktop app for managing your team's Jira Data Center sprint stories — update assignees, story points, priorities, descriptions, post comments, transition statuses, import bulk comments, bulk-create stories from CSV, and export sprint data, all from one panel.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **`keyring` is recommended** for secure PAT storage. If installed, tokens are stored in your OS native credential store (Windows Credential Manager, macOS Keychain, Linux Secret Service) instead of encoded in application settings. If `keyring` is not installed the app falls back to legacy storage automatically.

### 2. Run the app

```bash
python sprintmate.py
```

---

## Configuration

On first launch, click **⚙ Configure** in the top bar. SprintMate supports two Jira Data Center instances — **Primary** and **Secondary** — each configured independently.

Use the **PRIMARY / SECONDARY** toggle at the top of the settings dialog to switch between them.

| Field | Value |
|---|---|
| **Jira URL** | Base URL of the instance, e.g. `https://jira.yourcompany.com` |
| **PAT Token** | Personal Access Token generated in Jira → Profile → Personal Access Tokens |
| **Token Expiry** | Optional expiry date — SprintMate will warn you when it is approaching |
| **Default Project** | Project key to auto-select on connect, e.g. `project1` |
| **Default Board** | Board name to auto-select on connect, e.g. `project1 board` |
| **Filter Projects** | Comma-separated substrings — only matching projects appear in the dropdown. Leave blank to show all. |
| **Filter Boards** | Comma-separated substrings — only matching boards appear in the dropdown. Leave blank to show all. |

Click **Test Connection** to verify credentials before saving. Click **Save** to apply.

> SprintMate will warn you in the status bar if a token has expired or is within 14 days of expiry, both on launch and after saving settings.

---

## Workflow

### Navigating stories

1. On launch, the last-used instance connects automatically if credentials are saved.
2. **Select a project** from the PROJECT dropdown — boards and members auto-load.
3. **Select a board** — sprints auto-load.
4. **Select a sprint** and click **Load Stories** (or press `Ctrl+L`).
5. Use the **filter box** (top-right of the filter bar) to search live across all columns. Matching cells are highlighted.
6. **Click any story row** to open it in the edit panel on the right.

### Table columns

By default the table shows KEY, SUMMARY, ASSIGNEE, STATUS, and DUE DATE. **Right-click the column header** to open a toggle menu and show or hide any of the following columns: ASSIGNEE, STATUS, DUE DATE, PTS, PRIORITY, TYPE, FEATURE LINK. KEY and SUMMARY are always visible. Column visibility resets to defaults each time stories are loaded.

The table supports **click-to-sort** on any column header.

### Editing a story

The **▶ SAVE CHANGES** button is disabled until you make a change. Fields available for editing:

| Field | Notes |
|---|---|
| **Assignee** | Picked from all users on the instance |
| **Feature Link** | URL or ID for the linked feature |
| **Issue Type** | Loaded from the project's configured types |
| **Priority** | Highest / High / Medium / Low / Lowest |
| **Story Points** | Fibonacci dropdown: 0, 1, 3, 5, 8, 13, 21 |
| **Sprint** | Move the story to a different sprint on save |
| **Due Date** | Calendar picker; use Clear to remove |
| **Status Transition** | Apply a workflow transition on save |
| **Description** | Full plain-text edit |
| **Add Comment** | Optional comment posted to the story on save |

The **RECENT COMMENTS** panel shows the five most recent comments on the selected story (author, date, and truncated body) with no additional API calls. Click **⤢ Expand** to view a selected comment in full.

The **⎘** button in the edit panel header copies the current issue key to the clipboard.

Click **▶ SAVE CHANGES** (or press `Ctrl+S`) — the app updates Jira and re-selects the saved story automatically.

> If you attempt to reload stories or close the app while there are unsaved changes in the edit panel, SprintMate will prompt you before discarding them. It will also warn if background operations are still in flight when you close.

### Creating a story

Click **＋ New Story** (or press `Ctrl+N`) in the filter bar to open the creation dialog. Fill in summary (required), issue type, priority, story points, assignee, sprint, due date, and description, then click **＋ Create Story**.

The story points dropdown in the creation dialog includes the extended Fibonacci sequence: 0, 1, 3, 5, 8, 13, 21.

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
- **Cross-post** — if a story with the same summary and assignee is found on the other instance, the comment is posted there too. Cross-post targets are highlighted in cyan in the preview. Cross-posting uses fuzzy JQL summary matching and falls back to exact match if the contains search returns nothing.

Progress is shown per-comment in the progress bar. Any failures are reported in the status bar at completion without aborting the rest of the batch.

### Exporting stories

Click **⬇ Export** (or press `Ctrl+E`) to export the current sprint's stories to a CSV file. You can choose to export all stories or select specific ones using a basket-style picker (search, double-click or use the Add/Remove buttons).

The exported CSV includes the following columns:

```
key, summary, assignee, status, issue_type, priority, story_points,
feature_link, due_date, sprint, description, comments
```

Comments are exported as a pipe-separated list in the format `[Author]: body text`.

The suggested filename is auto-generated from the current project, board, sprint, and date (e.g. `project1-project1-board-Sprint-42-2025-06-01.csv`).

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save changes (when save button is enabled) |
| `Ctrl+N` | New Story |
| `Ctrl+L` | Load Stories |
| `Ctrl+I` | Import Comments |
| `Ctrl+E` | Export Stories |
| `Ctrl+F` | Focus the filter/search box |
| `Ctrl+C` | Copy visible columns of the selected row to clipboard (comma-separated) — table must have focus |
| `Ctrl+Shift+C` | Copy full issue as a CSV-ready row (all fields, matching export format) |

---

## Top Bar

| Button | Action |
|---|---|
| **⚙ Configure** | Open the settings dialog |
| **⇄ Switch Instance** | Toggle between Primary and Secondary |
| **↺ Refresh** | Reload the current sprint |

---

## Notes

- The app targets **Jira Data Center** exclusively and uses the **REST API v2** and the **Agile API v1.0** for boards and sprints.
- Story point field IDs are mapped per instance: `customfield_10106` (Secondary) and `customfield_10006` (Primary).
- All API calls run on background threads — the UI stays responsive during loads. A maximum of 5 background operations can run concurrently.
- Settings (URLs, default project/board, token expiry, project/board filters) are stored via `QSettings` (registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). PAT tokens are stored in the OS keychain when `keyring` is available.
- On first save with `keyring` present, any token previously stored as base64 in QSettings is automatically migrated to the keychain and the legacy entry is removed.
