# OCR Invoice Parser - System Architecture

> **High-level system design and architecture overview**

## 🏗️ System Overview

The OCR Invoice Parser is a comprehensive system for extracting structured data from PDF invoices using advanced OCR techniques. The system consists of both command-line interface (CLI) and desktop graphical user interface (GUI) components, providing flexibility for different use cases.

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
│  │                 │    │                 │    │   Engine     │ │
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

## 🖥️ GUI Architecture (Sprint 3 Completed ✅)

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
│  └─────────────────┘    │ • Validation    │    └──────────────┘ │
│           │             └─────────────────┘             │       │
│           │                       │                     │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Single PDF    │    │   Data Panel    │    │   PDF        │ │
│  │   Tab           │    │                 │    │   Preview    │ │
│  │                 │    │ • Extracted     │    │              │ │
│  │ • File Selection│    │   Data Table    │    │ • Zoom/Pan   │ │
│  │ • OCR Progress  │    │ • Confidence    │    │ • Page Nav   │ │
│  │ • Drag & Drop   │    │   Indicators    │    │ • Thumbnails │ │
│  └─────────────────┘    │ • Export        │    └──────────────┘ │
│                         └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key GUI Features (Sprint 3)

#### 1. File Naming System
- **Template Builder**: Visual interface for creating naming patterns
- **Live Preview**: Real-time filename preview with validation
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Backup Options**: Configurable backup settings
- **Validation**: Real-time template and filename validation

#### 2. Single PDF Processing
- **File Selection**: Drag-and-drop or browse for PDF files
- **OCR Processing**: Background processing with progress indicators
- **Data Display**: Clean table-based display of extracted data
- **Export Capabilities**: Save results in JSON/CSV format

#### 3. Settings Management
- **OCR Configuration**: Language and processing settings
- **Output Settings**: Default directories and file locations
- **Business Settings**: Alias file configuration
- **Integration**: Shared settings with CLI

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

### Data Flow

1. **Configuration**: Shared JSON configuration files
2. **Business Aliases**: Same alias system for both interfaces
3. **File Management**: Compatible naming templates and options
4. **Data Formats**: Identical JSON/CSV output formats
5. **Validation**: Shared validation rules and error handling

## 📊 Performance Architecture

### Processing Pipeline

```
PDF Input → Image Processing → OCR Extraction → Text Parsing → Data Validation → Output
     │              │                │              │              │            │
     ▼              ▼                ▼              ▼              ▼            ▼
File Manager → Image Processor → OCR Engine → Parser Layer → Validation → Export
```

### Optimization Strategies

1. **Background Processing**: Non-blocking OCR in GUI
2. **Caching**: Template and configuration caching
3. **Batch Processing**: Optimized for multiple files
4. **Memory Management**: Efficient image and data handling
5. **Error Recovery**: Graceful handling of processing failures

## 🔒 Security & Reliability

### Error Handling
- **Graceful Degradation**: Continue processing on partial failures
- **User Feedback**: Clear error messages and status updates
- **Logging**: Comprehensive logging for debugging
- **Validation**: Input validation and sanitization

### Data Integrity
- **Backup Systems**: Automatic backup before file operations
- **Validation**: Multi-layer data validation
- **Confidence Scoring**: Quality assessment of extracted data
- **Conflict Resolution**: Smart handling of file conflicts

## 🚀 Scalability Considerations

### Horizontal Scaling
- **Batch Processing**: Efficient handling of large file volumes
- **Parallel Processing**: Multi-threaded OCR processing
- **Resource Management**: Memory and CPU optimization

### Vertical Scaling
- **Modular Architecture**: Easy to add new parsers and features
- **Plugin System**: Extensible architecture for custom functionality
- **Configuration**: Flexible configuration for different environments

## 🔮 Future Architecture

### Planned Enhancements
- **Batch Processing GUI**: Visual interface for batch operations
- **Search & Filter**: Advanced PDF search capabilities
- **Cloud Integration**: Remote processing and storage
- **API Layer**: RESTful API for external integrations
- **Plugin System**: Third-party extension support

### Technology Evolution
- **AI/ML Integration**: Enhanced OCR accuracy with machine learning
- **Cloud Processing**: Distributed OCR processing
- **Real-time Collaboration**: Multi-user editing and sharing
- **Mobile Support**: Mobile application for field use

## 📋 Development Guidelines

### Code Organization
- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Injection**: Loose coupling between components
- **Interface Design**: Well-defined APIs between modules
- **Error Handling**: Consistent error handling patterns

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component testing
- **GUI Tests**: Automated UI testing with pytest-qt
- **Performance Tests**: Load and stress testing

### Documentation Standards
- **API Documentation**: Comprehensive docstrings
- **Architecture Documentation**: System design documentation
- **User Guides**: End-user documentation
- **Developer Guides**: Technical implementation guides

---

**Architecture Summary**: The OCR Invoice Parser system provides a robust, scalable, and user-friendly solution for PDF invoice processing, with seamless integration between CLI and GUI interfaces, comprehensive error handling, and extensible architecture for future enhancements.
