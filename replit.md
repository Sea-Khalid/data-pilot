# Overview

This is a Data Analytics Platform built with Streamlit that allows users to create custom dashboards, manage data sources, and generate reports. The platform provides an intuitive interface for uploading data, building interactive charts, and exporting dashboards in various formats including PDF. It's designed as a self-contained analytics solution with session-based data management and real-time visualization capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page architecture
- **Page Structure**: Main app entry point with dedicated pages for Dashboard Builder, Data Sources, and Reports
- **Component System**: Modular components for chart building, data processing, and export utilities
- **State Management**: Session-based state management using Streamlit's session state for dashboards, data sources, and user preferences

## Data Processing Layer
- **Data Storage**: In-memory storage using session state with metadata tracking
- **Data Validation**: Automatic data type detection, missing value identification, and data quality suggestions
- **Data Transformation**: Built-in data cleaning capabilities including missing value handling and type conversion
- **Caching System**: Hash-based data integrity checking and caching mechanisms

## Visualization Engine
- **Chart Library**: Plotly Express and Plotly Graph Objects for interactive visualizations
- **Chart Types**: Support for line charts, bar charts, scatter plots, pie charts, area charts, histograms, and box plots
- **Customization**: Configurable chart properties including dimensions, colors, legends, and styling options
- **Real-time Updates**: Dynamic chart generation based on user selections and data changes

## Export and Reporting
- **Image Export**: Chart export to PNG and other image formats using Plotly IO
- **PDF Generation**: Comprehensive dashboard reports using ReportLab with custom styling
- **Data Export**: CSV and JSON export capabilities for data sources and dashboard configurations
- **Multi-format Support**: Flexible export options for different use cases and sharing requirements

## Application Flow
- **Data Ingestion**: File upload and validation through the Data Sources page
- **Dashboard Creation**: Visual dashboard builder with drag-and-drop chart configuration
- **Report Generation**: Automated report creation with embedded charts and data summaries
- **State Persistence**: Session-based persistence with dashboard and data source management utilities

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing support for data operations

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