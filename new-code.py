Traceback (most recent call last):
  File "c:\Users\P09816\OneDrive - NGC\Desktop\Coding\JIRA_manager\sprintmate.py", line 1722, in _on_story_selected
    self.edit_panel.load_issue(issue)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "c:\Users\P09816\OneDrive - NGC\Desktop\Coding\JIRA_manager\sprintmate.py", line 1164, in load_issue
    print(f"ASSIGNEE FIELD: {assignee}\nMembers Sample: {self._members[:2] if self._members else 'EMPTY'}")
                             ^^^^^^^^
UnboundLocalError: cannot access local variable 'assignee' where it is not associated with a value
