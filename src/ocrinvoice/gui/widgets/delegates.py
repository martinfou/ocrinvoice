from PyQt6.QtWidgets import QStyledItemDelegate, QDateEdit
from PyQt6.QtCore import QDate

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