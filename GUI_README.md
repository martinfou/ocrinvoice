# Business Aliases GUI Manager

A PyQt6 desktop application for managing business name aliases used by the OCR invoice parser.

## 🚀 Quick Start

### Prerequisites

1. **Install PyQt6** (required for the GUI):
   ```bash
   pip3 install PyQt6
   ```

   If you're on macOS with Homebrew Python and get permission errors:
   ```bash
   pip3 install --user PyQt6
   ```

2. **Alternative: Use a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install PyQt6
   ```

## 🖥️ Running the GUI

### Method 1: Direct GUI Launcher (Recommended)
```bash
python3 launch_gui.py
```

### Method 2: CLI Wrapper (Simulates ocrinvoice --gui)
```bash
# Launch GUI directly
python3 ocrinvoice_cli.py --gui

# Or through aliases command
python3 ocrinvoice_cli.py aliases --gui
```

### Method 3: One-liner
```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from ocrinvoice.gui.main_window import main; main()"
```

## 📋 Available Commands

### CLI Commands
```bash
# Show help
python3 ocrinvoice_cli.py --help

# Show aliases help
python3 ocrinvoice_cli.py aliases --help

# Launch GUI
python3 ocrinvoice_cli.py --gui

# Launch GUI through aliases
python3 ocrinvoice_cli.py aliases --gui
```

## 🎯 GUI Features

The Business Aliases GUI Manager provides:

- **📋 Alias Table**: View all business aliases in a sortable table
- **➕ Add Aliases**: Add new company name mappings
- **✏️ Edit Aliases**: Modify existing aliases
- **🗑️ Delete Aliases**: Remove aliases with confirmation
- **🔍 Search**: Find aliases quickly (Week 2)
- **📊 Statistics**: View alias usage statistics
- **📥 Import/Export**: Import/export alias data (Week 2)

## 🏗️ Development Status

### ✅ Week 1: Foundation (COMPLETED)
- [x] Project structure setup
- [x] Basic PyQt6 application skeleton
- [x] Main window layout
- [x] Basic table widget
- [x] Add/edit form
- [x] Basic CRUD operations
- [x] CLI integration

### 🔄 Week 2: Data Management (NEXT)
- [ ] Enhanced search functionality
- [ ] Import/export dialogs
- [ ] Data validation improvements
- [ ] Error handling enhancements

### 📋 Week 3: User Interface (PLANNED)
- [ ] Advanced filtering
- [ ] Bulk operations
- [ ] Keyboard shortcuts
- [ ] Context menus

### 🎨 Week 4: Integration (PLANNED)
- [ ] CLI integration completion
- [ ] Configuration management
- [ ] Comprehensive testing
- [ ] Documentation

## 🐛 Troubleshooting

### Import Errors
If you get import errors:
1. Make sure PyQt6 is installed: `pip3 install PyQt6`
2. On macOS, try: `pip3 install --user PyQt6`
3. Use a virtual environment for isolation

### GUI Not Appearing
1. Check if the process is running in the background
2. Look for error messages in the terminal
3. Make sure you have a display server running (X11 on Linux, etc.)

### Permission Errors
1. Make sure the launcher scripts are executable: `chmod +x *.py`
2. Use `python3` instead of `python` if needed

## 📁 File Structure

```
src/ocrinvoice/gui/
├── __init__.py              # Package initialization
├── main_window.py           # Main application window
├── alias_table.py           # Custom table widget
├── alias_form.py            # Add/edit form widget
├── dialogs/                 # Modal dialogs (Week 2)
└── utils/                   # Utility functions (Week 2)
```

## 🔗 Integration

The GUI integrates seamlessly with the existing CLI functionality:
- Uses the same `BusinessAliasManager` for data operations
- Maintains compatibility with existing alias files
- Follows the same data formats and validation rules

## 📝 Next Steps

1. **Test the GUI**: Run `python3 launch_gui.py` and explore the interface
2. **Add Aliases**: Use the "➕ Add" button to create new aliases
3. **View Statistics**: Click "📊 Statistics" to see alias information
4. **Continue Development**: Move to Week 2 for enhanced features

---

**Ready to manage your business aliases with a beautiful GUI!** 🎉
