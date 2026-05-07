# Jira Team Manager

A PyQt6 desktop app for managing your team's Jira stories by sprint — update assignees, story points, descriptions, and post comments, all from one panel.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python jira_team_manager.py
```

---

## Configuration

On first launch, click **⚙ Configure** in the top-right corner and enter:

| Field | Value |
|---|---|
| **Jira URL** | `https://yourteam.atlassian.net` |
| **Email** | Your Atlassian account email |
| **API Token** | Generate at [id.atlassian.com → Security → API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |

Click **Test Connection** to verify before saving.

---

## Workflow

1. **Select a project** from the PROJECT dropdown — boards and members will auto-load.
2. **Select a board** — sprints will auto-load.
3. **Select a sprint** and click **Load Stories**.
4. **Click any story row** in the table to open it in the edit panel on the right.
5. **Edit fields:**
   - **Assignee** — pick from team members on that project
   - **Story Points** — numeric spinner (supports half-points)
   - **Description** — full plain-text edit
   - **Add Comment** — optional comment posted on save
6. Click **▶ SAVE CHANGES** — the app updates Jira and refreshes the table.

---

## Notes

- The app uses the **Jira Cloud REST API v3** and the **Agile/Software API** for boards and sprints.
- Story points map to `customfield_10016` (standard for Jira Cloud next-gen projects).
- Only **Jira Cloud** is supported (email + API token auth). Jira Server/DC uses different auth.
- All API calls run on background threads — the UI stays responsive during loads.
- The filter box (top-right of the table) filters stories live by any column text.
