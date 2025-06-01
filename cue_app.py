import sys
import os
import json
import webbrowser
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
    QTabWidget, QTextEdit, QLineEdit, QListWidget, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QPoint

PROGRAMS_FILE = 'programs.json'

def load_programs():
    if not os.path.exists(PROGRAMS_FILE):
        return {}
    with open(PROGRAMS_FILE, 'r') as f:
        return json.load(f)

def save_programs(programs):
    with open(PROGRAMS_FILE, 'w') as f:
        json.dump(programs, f, indent=4)

def activate_program_set(name):
    programs = load_programs()
    name = name.lower()
    if name not in programs:
        QMessageBox.critical(None, "Error", f"No program set found with name '{name}'")
        return
    for cmd in programs[name]:
        try:
            if cmd.startswith("http://") or cmd.startswith("https://"):
                webbrowser.open(cmd)
            else:
                subprocess.Popen(cmd, shell=True)
        except Exception as e:
            QMessageBox.critical(None, "Launch Error", f"Failed to start: {cmd}\n{e}")

class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Cue App - Mac OS Style Frameless Window")
        self.resize(700, 550)
        self.setStyleSheet("background-color: #121212; color: white;")

        self.old_pos = None

        # Title bar with mac style buttons
        self.title_bar = QFrame(self)
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: #1c1c1e;")

        self.close_btn = QPushButton(self)
        self.close_btn.setFixedSize(15, 15)
        self.close_btn.setStyleSheet("background-color: #ff5f57; border-radius: 7px; border: none;")
        self.close_btn.clicked.connect(self.close)

        self.min_btn = QPushButton(self)
        self.min_btn.setFixedSize(15, 15)
        self.min_btn.setStyleSheet("background-color: #ffbd2e; border-radius: 7px; border: none;")
        self.min_btn.clicked.connect(self.showMinimized)

        self.max_btn = QPushButton(self)
        self.max_btn.setFixedSize(15, 15)
        self.max_btn.setStyleSheet("background-color: #28c840; border-radius: 7px; border: none;")
        self.max_btn.clicked.connect(self.toggle_max_restore)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(10, 7, 0, 0)
        h_layout.setSpacing(8)
        h_layout.addWidget(self.close_btn)
        h_layout.addWidget(self.min_btn)
        h_layout.addWidget(self.max_btn)
        h_layout.addStretch()
        self.title_bar.setLayout(h_layout)

        # Tabs widget
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: #2e2e2e;
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #444444;
                font-weight: bold;
            }
        """)

        self.create_tabs()

        # Main layout
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0,0,0,0)
        v_layout.setSpacing(0)
        v_layout.addWidget(self.title_bar)
        v_layout.addWidget(self.tabs)

        self.setLayout(v_layout)

        self.is_maximized = False

    def toggle_max_restore(self):
        if self.isMaximized() or self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.title_bar.height():
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def create_tabs(self):
        self.programs = load_programs()

        # Activate Tab
        self.activate_tab = QWidget()
        self.tabs.addTab(self.activate_tab, "Activate")
        self.create_activate_tab()

        # Add New Tab
        self.add_tab = QWidget()
        self.tabs.addTab(self.add_tab, "Add New")
        self.create_add_tab()

        # View All Tab
        self.view_tab = QWidget()
        self.tabs.addTab(self.view_tab, "View All")
        self.create_view_tab()

        # Modify/Delete Tab
        self.modify_tab = QWidget()
        self.tabs.addTab(self.modify_tab, "Modify/Delete")
        self.create_modify_tab()

    def create_activate_tab(self):
        layout = QVBoxLayout(self.activate_tab)
        layout.setContentsMargins(20,20,20,20)
        label = QLabel("Enter Activation Code:")
        label.setStyleSheet("color: white;")
        layout.addWidget(label)

        self.activate_entry = QLineEdit()
        self.activate_entry.setStyleSheet("background-color: #2e2e2e; color: white; padding: 6px;")
        layout.addWidget(self.activate_entry)

        activate_btn = QPushButton("Activate")
        activate_btn.setStyleSheet("background-color: #333333; color: white; padding: 8px;")
        activate_btn.clicked.connect(self.activate_mode)
        layout.addWidget(activate_btn)

        layout.addStretch()

    def create_add_tab(self):
        layout = QVBoxLayout(self.add_tab)
        layout.setContentsMargins(20,20,20,20)

        label_name = QLabel("New Mode Name:")
        label_name.setStyleSheet("color: white;")
        layout.addWidget(label_name)

        self.add_name_entry = QLineEdit()
        self.add_name_entry.setStyleSheet("background-color: #2e2e2e; color: white; padding: 6px;")
        layout.addWidget(self.add_name_entry)

        label_cmds = QLabel("Enter one command per line:")
        label_cmds.setStyleSheet("color: white;")
        layout.addWidget(label_cmds)

        self.add_cmds_text = QTextEdit()
        self.add_cmds_text.setStyleSheet("background-color: #2e2e2e; color: white;")
        self.add_cmds_text.setFixedHeight(120)
        layout.addWidget(self.add_cmds_text)

        save_btn = QPushButton("Save Mode")
        save_btn.setStyleSheet("background-color: #333333; color: white; padding: 8px;")
        save_btn.clicked.connect(self.save_new_mode)
        layout.addWidget(save_btn)

        layout.addStretch()

    def create_view_tab(self):
        layout = QVBoxLayout(self.view_tab)
        layout.setContentsMargins(20,20,20,20)

        self.view_text = QTextEdit()
        self.view_text.setReadOnly(True)
        self.view_text.setStyleSheet("background-color: #2e2e2e; color: white;")
        layout.addWidget(self.view_text)

        self.refresh_view_tab()

    def create_modify_tab(self):
        layout = QVBoxLayout(self.modify_tab)
        layout.setContentsMargins(20,20,20,20)

        self.mod_listbox = QListWidget()
        self.mod_listbox.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #555555;
            }
        """)
        self.mod_listbox.setFixedHeight(150)
        self.mod_listbox.itemSelectionChanged.connect(self.fill_modify_fields)
        layout.addWidget(self.mod_listbox)

        label_name = QLabel("Mode Name:")
        label_name.setStyleSheet("color: white;")
        layout.addWidget(label_name)

        self.mod_name_entry = QLineEdit()
        self.mod_name_entry.setStyleSheet("background-color: #2e2e2e; color: white; padding: 6px;")
        layout.addWidget(self.mod_name_entry)

        label_cmds = QLabel("Commands (one per line):")
        label_cmds.setStyleSheet("color: white;")
        layout.addWidget(label_cmds)

        self.mod_cmds_text = QTextEdit()
        self.mod_cmds_text.setStyleSheet("background-color: #2e2e2e; color: white;")
        self.mod_cmds_text.setFixedHeight(120)
        layout.addWidget(self.mod_cmds_text)

        btn_layout = QHBoxLayout()
        btn_update = QPushButton("Update")
        btn_update.setStyleSheet("background-color: #333333; color: white; padding: 8px;")
        btn_update.clicked.connect(self.update_mode)

        btn_delete = QPushButton("Delete")
        btn_delete.setStyleSheet("background-color: #ff5f57; color: white; padding: 8px;")
        btn_delete.clicked.connect(self.delete_mode)

        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)

        self.refresh_modify_tab()

    def activate_mode(self):
        cue = self.activate_entry.text().strip()
        if not cue:
            QMessageBox.warning(self, "Missing Input", "Please enter a code.")
            return
        activate_program_set(cue)

    def save_new_mode(self):
        name = self.add_name_entry.text().strip().lower()
        cmds = [line.strip() for line in self.add_cmds_text.toPlainText().splitlines() if line.strip()]
        if not name or not cmds:
            QMessageBox.critical(self, "Error", "Mode name and commands required.")
            return
        self.programs[name] = cmds
        save_programs(self.programs)
        QMessageBox.information(self, "Saved", f"Mode '{name}' saved.")
        self.add_name_entry.clear()
        self.add_cmds_text.clear()
        self.refresh_view_tab()
        self.refresh_modify_tab()

    def refresh_view_tab(self):
        self.programs = load_programs()
        if not self.programs:
            self.view_text.setPlainText("No modes saved.")
        else:
            text = ""
            for mode, cmds in sorted(self.programs.items()):
                text += f"[{mode}]\n"
                for cmd in cmds:
                    text += f"  • {cmd}\n"
                text += "\n"
            self.view_text.setPlainText(text)

    def refresh_modify_tab(self):
        self.programs = load_programs()
        self.mod_listbox.clear()
        self.mod_listbox.addItems(sorted(self.programs.keys()))
        self.mod_name_entry.clear()
        self.mod_cmds_text.clear()

    def fill_modify_fields(self):
        items = self.mod_listbox.selectedItems()
        if not items:
            return
        mode = items[0].text()
        self.mod_name_entry.setText(mode)
        cmds = self.programs.get(mode, [])
        self.mod_cmds_text.setPlainText("\n".join(cmds))

    def update_mode(self):
        items = self.mod_listbox.selectedItems()
        if not items:
            QMessageBox.critical(self, "Error", "Select a mode to update first.")
            return
        old_mode = items[0].text()
        new_name = self.mod_name_entry.text().strip().lower()
        cmds = [line.strip() for line in self.mod_cmds_text.toPlainText().splitlines() if line.strip()]
        if not new_name or not cmds:
            QMessageBox.critical(self, "Error", "Mode name and commands required.")
            return
        if new_name != old_mode and new_name in self.programs:
            QMessageBox.critical(self, "Error", f"Mode '{new_name}' already exists.")
            return
        if new_name != old_mode:
            del self.programs[old_mode]
        self.programs[new_name] = cmds
        save_programs(self.programs)
        QMessageBox.information(self, "Updated", f"Mode '{new_name}' updated.")
        self.refresh_modify_tab()
        self.refresh_view_tab()

    def delete_mode(self):
        items = self.mod_listbox.selectedItems()
        if not items:
            QMessageBox.critical(self, "Error", "Select a mode to delete first.")
            return
        mode = items[0].text()
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete mode '{mode}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            del self.programs[mode]
            save_programs(self.programs)
            QMessageBox.information(self, "Deleted", f"Mode '{mode}' deleted.")
            self.refresh_modify_tab()
            self.refresh_view_tab()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())
