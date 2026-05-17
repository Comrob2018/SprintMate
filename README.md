# SprintMate  ◈  v2.11.7

A Python desktop app for managing your team's Jira Data Center sprint stories — update assignees, story points, priorities, descriptions, post comments, transition statuses, import bulk comments, bulk-create stories from CSV, and export sprint data, all from one panel.

---

## Setup
### 1. Generate your Personal Access Token

* Log in to JIRA.
* Open Profile ▶ Personal Access Tokens.
* Click Create token, give it a name, set an expiry, pick the required scopes, and Create.
* **Copy the generated token** – you'll see it only once.
  
### 2. Install python

* Go to the appropriate place to get the latest version of python.
* **If using this on a company PC, you may need to get permission** 

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

> SprintMate will warn you in the status bar if a token has expired or is within 14 days of expiry — on launch, after saving settings, and every 4 hours while the app is running.

---

## Workflow

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

### Editing a story

The **▶ SAVE CHANGES** button is disabled until you make a change. Fields available for editing:

| Field | Notes |
|---|---|
| **Assignee** | Picked from all users on the instance |
| **Feature Link** | URL or ID for the linked feature |
| **Issue Type** | Loaded from the project's configured types |
| **Priority** | Highest / High / Medium / Low / Lowest |
| **Story Points** | Fibonacci dropdown: 0, 1, 3, 5, 8, 13, 21. Values 13 and 21 are highlighted in amber with a "consider splitting" label. |
| **Sprint** | Move the story to a different sprint on save |
| **Due Date** | Calendar picker; use Clear to remove |
| **Status Transition** | Apply a workflow transition on save |
| **Description** | Full plain-text edit |
| **Add Comment** | Optional comment posted to the story on save |

The **RECENT COMMENTS** panel shows the five most recent comments on the selected story (author, date, and truncated body) with no additional API calls. Click **⤢ Expand** to view a selected comment in full.

The edit panel header includes three controls:

| Control | Action |
|---|---|
| **⎘** | Copies the current issue key to the clipboard |
| **⎋ Open in Jira** | Opens the current story in your browser |

Click **▶ SAVE CHANGES** (or press `Ctrl+S`) — the app updates Jira and re-selects the saved story automatically.

> If Jira rejects the story points field on save (e.g. because it is read-only for the issue type), a warning dialog will explain that all other changes were saved but points were not.

> If you attempt to reload stories or close the app while there are unsaved changes in the edit panel, SprintMate will prompt you before discarding them. It will also warn if background operations are still in flight when you close.

### Creating a story

Click **＋ New Story** (or press `Ctrl+N`) in the filter bar to open the creation dialog. Fill in summary (required), issue type, priority, story points, assignee, sprint, due date, and description, then click **＋ Create Story**.

The story points dropdown includes: 0, 1, 3, 5, 8, 13, 21. Values 13 and 21 are highlighted in amber with a "consider splitting" label.

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

## User Guide

### How to set up and connect for the first time

1. Install dependencies with `pip install -r requirements.txt`, then run `python sprintmate.py`.
2. Click **⚙ Configure** in the top bar.
3. Use the **PRIMARY / SECONDARY** toggle to select the instance you want to set up first.
4. Enter the **Jira URL** and your **PAT Token**. Optionally set a **Token Expiry** date, a **Default Project**, and a **Default Board** so the app pre-selects them on every launch.
5. Click **Test Connection** — you should see a green "Connected as …" confirmation.
6. Click **Save**. Repeat steps 3–5 for the other instance if needed.
7. The app will connect automatically and load your projects. Select a project, board, and sprint, then click **Load Stories**.