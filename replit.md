# Overview

This is an advanced Data Analytics Platform built with Streamlit that allows users to create custom dashboards, manage data sources, and generate reports with AI-powered insights. The platform features real-time collaboration, drag-and-drop dashboard editing, embedded sharing capabilities, and intelligent data analysis. It provides an intuitive interface for uploading data, building interactive charts, applying advanced filters, and exporting dashboards in various formats including PDF. The platform is designed as a comprehensive analytics solution with modern collaboration features, theme customization, and AI-powered business insights.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page architecture and advanced UI components
- **Page Structure**: Main app entry point with dedicated pages for Dashboard Builder, Data Sources, Reports, and Deployment
- **Component System**: Modular components including:
  - AI-powered insights engine with OpenAI integration
  - Real-time collaboration features with user activity tracking
  - Drag-and-drop dashboard layout editor with grid-based positioning
  - Advanced theme management with dark mode support
  - Embedded sharing and iframe generation capabilities
- **State Management**: Session-based state management with collaboration features, theme persistence, and layout configurations
- **Advanced Features**: Tab-based interface design, visual grid editor, and real-time user activity simulation

## Data Processing Layer
- **Data Storage**: In-memory storage using session state with comprehensive metadata tracking and collaboration features
- **Data Validation**: Advanced data validation including:
  - Automatic data type detection and optimization
  - Missing value identification with multiple handling strategies
  - Duplicate detection and removal options
  - Data quality scoring and improvement suggestions
- **Data Transformation**: Enhanced data cleaning capabilities with:
  - Interactive before/after preview functionality
  - Auto-detection of date columns with confidence scoring
  - Column name standardization and cleaning suggestions
  - Multiple missing value handling strategies (median, mean, mode, zero, drop)
  - Data type optimization for memory efficiency
- **AI-Powered Analysis**: OpenAI integration for intelligent data insights including trend analysis, anomaly detection, and business intelligence recommendations

## Visualization Engine
- **Chart Library**: Enhanced Plotly Express and Plotly Graph Objects with theme integration
- **Chart Types**: Support for line charts, bar charts, scatter plots, pie charts, area charts, histograms, and box plots
- **Advanced Filtering**: Multi-dimensional filtering system including:
  - Date range filters with intelligent date column detection
  - Category-based filtering with dynamic option generation
  - Region-based filtering for geographical data analysis
  - Real-time filter application across all dashboard charts
- **Layout Management**: Drag-and-drop grid-based layout editor with:
  - Visual chart placement interface
  - Auto-arrangement and manual positioning options
  - Responsive grid system with configurable dimensions
  - Layout export/import functionality
- **Theme Integration**: Dynamic theming with dark/light mode support and custom color schemes
- **Real-time Updates**: Dynamic chart generation with collaboration tracking and filter state persistence

## Export and Reporting
- **Image Export**: Chart export to PNG and other image formats using Plotly IO with theme-aware styling
- **PDF Generation**: Comprehensive dashboard reports using ReportLab with custom styling and AI insights integration
- **Data Export**: CSV and JSON export capabilities for data sources and dashboard configurations
- **Advanced Sharing**: Embedded dashboard capabilities including:
  - iframe generation for external website embedding
  - Shareable links with access control (view/edit/admin permissions)
  - Password protection and expiration settings for secure sharing
  - Collaborative sharing with real-time user activity tracking
- **Package Export**: Complete deployment packages with documentation, requirements, and configuration files

## Application Flow
- **Data Ingestion**: Enhanced file upload with comprehensive validation and interactive cleaning preview
- **Dashboard Creation**: Advanced visual dashboard builder featuring:
  - Multi-tab interface (Chart Builder, Layout Editor, AI Insights, Share & Embed, Settings)
  - Drag-and-drop chart configuration and positioning
  - Real-time collaboration with user activity tracking
  - AI-powered insights and business intelligence recommendations
- **Advanced Filtering**: Interactive filtering system with date, category, and region-based filtering
- **Theme Customization**: Dark/light mode toggle with advanced theme settings and custom CSS support
- **Collaboration Features**: Real-time multi-user editing simulation with activity tracking and sharing capabilities
- **Report Generation**: AI-enhanced automated report creation with embedded charts, insights, and data summaries
- **Deployment Preparation**: Comprehensive deployment tools with Replit integration, export packages, and settings management

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework for the user interface with advanced component integration
- **Pandas**: Data manipulation and analysis library with enhanced data cleaning capabilities
- **NumPy**: Numerical computing support for data operations and statistical analysis
- **OpenAI**: AI-powered insights generation and intelligent data analysis (requires API key)

## Visualization
- **Plotly Express**: High-level charting interface for quick visualizations
- **Plotly Graph Objects**: Low-level charting API for custom chart configurations
- **Plotly IO**: Chart export and image generation capabilities

## Document Generation
- **ReportLab**: PDF generation library for creating formatted reports
- **ReportLab Platypus**: Document layout engine for complex PDF documents

## Utility Libraries
- **datetime**: Date and time handling for timestamps and data processing
- **json**: Configuration serialization and data exchange
- **uuid**: Unique identifier generation for dashboards and components
- **hashlib**: Data integrity verification through hash generation
- **tempfile**: Temporary file management for export operations
- **base64**: Binary data encoding for file downloads and exports
- **io**: Stream handling for file operations and data processing
- **zipfile**: Archive creation for bulk exports
- **pickle**: Object serialization for complex data structures
- **re**: Regular expression support for data pattern matching