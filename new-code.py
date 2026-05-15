Makes total sense — “Yes/No/Cancel” is completely ambiguous in that context. Here’s the change:​​​​​​​​​​​​​​​​

QMessageBox.question doesn’t support custom button labels, so we need to swap it for a QMessageBox built manually. Here’s the replacement:

        # Ask the user: export all or select
        msg = QMessageBox(self)
        msg.setWindowTitle("Export Stories")
        msg.setText(f"Export all {len(self._issues)} stories, or select specific ones?")
        btn_all    = msg.addButton("All",    QMessageBox.ButtonRole.YesRole)
        btn_select = msg.addButton("Select", QMessageBox.ButtonRole.NoRole)
        msg.addButton("Cancel",              QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(btn_all)
        msg.exec()
        clicked = msg.clickedButton()
        # Map: All = export everything, Select = open picker, Cancel = abort
        if clicked is btn_all:
            issues_to_export = self._issues
        elif clicked is btn_select:
            dlg = ExportStoriesDialog(self._issues, self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            issues_to_export = dlg.get_selected_issues()
            if not issues_to_export:
                return
        else:
            return


This replaces lines 3191–3210 (up to and including issues_to_export = self._issues). Want me to apply it?​​​​​​​​​​​​​​​​