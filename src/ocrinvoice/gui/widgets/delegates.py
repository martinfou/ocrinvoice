from PyQt6.QtWidgets import QStyledItemDelegate, QDateEdit, QComboBox, QLineEdit, QMessageBox
from PyQt6.QtCore import QDate, Qt

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
    def __init__(self, business_list, parent=None):
        super().__init__(parent)
        self.business_list = business_list

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.addItems(self.business_list)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMaxVisibleItems(15)
        # Disconnect previous connections to avoid duplicate triggers
        try:
            combo.lineEdit().editingFinished.disconnect()
        except Exception:
            pass
        combo.lineEdit().editingFinished.connect(lambda: self._check_add_new(combo))
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        if value:
            idx = editor.findText(value, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                editor.setCurrentIndex(idx)
            else:
                editor.setEditText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value)

    def _check_add_new(self, combo):
        text = combo.currentText().strip()
        if text and text not in self.business_list:
            # Prompt to add new business
            reply = QMessageBox.question(combo, "Add New Business", f'Add "{text}" as a new business/alias?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.business_list.append(text)
                combo.addItem(text)
                combo.setCurrentText(text)
        # Always ensure the current text is set (even if not added)
        combo.setEditText(text) 