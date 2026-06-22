## [2.15.0] — 2026-06-22

### Features

* **Clone stories to any project or instance.** Added a "⎘ Clone" button to the story edit panel header. Opens a dialog with three sections: a target instance selector (current instance, or the other saved instance if credentials exist), a target project dropdown populated lazily from the selected instance, and editable fields for Summary (pre-filled as `[Clone] Original summary`), Description, and Assignee. Executes via `POST /rest/api/2/issue` against the target `JiraClient`. On success, shows the new issue key with **Copy Key** and **Open in Jira** action buttons.
