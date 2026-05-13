# SprintMate

A PyQt6 desktop app for managing your team's Jira Data Center sprint stories — update assignees, story points, priorities, descriptions, post comments, transition statuses, and import bulk comments, all from one panel.

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

On first launch, click **⚙ Configure** in the top bar. SprintMate supports two Jira Data Center instances — **Sentinel** and **ACyD** — each configured independently.

Use the **SENTINEL / ACYD** toggle at the top of the settings dialog to switch between them.

| Field | Value |
|---|---|
| **Jira URL** | Base URL of the instance, e.g. `https://jira.yourcompany.com` |
| **PAT Token** | Personal Access Token generated in Jira → Profile → Personal Access Tokens |
| **Token Expiry** | Optional expiry date — SprintMate will warn you when it is approaching |
| **Default Project** | Project key to auto-select on connect, e.g. `MDT` |
| **Default Board** | Board name to auto-select on connect, e.g. `MDT board` |

Click **Test Connection** to verify credentials before saving. Click **Save** to apply.

> SprintMate will warn you in the status bar if a token has expired or is within 14 days of expiry, both on launch and after saving settings.

---

## Workflow

### Navigating stories

1. On launch, the last-used instance connects automatically if credentials are saved.
2. **Select a project** from the PROJECT dropdown — boards and members auto-load.
3. **Select a board** — sprints auto-load.
4. **Select a sprint** and click **Load Stories**.
5. Use the **filter box** (top-right of the table) to search live across all columns.
6. **Click any story row** to open it in the edit panel on the right.

### Editing a story

The **▶ SAVE CHANGES** button is disabled until you make a change. Fields available for editing:

| Field | Notes |
|---|---|
| **Assignee** | Picked from all users on the instance |
| **Feature Link** | URL or ID for the linked feature |
| **Issue Type** | Loaded from the project's configured types |
| **Priority** | Highest / High / Medium / Low / Lowest |
| **Story Points** | Fibonacci dropdown: 0, 1, 2, 3, 5, 8, 13, 21 |
| **Sprint** | Move the story to a different sprint on save |
| **Due Date** | Calendar picker; use Clear to remove |
| **Status Transition** | Apply a workflow transition on save |
| **Description** | Full plain-text edit |
| **Add Comment** | Optional comment posted to the story on save |

The **RECENT COMMENTS** panel shows the five most recent comments on the selected story (author, date, and truncated body) with no additional API calls.

Click **▶ SAVE CHANGES** — the app updates Jira and re-selects the saved story automatically.

### Creating a story

Click **＋ New Story** in the filter bar to open the creation dialog. Fill in summary (required), issue type, priority, story points, assignee, sprint, due date, and description, then click **＋ Create Story**.

### Switching instances

Click **⇄ Switch Instance** in the top bar to toggle between Sentinel and ACyD without opening settings. The app swaps credentials, clears the current view, and reloads projects automatically. A warning is shown if the target instance has no saved credentials.

### Importing comments

Click **📄 Import Comments** to bulk-post comments from a text or Markdown file.

**File format — one entry per line:**

```
KEY-123 - Task Summary - Assignee Name: Comment text here
KEY-456 | Another Task | Jane Smith: Another comment here
```

Accepted field separators: `-`, `|`, `~`, `;`

A preview dialog shows all parsed entries with their match status before anything is posted:

- **Matched** entries (key found in the current sprint) are posted to the active instance.
- **Unmatched** entries are skipped.
- **Cross-post** — if a story with the same summary and assignee is found on the other instance, the comment is posted there too. Cross-post targets are highlighted in cyan in the preview.

Progress is shown per-comment in the progress bar. Any failures are reported in the status bar at completion without aborting the rest of the batch.

---

## Notes

- The app targets **Jira Data Center** exclusively and uses the **REST API v2** and the **Agile API v1.0** for boards and sprints.
- Story point field IDs are mapped per instance: `customfield_10106` (Sentinel) and `customfield_10006` (ACyD).
- All API calls run on background threads — the UI stays responsive during loads.
- Settings (URLs, default project/board, token expiry) are stored via `QSettings` (registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS). PAT tokens are stored in the OS keychain when `keyring` is available.
