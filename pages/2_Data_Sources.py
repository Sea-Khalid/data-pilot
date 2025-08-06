import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import json

st.set_page_config(page_title="Data Sources", page_icon="📁", layout="wide")

def validate_dataframe(df, filename):
    """Validate uploaded dataframe and return validation results"""
    issues = []
    suggestions = []
    
    # Check for empty dataframe
    if df.empty:
        issues.append("❌ File is empty")
        return issues, suggestions
    
    # Check column names
    if df.columns.duplicated().any():
        issues.append("❌ Duplicate column names found")
    
    # Check for missing values
    missing_cols = df.columns[df.isnull().any()].tolist()
    if missing_cols:
        suggestions.append(f"⚠️ Missing values found in columns: {', '.join(missing_cols[:5])}")
    
    # Check data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=['object']).columns
    
    suggestions.append(f"✅ Found {len(numeric_cols)} numeric columns and {len(text_cols)} text columns")
    
    # Suggest date parsing
    potential_date_cols = [col for col in text_cols if 'date' in col.lower() or 'time' in col.lower()]
    if potential_date_cols:
        suggestions.append(f"💡 Potential date columns detected: {', '.join(potential_date_cols)}")
    
    return issues, suggestions

def clean_dataframe(df, options):
    """Apply cleaning operations to dataframe based on user selections"""
    cleaned_df = df.copy()
    
    # Remove completely empty rows
    if options.get('remove_empty'):
        cleaned_df = cleaned_df.dropna(how='all')
    
    # Handle missing values
    if options.get('fill_missing'):
        missing_strategy = options.get('missing_strategy', 'median')
        missing_text_strategy = options.get('missing_text_strategy', 'Unknown')
        
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype in ['object', 'string']:
                if missing_text_strategy == 'Unknown':
                    cleaned_df[col] = cleaned_df[col].fillna('Unknown')
                elif missing_text_strategy == 'most_frequent':
                    mode_val = cleaned_df[col].mode()
                    fill_val = mode_val[0] if not mode_val.empty else 'Unknown'
                    cleaned_df[col] = cleaned_df[col].fillna(fill_val)
                elif missing_text_strategy == 'drop_rows':
                    cleaned_df = cleaned_df.dropna(subset=[col])
            else:
                if missing_strategy == 'median':
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                elif missing_strategy == 'mean':
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
                elif missing_strategy == 'zero':
                    cleaned_df[col] = cleaned_df[col].fillna(0)
                elif missing_strategy == 'drop_rows':
                    cleaned_df = cleaned_df.dropna(subset=[col])
    
    # Remove duplicates
    if options.get('remove_duplicates'):
        cleaned_df = cleaned_df.drop_duplicates()
    
    # Apply column renaming
    if options.get('apply_column_rename'):
        # Apply suggested clean names
        new_columns = {}
        for col in cleaned_df.columns:
            clean_name = col.strip().replace(' ', '_').replace('-', '_').lower()
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
            new_columns[col] = clean_name
        cleaned_df = cleaned_df.rename(columns=new_columns)
    
    # Parse dates
    if options.get('parse_dates') and options.get('date_columns'):
        for col in options['date_columns']:
            try:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
            except Exception as e:
                st.warning(f"Could not parse dates in column {col}: {str(e)}")
    
    # Optimize data types
    if options.get('optimize_types'):
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    numeric_col = pd.to_numeric(cleaned_df[col], errors='raise')
                    # Check if it's actually integer
                    if numeric_col.equals(numeric_col.astype('int64')):
                        cleaned_df[col] = numeric_col.astype('int64')
                    else:
                        cleaned_df[col] = numeric_col
                except:
                    # Check if it should be categorical
                    if cleaned_df[col].nunique() / len(cleaned_df) < 0.1:  # Less than 10% unique values
                        cleaned_df[col] = cleaned_df[col].astype('category')
    
    return cleaned_df

def main():
    st.title("📁 Data Sources Management")
    st.markdown("Upload and manage your data sources for dashboard creation")
    
    # Initialize session state
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    tab1, tab2, tab3 = st.tabs(["Upload Data", "Manage Sources", "Data Preview"])
    
    with tab1:
        st.header("📤 Upload New Data Source")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload CSV files to use as data sources for your dashboards"
        )
        
        if uploaded_file is not None:
            try:
                # Read the file
                df = pd.read_csv(uploaded_file)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(f"Preview: {uploaded_file.name}")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Data info
                    st.subheader("Data Information")
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.metric("Rows", len(df))
                    with info_col2:
                        st.metric("Columns", len(df.columns))
                    with info_col3:
                        st.metric("Missing Values", df.isnull().sum().sum())
                
                with col2:
                    st.subheader("Data Validation")
                    
                    # Validate the data
                    issues, suggestions = validate_dataframe(df, uploaded_file.name)
                    
                    if issues:
                        st.error("Issues Found:")
                        for issue in issues:
                            st.write(issue)
                    else:
                        st.success("✅ No critical issues found!")
                    
                    if suggestions:
                        st.info("Suggestions:")
                        for suggestion in suggestions:
                            st.write(suggestion)
                
                # Enhanced Data cleaning options with preview
                with st.expander("🧹 Data Cleaning & Transformation", expanded=True):
                    st.markdown("### Preview and clean your data before saving")
                    
                    # Create tabs for different cleaning operations
                    clean_tab1, clean_tab2, clean_tab3, clean_tab4 = st.tabs(["🗑️ Clean Data", "📝 Rename Columns", "📅 Auto-Detect Dates", "👁️ Preview Changes"])
                    
                    with clean_tab1:
                        st.subheader("Data Cleaning Options")
                        cleaning_col1, cleaning_col2 = st.columns(2)
                        
                        with cleaning_col1:
                            # Missing values section
                            st.write("**Missing Values:**")
                            fill_missing = st.checkbox("Fill missing values", help="Fill numeric columns with median, text columns with 'Unknown'")
                            if fill_missing:
                                missing_strategy = st.selectbox("Strategy for numeric columns", ["median", "mean", "zero", "drop_rows"])
                                missing_text_strategy = st.selectbox("Strategy for text columns", ["Unknown", "most_frequent", "drop_rows"])
                            
                            # Duplicates section  
                            st.write("**Duplicate Rows:**")
                            remove_duplicates = st.checkbox("Remove duplicate rows")
                            if remove_duplicates:
                                duplicate_count = df.duplicated().sum()
                                if duplicate_count > 0:
                                    st.info(f"Found {duplicate_count} duplicate rows")
                                else:
                                    st.success("No duplicates found")
                        
                        with cleaning_col2:
                            # Empty rows section
                            st.write("**Empty Rows:**")
                            remove_empty = st.checkbox("Remove completely empty rows")
                            
                            # Data type optimization
                            st.write("**Data Types:**")
                            optimize_types = st.checkbox("Optimize data types automatically")
                            if optimize_types:
                                st.info("Will convert text numbers to numeric, optimize memory usage")
                            
                            # Outlier detection
                            st.write("**Outliers:**")
                            remove_outliers = st.checkbox("Detect and flag outliers")
                            if remove_outliers:
                                outlier_method = st.selectbox("Method", ["IQR", "Z-score"])
                                outlier_threshold = st.slider("Threshold", 1.0, 3.0, 1.5)
                    
                    with clean_tab2:
                        st.subheader("Rename Columns")
                        st.write("Clean up column names for better usability")
                        
                        # Show current column names and suggested improvements
                        col_rename_data = []
                        for col in df.columns:
                            # Suggest cleaned column name
                            clean_name = col.strip().replace(' ', '_').replace('-', '_').lower()
                            clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
                            col_rename_data.append([col, clean_name])
                        
                        if col_rename_data:
                            rename_df = pd.DataFrame(col_rename_data, columns=["Original Name", "Suggested Name"])
                            st.dataframe(rename_df, use_container_width=True)
                            
                            apply_column_rename = st.checkbox("Apply suggested column name cleaning")
                            custom_renames = st.text_area(
                                "Custom renames (format: old_name->new_name, one per line)", 
                                placeholder="Sales Data->sales\nCustomer ID->customer_id"
                            )
                    
                    with clean_tab3:
                        st.subheader("Auto-Detect Date Columns")
                        
                        # Analyze columns for date patterns
                        potential_date_cols = []
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                sample_values = df[col].dropna().head(10).astype(str)
                                date_like_patterns = 0
                                
                                for value in sample_values:
                                    # Check common date patterns
                                    import re
                                    patterns = [
                                        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                                        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                                        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
                                        r'\w+ \d{1,2}, \d{4}', # Month DD, YYYY
                                    ]
                                    
                                    if any(re.search(pattern, value) for pattern in patterns):
                                        date_like_patterns += 1
                                
                                confidence = date_like_patterns / len(sample_values) if len(sample_values) > 0 else 0
                                if confidence > 0.5:  # More than 50% look like dates
                                    potential_date_cols.append((col, confidence))
                        
                        if potential_date_cols:
                            st.write("**Detected potential date columns:**")
                            for col, confidence in potential_date_cols:
                                st.write(f"• **{col}** (confidence: {confidence:.1%})")
                                # Show sample values
                                sample_vals = df[col].dropna().head(3).tolist()
                                st.write(f"  Sample: {sample_vals}")
                            
                            parse_dates = st.checkbox("Convert detected date columns to datetime")
                            if parse_dates:
                                date_columns = st.multiselect(
                                    "Select columns to convert", 
                                    [col for col, conf in potential_date_cols],
                                    default=[col for col, conf in potential_date_cols if conf > 0.8]
                                )
                        else:
                            st.info("No potential date columns detected")
                            parse_dates = False
                            date_columns = []
                    
                    with clean_tab4:
                        st.subheader("Preview Cleaned Data")
                        
                        # Build cleaning options based on user selections
                        cleaning_options = {
                            'fill_missing': fill_missing if 'fill_missing' in locals() else False,
                            'remove_duplicates': remove_duplicates if 'remove_duplicates' in locals() else False,
                            'remove_empty': remove_empty if 'remove_empty' in locals() else False,
                            'parse_dates': parse_dates if 'parse_dates' in locals() else False,
                            'date_columns': date_columns if 'date_columns' in locals() else [],
                            'optimize_types': optimize_types if 'optimize_types' in locals() else False,
                            'apply_column_rename': apply_column_rename if 'apply_column_rename' in locals() else False
                        }
                        
                        # Show before/after comparison
                        if any(cleaning_options.values()):
                            preview_df = clean_dataframe(df.copy(), cleaning_options)
                            
                            st.write("**Before/After Comparison:**")
                            comparison_col1, comparison_col2 = st.columns(2)
                            
                            with comparison_col1:
                                st.write("**Original Data:**")
                                st.dataframe(df.head(), use_container_width=True)
                                st.write(f"Shape: {df.shape}")
                                st.write(f"Missing values: {df.isnull().sum().sum()}")
                            
                            with comparison_col2:
                                st.write("**Cleaned Data:**")
                                st.dataframe(preview_df.head(), use_container_width=True)
                                st.write(f"Shape: {preview_df.shape}")
                                st.write(f"Missing values: {preview_df.isnull().sum().sum()}")
                                
                                # Show changes summary
                                changes = []
                                if df.shape[0] != preview_df.shape[0]:
                                    changes.append(f"Rows: {df.shape[0]} → {preview_df.shape[0]}")
                                if df.isnull().sum().sum() != preview_df.isnull().sum().sum():
                                    changes.append(f"Missing values: {df.isnull().sum().sum()} → {preview_df.isnull().sum().sum()}")
                                
                                if changes:
                                    st.success("Changes: " + ", ".join(changes))
                        else:
                            st.info("Select cleaning options above to see preview")
                    
                    # Apply cleaning button
                    st.divider()
                    apply_col1, apply_col2 = st.columns([1, 1])
                    
                    with apply_col1:
                        if st.button("🧹 Apply All Selected Cleaning", type="primary"):
                            try:
                                cleaning_options = {
                                    'fill_missing': fill_missing if 'fill_missing' in locals() else False,
                                    'remove_duplicates': remove_duplicates if 'remove_duplicates' in locals() else False,
                                    'remove_empty': remove_empty if 'remove_empty' in locals() else False,
                                    'parse_dates': parse_dates if 'parse_dates' in locals() else False,
                                    'date_columns': date_columns if 'date_columns' in locals() else [],
                                    'optimize_types': optimize_types if 'optimize_types' in locals() else False,
                                    'apply_column_rename': apply_column_rename if 'apply_column_rename' in locals() else False
                                }
                                
                                df = clean_dataframe(df, cleaning_options)
                                st.success("Data cleaning applied successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error during cleaning: {str(e)}")
                    
                    with apply_col2:
                        if st.button("↩️ Reset to Original", type="secondary"):
                            # Reset df to original uploaded state
                            df = pd.read_csv(uploaded_file)
                            st.info("Data reset to original state")
                
                # Save data source
                st.divider()
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    data_source_name = st.text_input(
                        "Data Source Name",
                        value=uploaded_file.name.replace('.csv', ''),
                        placeholder="Enter a name for this data source"
                    )
                
                with col2:
                    if st.button("💾 Save Data Source", type="primary"):
                        if data_source_name:
                            if data_source_name in st.session_state.data_sources:
                                if st.checkbox("Overwrite existing data source"):
                                    st.session_state.data_sources[data_source_name] = df
                                    st.success(f"Data source '{data_source_name}' updated!")
                                else:
                                    st.error("Data source name already exists!")
                            else:
                                st.session_state.data_sources[data_source_name] = df
                                st.success(f"Data source '{data_source_name}' saved!")
                        else:
                            st.error("Please enter a data source name!")
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please ensure your CSV file is properly formatted.")
    
    with tab2:
        st.header("🗂️ Manage Data Sources")
        
        if not st.session_state.data_sources:
            st.info("No data sources uploaded yet. Use the 'Upload Data' tab to add your first data source.")
        else:
            # Display existing data sources
            for i, (name, df) in enumerate(st.session_state.data_sources.items()):
                with st.expander(f"📊 {name}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Rows:** {len(df)} | **Columns:** {len(df.columns)}")
                        st.write(f"**Columns:** {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                    
                    with col2:
                        if st.button("👁️ Preview", key=f"preview_{i}"):
                            st.session_state.preview_source = name
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{i}", type="secondary"):
                            del st.session_state.data_sources[name]
                            st.success(f"Data source '{name}' deleted!")
                            st.rerun()
                    
                    # Show preview if selected
                    if st.session_state.get('preview_source') == name:
                        st.subheader("Data Preview")
                        st.dataframe(df.head(20), use_container_width=True)
                        
                        # Column statistics
                        st.subheader("Column Statistics")
                        stats_df = df.describe(include='all').transpose()
                        st.dataframe(stats_df, use_container_width=True)
    
    with tab3:
        st.header("📊 Data Preview & Analysis")
        
        if not st.session_state.data_sources:
            st.info("No data sources available for preview.")
        else:
            # Data source selector
            selected_source = st.selectbox("Select Data Source", list(st.session_state.data_sources.keys()))
            
            if selected_source:
                df = st.session_state.data_sources[selected_source]
                
                # Data overview
                overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
                
                with overview_col1:
                    st.metric("Total Rows", len(df))
                with overview_col2:
                    st.metric("Total Columns", len(df.columns))
                with overview_col3:
                    st.metric("Numeric Columns", len(df.select_dtypes(include=[np.number]).columns))
                with overview_col4:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                # Data sample and column info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Data Sample")
                    sample_size = st.slider("Sample Size", 5, min(100, len(df)), 10)
                    st.dataframe(df.head(sample_size), use_container_width=True)
                
                with col2:
                    st.subheader("Column Information")
                    for col in df.columns:
                        with st.container():
                            st.write(f"**{col}**")
                            st.write(f"Type: {df[col].dtype}")
                            st.write(f"Non-null: {df[col].notna().sum()}")
                            if df[col].dtype in ['object', 'category']:
                                st.write(f"Unique: {df[col].nunique()}")
                            st.divider()
                
                # Quick statistics for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.subheader("Numeric Column Statistics")
                    stats_df = df[numeric_cols].describe()
                    st.dataframe(stats_df, use_container_width=True)
                
                # Data quality issues
                st.subheader("Data Quality Check")
                quality_col1, quality_col2 = st.columns(2)
                
                with quality_col1:
                    st.write("**Missing Values by Column:**")
                    missing_data = df.isnull().sum()
                    missing_data = missing_data[missing_data > 0]
                    if len(missing_data) > 0:
                        st.dataframe(missing_data.to_frame("Missing Count"), use_container_width=True)
                    else:
                        st.success("No missing values found!")
                
                with quality_col2:
                    st.write("**Duplicate Rows:**")
                    duplicates = df.duplicated().sum()
                    if duplicates > 0:
                        st.warning(f"Found {duplicates} duplicate rows")
                    else:
                        st.success("No duplicate rows found!")
                
                # Export options
                st.divider()
                st.subheader("Export Options")
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    if st.button("📥 Download as CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{selected_source}.csv",
                            mime="text/csv"
                        )
                
                with export_col2:
                    if st.button("📊 Create Dashboard"):
                        st.session_state.selected_data_source = selected_source
                        st.switch_page("pages/1_Dashboard_Builder.py")

if __name__ == "__main__":
    main()
