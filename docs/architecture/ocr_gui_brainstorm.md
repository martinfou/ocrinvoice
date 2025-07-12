# OCR Invoice Parser GUI - Comprehensive Design Brainstorm

## 1. Main Screen (Hub)

### Navigation Layout
- **Navigation Tabs/Sidebar:**  
  - Home (Dashboard)
  - Single PDF OCR
  - Batch PDF OCR
  - PDF Search
  - Business Alias Manager (existing)
  - Settings

### ASCII Mockup: Main Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│                    OCR Invoice Parser                       │
├─────────────────────────────────────────────────────────────┤
│  [🏠 Home] [📁 Single] [📂 Batch] [🔍 Search] [⚙️ Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Quick Start   │  │ Recent Projects │  │ Statistics   │ │
│  │                 │  │                 │  │              │ │
│  │ • Single PDF    │  │ • Q1_2024       │  │ • Files      │ │
│  │ • Batch Folder  │  │ • Q4_2023       │  │ • Success    │ │
│  │ • Search PDFs   │  │ • Q3_2023       │  │ • Errors     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Recent Activity                                         │ │
│  │ • Processed invoice_001.pdf → ...                       │ │
│  │ • Batch completed: 47 files, 2 errors                   │ │
│  │ • Added alias: "Hydro Quebec" → "HYDRO-QUÉBEC"          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Single PDF OCR Mode

### Layout
- **Left:** PDF preview (with zoom, page navigation)
- **Right:**  
  - Project Name input (used in file naming)
  - Document Type dropdown
  - Extracted fields (company, date, total, invoice #, etc.) with:
    - Confidence indicator (color or icon)
    - Inline edit/confirmation for each field
    - "Unsure" fields highlighted, with a prompt for user confirmation
  - File naming preview (shows: `project_documentType_date_company_$total.pdf`)
  - "Rename & Save" button
  - "Re-run OCR" button

### ASCII Mockup: Single PDF Mode
```
┌─────────────────────────────────────────────────────────────┐
│ Single PDF Processor                    [📁 Browse] [🔄]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │                 │  │ Project Settings                    │ │
│  │   PDF Preview   │  ├─────────────────────────────────────┤ │
│  │                 │  │ Project Name: [Q1_2024_____________]│ │
│  │                 │  │ Document Type: [Invoice ▼]         │ │
│  │                 │  │ Interactive Mode: [✓] Enabled      │ │
│  │                 │  │ Confidence Threshold: [80% ████████]│ │
│  │                 │  └─────────────────────────────────────┘ │
│  │                 │                                        │
│  │                 │  ┌─────────────────────────────────────┐ │
│  │                 │  │ Extracted Data                      │ │
│  │                 │  ├─────────────────────────────────────┤ │
│  │                 │  │ Company: [Hydro Quebec] [✓] [✏️]   │ │
│  │                 │  │ Date: [2024-01-15] [✓] [✏️]        │ │
│  │                 │  │ Total: [$1,234.56] [✓] [✏️]        │ │
│  │                 │  │ Invoice #: [INV-001] [⚠️] [✏️]     │ │
│  │                 │  └─────────────────────────────────────┘ │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ File Naming Preview                                     │ │
│  │ Q1_2024_invoice_2024-01-15_hydro_quebec_$1234.56.pdf    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [🔄 Re-process] [💾 Save] [📁 Rename File] [📊 Export]      │
└─────────────────────────────────────────────────────────────┘
```

### Features
- Drag-and-drop PDF to start
- If confidence is low, pop up a dialog for user confirmation
- Show live preview of the new filename
- Option to open containing folder after save

---

## 3. Batch PDF OCR Mode

### Layout
- **Top:** Project Name, Document Type, Folder Picker, Recursive option, Confidence threshold slider, "Start Batch" button
- **Center:** Table of PDFs in the folder:
  - Columns: Filename, Status (pending/processing/done/needs review), Extracted Company, Date, Total, New Filename, [Preview] button
  - Search/filter bar above the table (filters by filename or extracted text)
- **Bottom:** Progress bar, stats (total, processed, errors, interactive confirmations needed)

### ASCII Mockup: Batch PDF Mode
```
┌─────────────────────────────────────────────────────────────┐
│ Batch PDF Processor                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Project Configuration                                   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Project Name: [Q1_2024_Invoices________________]        │ │
│  │ Folder: [📁 /Users/me/Documents/Invoices] [Browse]      │ │
│  │ Document Type: [Invoice ▼] Recursive: [✓] Subfolders    │ │
│  │ Interactive Mode: [✓] Only for low confidence           │ │
│  │ Confidence Threshold: [75% ████████]                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ File Discovery & Preview                                │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Found 47 PDF files                                      │ │
│  │                                                         │ │
│  │ ┌─────────────────────────────────────────────────────┐ │ │
│  │ │ Filename          │ Size    │ Status  │ Preview     │ │ │
│  │ ├─────────────────────────────────────────────────────┤ │ │
│  │ │ invoice_001.pdf   │ 245 KB  │ [✓]     │ [👁️ View]   │ │ │
│  │ │ invoice_002.pdf   │ 189 KB  │ [✓]     │ [👁️ View]   │ │ │
│  │ │ invoice_003.pdf   │ 312 KB  │ [⚠️]     │ [👁️ View]   │ │ │
│  │ │ ...               │ ...     │ ...     │ ...         │ │ │
│  │ └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Processing Progress                                     │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ████████████████████████████████████████████████████████  │ │
│  │ Processed: 23/47 files (48.9%)                          │ │
│  │ Success: 21 | Errors: 2 | Interactive: 0                │ │
│  │ Estimated time remaining: 2m 15s                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [▶️ Start Processing] [⏸️ Pause] [⏹️ Stop] [📊 Results]     │
└─────────────────────────────────────────────────────────────┘
```

### Features
- Only show PDF preview/interactive dialog for files needing user confirmation (low-confidence fields)
- "Skip", "Confirm", "Edit" options in interactive mode
- Batch renaming with live preview of filenames
- Export results (CSV/JSON)
- Pause/resume batch

---

## 4. PDF Search Tool

### Layout
- Folder picker
- Search bar (with options: case sensitive, regex, fuzzy)
- Table of results: Filename, Match context (snippet), [Open PDF] button
- Option to export search results

### ASCII Mockup: PDF Search Tool
```
┌─────────────────────────────────────────────────────────────┐
│ PDF Content Search                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Search Configuration                                    │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Search Folder: [📁 /Users/me/Documents] [Browse]        │ │
│  │ Search Term: [Hydro Quebec________________] [🔍 Search] │ │
│  │ Options: [✓] Case sensitive [✓] Fuzzy match [✓] Regex   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Search Results (23 matches found)                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ┌─────────────────────────────────────────────────────┐ │ │
│  │ │ Filename          │ Match Type │ Context            │ │ │
│  │ ├─────────────────────────────────────────────────────┤ │ │
│  │ │ invoice_001.pdf   │ Company    │ "Hydro Quebec Inc" │ │ │
│  │ │ invoice_002.pdf   │ Address    │ "Hydro Quebec St"  │ │ │
│  │ │ invoice_003.pdf   │ Total      │ "Hydro Quebec: $50"│ │ │
│  │ │ ...               │ ...        │ ...                │ │ │
│  │ └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [📁 Open Folder] [📊 Export Results] [🔍 New Search]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. File Renaming UX

### Template Builder
- Visual builder for filename template (checkboxes for each field, drag to reorder, separator picker)
- Live preview with sample data
- Warnings for missing/invalid fields
- Option to save/load templates

### ASCII Mockup: File Naming Template Builder
```
┌─────────────────────────────────────────────────────────────┐
│ File Naming Template Builder                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Template: [project_documentType_date_company_$total]       │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Template Components                                    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [✓] Project Name    [project]                          │  │
│  │ [✓] Document Type   [documentType]                     │  │
│  │ [✓] Date            [date]                             │  │
│  │ [✓] Company         [company]                          │  │
│  │ [✓] Total Amount    [$total]                           │  │
│  │ [ ] Invoice Number  [invoiceNumber]                    │  │
│  │ [ ] Custom Text     [custom]                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Preview Examples                                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Q1_2024_invoice_2024-01-15_hydro_quebec_$1234.56.pdf   │  │
│  │ Q1_2024_invoice_2024-01-16_royal_bank_$567.89.pdf      │  │
│  │ Q1_2024_invoice_2024-01-17_bell_canada_$234.12.pdf     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                             │
│  [💾 Save Template] [🔄 Reset] [❌ Cancel]                  │
└─────────────────────────────────────────────────────────────┘
```

### Batch Mode
- Show all new filenames in a column before confirming rename
- Handle conflicts (e.g., add suffix if duplicate)

---

## 6. Interactive Mode (Uncertain Extraction)

### Single Mode
- If a field is low-confidence, highlight and prompt user to confirm or edit
- Show context from PDF (highlighted region, text snippet)

### ASCII Mockup: Interactive Confirmation Dialog
```
┌─────────────────────────────────────────────────────────────┐
│ Interactive Confirmation - Low Confidence Detection         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  File: invoice_003.pdf                                      │
│  Field: Company Name                                        │
│  Confidence: 65% (Low)                                      │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ PDF Context                                            │  │
│  │                                                        │  │
│  │ ...                                                    │  │
│  │ Invoice Date: 2024-01-17                               │  │
│  │ Company: Hydro Quebec Inc.                             │  │
│  │ Address: 123 Main Street                               │  │
│  │ ...                                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Extracted Options                                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ [✓] Hydro Quebec Inc. (65% confidence)                  │ │
│  │ [ ] Hydro Quebec (78% confidence)                       │ │
│  │ [ ] Hydro Quebec Inc (72% confidence)                   │ │
│  │ [ ] Enter manually: [________________]                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [✅ Confirm] [🔄 Re-scan] [⏭️ Skip] [❌ Cancel]            │
└─────────────────────────────────────────────────────────────┘
```

### Batch Mode
- Only pause for user input when a file/field is below confidence threshold
- Show PDF and extracted data side-by-side for quick confirmation

---

## 7. Other UX Enhancements
- Keyboard shortcuts for all major actions
- Drag-and-drop support for files/folders
- Recent projects/folders list
- Status bar with helpful messages
- Integration with business alias manager (right-click to add alias from extracted company field)

---

## 8. Technical/Implementation Notes
- Use QTableView for file lists and search results
- Use QSplitter for resizable panels (PDF preview vs. data)
- Use QProgressBar for batch progress
- Use QDialog for interactive confirmations
- Use QSettings for persisting user preferences (recent folders, templates, etc.)
- Modularize: each mode as a separate QWidget, managed by a QStackedWidget in the main window

---

### Summary Table of Key Features

| Feature                | Single Mode | Batch Mode | Search Tool | All Modes |
|------------------------|:----------:|:----------:|:-----------:|:---------:|
| PDF Preview            |     ✓      |   (✓*)     |     ✓       |           |
| Project Name           |     ✓      |     ✓      |             |           |
| File Renaming Preview  |     ✓      |     ✓      |             |           |
| Interactive Confirm    |     ✓      |     ✓      |             |           |
| Progress Bar           |            |     ✓      |             |           |
| Search PDFs            |            |     ✓      |     ✓       |           |
| Alias Manager          |     ✓      |     ✓      |             |     ✓     |

(*): Only for files needing confirmation 