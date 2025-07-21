import sys
from PyQt6.QtWidgets import QStyledItemDelegate, QDateEdit, QComboBox, QLineEdit, QMessageBox
from PyQt6.QtCore import QDate, Qt, QTimer, pyqtSignal

class DateEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd")
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        if value:
            date = QDate.fromString(value, "yyyy-MM-dd")
            if not date.isValid():
                # Try common alternative formats
                for fmt in ("dd/MM/yyyy", "MM/dd/yyyy", "yyyy/MM/dd"): 
                    date = QDate.fromString(value, fmt)
                    if date.isValid():
                        break
            if date.isValid():
                editor.setDate(date)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date().toString("yyyy-MM-dd"))

class BusinessComboDelegate(QStyledItemDelegate):
    businessAdded = pyqtSignal(str)
    def __init__(self, business_list, parent=None):
        super().__init__(parent)
        self.business_list = business_list

    def createEditor(self, parent, option, index):
        print("[DEBUG] BusinessComboDelegate.createEditor called", file=sys.stderr)
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.addItems(self.business_list)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMaxVisibleItems(15)
        # Use a dynamic property on the editor to guard against double addition
        combo._business_added = False
        def on_editing_finished():
            if not getattr(combo, '_business_added', False):
                combo._business_added = True
                self._check_add_new(combo)
                # Disconnect to prevent further triggers
                try:
                    combo.lineEdit().editingFinished.disconnect()
                except Exception:
                    pass
        try:
            combo.lineEdit().editingFinished.disconnect()
        except Exception:
            pass
        combo.lineEdit().editingFinished.connect(on_editing_finished)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        print(f"[DEBUG] setEditorData: value={value}", file=sys.stderr)
        if value:
            idx = editor.findText(value, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                editor.setCurrentIndex(idx)
            else:
                editor.setEditText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        print(f"[DEBUG] setModelData: value={value}", file=sys.stderr)
        model.setData(index, value)

    def _check_add_new(self, combo):
        text = combo.currentText().strip()
        print(f"[DEBUG] _check_add_new: text={text}", file=sys.stderr)
        if text and text not in self.business_list:
            print(f"[DEBUG] Scheduling prompt to add new business: {text}", file=sys.stderr)
            def show_dialog():
                try:
                    parent = combo.window() if combo.window() else None
                    print(f"[DEBUG] Showing QMessageBox for: {text}, parent={parent}", file=sys.stderr)
                    reply = QMessageBox.question(parent, "Add New Business", f'Add "{text}" as a new business/alias?',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                    print(f"[DEBUG] QMessageBox reply: {reply}", file=sys.stderr)
                    if reply == QMessageBox.StandardButton.Yes:
                        print(f"[DEBUG] Adding new business: {text}", file=sys.stderr)
                        self.business_list.append(text)
                        combo.addItem(text)
                        combo.setCurrentText(text)
                        self.businessAdded.emit(text)
                    combo.setEditText(text)
                except Exception as e:
                    print(f"[ERROR] Exception in show_dialog: {e}", file=sys.stderr)
            QTimer.singleShot(0, show_dialog)
        else:
            combo.setEditText(text)


class CategoryComboDelegate(QStyledItemDelegate):
    categoryAdded = pyqtSignal(str)
    def __init__(self, category_list, parent=None):
        super().__init__(parent)
        self.category_list = category_list

    def createEditor(self, parent, option, index):
        print("[DEBUG] BusinessComboDelegate.createEditor called", file=sys.stderr)
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.addItems(self.business_list)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMaxVisibleItems(15)
        # Use a dynamic property on the editor to guard against double addition
        combo._business_added = False
        def on_editing_finished():
            if not getattr(combo, '_business_added', False):
                combo._business_added = True
                self._check_add_new(combo)
                # Disconnect to prevent further triggers
                try:
                    combo.lineEdit().editingFinished.disconnect()
                except Exception:
                    pass
        try:
            combo.lineEdit().editingFinished.disconnect()
        except Exception:
            pass
        combo.lineEdit().editingFinished.connect(on_editing_finished)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        print(f"[DEBUG] setEditorData: value={value}", file=sys.stderr)
        if value:
            idx = editor.findText(value, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                editor.setCurrentIndex(idx)
            else:
                editor.setEditText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        print(f"[DEBUG] setModelData: value={value}", file=sys.stderr)
        model.setData(index, value)

    def _check_add_new(self, combo):
        text = combo.currentText().strip()
        print(f"[DEBUG] _check_add_new: text={text}", file=sys.stderr)
        if text and text not in self.business_list:
            print(f"[DEBUG] Scheduling prompt to add new business: {text}", file=sys.stderr)
            def show_dialog():
                try:
                    parent = combo.window() if combo.window() else None
                    print(f"[DEBUG] Showing QMessageBox for: {text}, parent={parent}", file=sys.stderr)
                    reply = QMessageBox.question(parent, "Add New Business", f'Add "{text}" as a new business/alias?',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                    print(f"[DEBUG] QMessageBox reply: {reply}", file=sys.stderr)
                    if reply == QMessageBox.StandardButton.Yes:
                        print(f"[DEBUG] Adding new business: {text}", file=sys.stderr)
                        self.business_list.append(text)
                        combo.addItem(text)
                        combo.setCurrentText(text)
                        self.businessAdded.emit(text)
                    combo.setEditText(text)
                except Exception as e:
                    print(f"[ERROR] Exception in show_dialog: {e}", file=sys.stderr)
            QTimer.singleShot(0, show_dialog)
        else:
            combo.setEditText(text)

    def createEditor(self, parent, option, index):
        print("[DEBUG] CategoryComboDelegate.createEditor called", file=sys.stderr)
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.addItems(self.category_list)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMaxVisibleItems(15)
        # Use a dynamic property on the editor to guard against double addition
        combo._category_added = False
        def on_editing_finished():
            if not getattr(combo, '_category_added', False):
                combo._category_added = True
                self._check_add_new(combo)
                # Disconnect to prevent further triggers
                try:
                    combo.lineEdit().editingFinished.disconnect()
                except Exception:
                    pass
        try:
            combo.lineEdit().editingFinished.disconnect()
        except Exception:
            pass
        combo.lineEdit().editingFinished.connect(on_editing_finished)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        print(f"[DEBUG] setEditorData: value={value}", file=sys.stderr)
        if value:
            idx = editor.findText(value, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                editor.setCurrentIndex(idx)
            else:
                editor.setEditText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        print(f"[DEBUG] setModelData: value={value}", file=sys.stderr)
        model.setData(index, value)

    def _check_add_new(self, combo):
        text = combo.currentText().strip()
        print(f"[DEBUG] _check_add_new: text={text}", file=sys.stderr)
        if text and text not in self.category_list:
            print(f"[DEBUG] Scheduling prompt to add new category: {text}", file=sys.stderr)
            def show_dialog():
                try:
                    parent = combo.window() if combo.window() else None
                    print(f"[DEBUG] Showing QMessageBox for: {text}, parent={parent}", file=sys.stderr)
                    reply = QMessageBox.question(parent, "Add New Category", f'Add "{text}" as a new category?',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                    print(f"[DEBUG] QMessageBox reply: {reply}", file=sys.stderr)
                    if reply == QMessageBox.StandardButton.Yes:
                        print(f"[DEBUG] Adding new category: {text}", file=sys.stderr)
                        self.category_list.append(text)
                        combo.addItem(text)
                        combo.setCurrentText(text)
                        self.categoryAdded.emit(text)
                    combo.setEditText(text)
                except Exception as e:
                    print(f"[ERROR] Exception in show_dialog: {e}", file=sys.stderr)
            QTimer.singleShot(0, show_dialog)
        else:
            combo.setEditText(text) 