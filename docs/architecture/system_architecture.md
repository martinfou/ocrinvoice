# OCR Invoice Parser - System Architecture

> **High-level system design and architecture overview**

## 🏗️ System Overview

The OCR Invoice Parser is a comprehensive system for extracting structured data from PDF invoices using advanced OCR techniques. The system consists of both command-line interface (CLI) and desktop graphical user interface (GUI) components, providing flexibility for different use cases. **The MVP is now complete with all core features fully functional.**

## 🎯 Architecture Goals

- **Modular Design**: Separate concerns into distinct modules
- **Extensibility**: Easy to add new parsers and features
- **Performance**: Efficient processing of large document volumes
- **Reliability**: Robust error handling and validation
- **User Experience**: Intuitive interfaces for both CLI and GUI users
- **Integration**: Seamless compatibility between CLI and GUI components

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OCR Invoice Parser System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   CLI Interface │    │   GUI Interface │    │   Core OCR   │ │
│  │                 │    │   (MVP Complete)│    │   Engine     │ │
│  │ • Parse Command │    │ • Main Window   │    │              │ │
│  │ • Batch Command │    │ • File Naming   │    │ • Tesseract  │ │
│  │ • Alias Mgmt    │    │ • Data Display  │    │ • Image Proc │ │
│  │ • Config Mgmt   │    │ • Settings      │    │ • Text Extr  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           └───────────────────────┼───────────────────────┘     │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Business Logic Layer                     │ │
│  │                                                             │ │
│  │ • Business Mapping Manager    • Amount Normalizer          │ │
│  │ • Fuzzy Matcher               • OCR Corrections            │ │
│  │ • Date Extractor              • Validation Engine          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     Parser Layer                            │ │
│  │                                                             │ │
│  │ • Invoice Parser             • Credit Card Parser          │ │
│  │ • Base Parser                • Custom Parser Support       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Data Layer                               │ │
│  │                                                             │ │
│  │ • JSON Configuration         • Business Alias Files        │ │
│  │ • CSV Export                 • Logging & Monitoring        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. OCR Engine (`core/`)

The heart of the system, responsible for converting PDF images to text.

**Key Components:**
- **Image Processor**: PDF to image conversion, preprocessing
- **Text Extractor**: OCR text extraction using Tesseract
- **OCR Engine**: Main orchestration and configuration

**Features:**
- Multi-page PDF support
- Image preprocessing for better OCR accuracy
- Configurable OCR parameters
- Error handling and retry logic

### 2. Parser Layer (`parsers/`)

Intelligent parsing of extracted text to identify structured data.

**Components:**
- **Base Parser**: Common parsing functionality
- **Invoice Parser**: Specialized for invoice documents
- **Credit Card Parser**: Specialized for credit card statements
- **Date Extractor**: Intelligent date parsing
- **Amount Normalizer**: Currency and amount processing

**Features:**
- Template-based parsing
- Confidence scoring
- Field validation
- Extensible parser architecture

### 3. Business Logic (`business/`)

Business-specific logic for data processing and validation.

**Components:**
- **Business Mapping Manager**: Company name aliases and matching
- **Fuzzy Matcher**: Approximate string matching
- **Validation Engine**: Data quality and business rule validation

**Features:**
- Intelligent company name matching
- Alias management system
- Data quality scoring
- Business rule enforcement

### 4. Utilities (`utils/`)

Shared utilities and helper functions.

**Components:**
- **File Manager**: File operations and naming
- **OCR Corrections**: Common OCR error corrections
- **Amount Normalizer**: Currency and amount processing
- **Fuzzy Matcher**: String similarity matching

## 🖥️ GUI Architecture (Sprint 4 ✅ COMPLETED)

### GUI Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    GUI Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Main Window   │    │   File Naming   │    │   Settings   │ │
│  │                 │    │   Widget        │    │   Panel      │ │
│  │ • Tab Manager   │    │ • Template      │    │ • OCR Config │ │
│  │ • Menu Bar      │    │   Builder       │    │ • Output Dir │ │
│  │ • Status Bar    │    │ • Live Preview  │    │ • Alias File │ │
│  │ • Filename      │    │ • Validation    │    └──────────────┘ │
│  │   Display       │    │ • Conflict      │             │       │
│  └─────────────────┘    │   Resolution    │             │       │
│           │             └─────────────────┘             │       │
│           │                       │                     │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Single PDF    │    │   Data Panel    │    │   PDF        │ │
│  │   Tab           │    │                 │    │   Preview    │ │
│  │                 │    │ • Extracted     │    │              │ │
│  │ • File Selection│    │   Data Table    │    │ • Zoom/Pan   │ │
│  │ • OCR Progress  │    │ • Confidence    │    │ • Page Nav   │ │
│  │ • Drag & Drop   │    │   Indicators    │    │ • Thumbnails │ │
│  │ • Rename Button │    │ • Export        │    └──────────────┘ │
│  │   (NEW)         │    │ • Clear         │                     │
│  └─────────────────┘    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key GUI Features (Sprint 4 ✅ COMPLETED)

#### 1. File Naming System
- **Template Builder**: Visual interface for creating naming patterns
- **Live Preview**: Real-time filename preview with validation
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Backup Options**: Configurable backup settings
- **Validation**: Real-time template and filename validation
- **Full Path Display**: Complete file paths in dialogs and status

#### 2. Single PDF Processing
- **File Selection**: Drag-and-drop or browse for PDF files
- **OCR Processing**: Background processing with progress indicators
- **Data Display**: Clean table-based display of extracted data
- **Export Capabilities**: Save results in JSON/CSV format
- **Quick Rename**: Direct access to file renaming from Single PDF tab
- **Persistent Filename**: Current filename displayed in status bar

#### 3. Settings Management
- **OCR Configuration**: Language and processing settings
- **Output Settings**: Default directories and file locations
- **Business Settings**: Alias file configuration
- **Integration**: Shared settings with CLI

#### 4. User Experience Enhancements
- **Consistent Theme**: Uniform blue/gray color scheme
- **Keyboard Shortcuts**: Quick access to common functions
- **Tooltips**: Helpful information on hover
- **Status Indicators**: Real-time feedback on all operations
- **Error Handling**: User-friendly error messages and validation

### GUI Technical Implementation

#### Technology Stack
- **Framework**: PyQt6 for cross-platform desktop application
- **Threading**: Background OCR processing to prevent UI freezing
- **Signals/Slots**: Event-driven architecture for responsive UI
- **Widgets**: Custom widgets for specialized functionality

#### Key Design Patterns
- **Model-View-Controller**: Separation of data, presentation, and logic
- **Observer Pattern**: Real-time updates between components
- **Factory Pattern**: Widget creation and management
- **Strategy Pattern**: Configurable parsing and validation

#### Integration Architecture
- **Shared Business Logic**: Uses same core modules as CLI
- **Data Format Compatibility**: Reads/writes same JSON/CSV formats
- **Configuration Sharing**: Settings compatible between CLI and GUI
- **File Management**: Same naming patterns and backup systems

## 🔄 Integration Architecture

### CLI-GUI Compatibility

The system maintains full compatibility between CLI and GUI:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Commands  │    │   Shared Data   │    │   GUI Interface │
│                 │    │   Layer         │    │                 │
│ • parse         │◄──►│ • JSON Config   │◄──►│ • File Naming   │
│ • batch         │    │ • Alias Files   │    │ • Data Display  │
│ • aliases       │    │ • Templates     │    │ • Settings      │
│ • config        │    │ • Validation    │    │ • Export        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Input    │───►│   OCR Engine    │───►│   Parser Layer  │
│                 │    │                 │    │                 │
│ • PDF Selection │    │ • Image Proc    │    │ • Data Extract  │
│ • Drag & Drop   │    │ • Text Extract  │    │ • Validation    │
│ • Batch Files   │    │ • Background    │    │ • Confidence    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Business      │◄───│   Data Display  │◄───│   File Naming   │
│   Logic         │    │                 │    │                 │
│                 │    │ • Table View    │    │ • Template      │
│ • Alias Match   │    │ • Confidence    │    │ • Preview       │
│ • Validation    │    │ • Export        │    │ • Rename        │
│ • Quality Score │    │ • Clear         │    │ • Backup        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧪 Testing Architecture

### Test Coverage

```
┌─────────────────────────────────────────────────────────────────┐
│                        Test Suite                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Unit Tests    │    │ Integration     │    │   GUI Tests  │ │
│  │                 │    │   Tests         │    │              │ │
│  │ • Core Logic    │    │ • End-to-End    │    │ • Widgets    │ │
│  │ • Parsers       │    │ • CLI-GUI       │    │ • Dialogs    │ │
│  │ • Business      │    │ • File Ops      │    │ • User Flow  │ │
│  │ • Utilities     │    │ • Data Format   │    │ • Error      │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           └───────────────────────┼───────────────────────┘     │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Quality Assurance                        │ │
│  │                                                             │ │
│  │ • Code Coverage    • Performance Tests    • User Testing   │ │
│  │ • Linting          • Memory Profiling     • Accessibility  │ │
│  │ • Type Checking    • Cross-Platform      • Error Handling  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Testing Technologies
- **pytest**: Core testing framework
- **pytest-qt**: GUI testing with PyQt6
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and test isolation

## 📊 Performance Architecture

### Processing Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Stage   │───►│ Processing      │───►│   Output Stage  │
│                 │    │   Stage         │    │                 │
│ • File Load     │    │ • OCR Engine    │    │ • Data Display  │
│ • Validation    │    │ • Parser        │    │ • File Rename   │
│ • Preprocessing │    │ • Business      │    │ • Export        │
│                 │    │   Logic         │    │ • Backup        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Background    │    │   Threading     │    │   User          │
│   Tasks         │    │   Management    │    │   Feedback      │
│                 │    │                 │    │                 │
│ • Image Proc    │    │ • OCR Thread    │    │ • Progress Bar  │
│ • File I/O      │    │ • UI Thread     │    │ • Status Msgs   │
│ • Data Export   │    │ • Signal/Slot   │    │ • Error Dialogs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Performance Optimizations
- **Background Processing**: OCR runs in separate thread
- **Memory Management**: Efficient image processing and cleanup
- **Caching**: Template and configuration caching
- **Lazy Loading**: Load components on demand

## 🔒 Security Architecture

### Data Protection
- **File Permissions**: Proper file access controls
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Secure error messages without data leakage
- **Backup Security**: Safe backup file handling

### Integration Security
- **Configuration Validation**: Secure configuration loading
- **Business Logic Isolation**: Protected business rule processing
- **File Operation Safety**: Safe file system operations

## 🚀 Deployment Architecture

### Distribution
- **Cross-Platform**: macOS, Windows, Linux support
- **Dependency Management**: pip-based package management
- **Virtual Environment**: Isolated Python environments
- **Configuration Management**: Environment-specific settings

### Development Workflow
- **Version Control**: Git-based development
- **CI/CD Pipeline**: Automated testing and quality checks
- **Documentation**: Comprehensive user and developer guides
- **Release Management**: Semantic versioning and changelog

---

## 📈 Future Architecture Considerations

### Scalability
- **Batch Processing**: Enhanced batch processing capabilities
- **Cloud Integration**: Potential cloud-based OCR services
- **API Development**: RESTful API for external integrations
- **Plugin System**: Extensible plugin architecture

### Performance Enhancements
- **GPU Acceleration**: GPU-based image processing
- **Parallel Processing**: Multi-core OCR processing
- **Caching Layer**: Intelligent result caching
- **Optimization**: Profile-driven performance improvements

### User Experience
- **Advanced UI**: Enhanced user interface components
- **Accessibility**: Improved accessibility features
- **Internationalization**: Multi-language support
- **Customization**: User-configurable interface

This architecture provides a solid foundation for the OCR Invoice Parser system, with the MVP now complete and ready for future enhancements and scaling.
