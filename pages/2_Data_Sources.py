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
    
    # Handle missing values
    if options.get('fill_missing'):
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype in ['object', 'string']:
                cleaned_df[col] = cleaned_df[col].fillna('Unknown')
            else:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
    
    # Remove duplicates
    if options.get('remove_duplicates'):
        cleaned_df = cleaned_df.drop_duplicates()
    
    # Parse dates
    if options.get('parse_dates') and options.get('date_columns'):
        for col in options['date_columns']:
            try:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col])
            except:
                st.warning(f"Could not parse dates in column: {col}")
    
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
                
                # Data cleaning options
                with st.expander("🧹 Data Cleaning Options"):
                    cleaning_col1, cleaning_col2 = st.columns(2)
                    
                    with cleaning_col1:
                        fill_missing = st.checkbox("Fill missing values", help="Fill numeric columns with median, text columns with 'Unknown'")
                        remove_duplicates = st.checkbox("Remove duplicate rows")
                    
                    with cleaning_col2:
                        parse_dates = st.checkbox("Parse date columns")
                        if parse_dates:
                            potential_date_cols = [col for col in df.columns if 
                                                 'date' in col.lower() or 'time' in col.lower() or
                                                 df[col].dtype == 'object']
                            date_columns = st.multiselect("Select date columns", potential_date_cols)
                        else:
                            date_columns = []
                    
                    # Apply cleaning if requested
                    if st.button("🧹 Clean Data", type="secondary"):
                        cleaning_options = {
                            'fill_missing': fill_missing,
                            'remove_duplicates': remove_duplicates,
                            'parse_dates': parse_dates,
                            'date_columns': date_columns
                        }
                        df = clean_dataframe(df, cleaning_options)
                        st.success("Data cleaning applied!")
                        st.rerun()
                
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
