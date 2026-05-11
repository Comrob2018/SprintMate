Two changes needed in _build_ui:
1. Equal 50/50 split:

# Change this:
splitter.setSizes([680, 480])

# To this:
splitter.setSizes([1, 1])


2. Remove horizontal scroll on the edit panel:

# Change this:
scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setWidget(self.edit_panel)
scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")
right_layout.addWidget(scroll)

# To this:
scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setWidget(self.edit_panel)
scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")
right_layout.addWidget(scroll)


The ScrollBarAlwaysOff prevents horizontal scrolling entirely, and the edit panel contents will just wrap/resize to fit the available width instead.​​​​​​​​​​​​​​​​