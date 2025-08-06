import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid

st.set_page_config(page_title="Dashboard Builder", page_icon="📊", layout="wide")

# Import utility functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_dashboard_filters(df, filters):
    """Apply dashboard filters to dataframe"""
    if not filters:
        return df
    
    filtered_df = df.copy()
    
    try:
        # Apply date filters
        if 'date_column' in filters and 'date_range' in filters:
            date_col = filters['date_column']
            date_range = filters['date_range']
            
            if date_col in filtered_df.columns and len(date_range) == 2:
                # Convert date column to datetime if needed
                if not filtered_df[date_col].dtype.name.startswith('datetime'):
                    filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
                
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                filtered_df = filtered_df[
                    (filtered_df[date_col] >= start_date) & 
                    (filtered_df[date_col] <= end_date)
                ]
        
        # Apply category filters
        if 'category_column' in filters and 'categories' in filters:
            cat_col = filters['category_column']
            categories = filters['categories']
            
            if cat_col in filtered_df.columns and categories:
                filtered_df = filtered_df[filtered_df[cat_col].isin(categories)]
        
        # Apply region filters
        if 'region_column' in filters and 'regions' in filters:
            region_col = filters['region_column']
            regions = filters['regions']
            
            if region_col in filtered_df.columns and regions:
                filtered_df = filtered_df[filtered_df[region_col].isin(regions)]
        
        return filtered_df
    
    except Exception as e:
        st.warning(f"Error applying filters: {str(e)}")
        return df

def create_chart(chart_type, data, x_col, y_col, color_col=None, title="Chart"):
    """Create a plotly chart based on type and parameters"""
    try:
        if chart_type == "Line Chart":
            fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Bar Chart":
            fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Pie Chart":
            if color_col:
                fig = px.pie(data, values=y_col, names=color_col, title=title)
            else:
                fig = px.pie(data, values=y_col, names=x_col, title=title)
        elif chart_type == "Area Chart":
            fig = px.area(data, x=x_col, y=y_col, color=color_col, title=title)
        else:
            return None
        
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

def main():
    st.title("📊 Dashboard Builder")
    
    # Initialize session state
    if 'dashboards' not in st.session_state:
        st.session_state.dashboards = {}
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    # Sidebar - Dashboard Management
    with st.sidebar:
        st.header("Dashboard Management")
        
        # Dashboard selection
        dashboard_options = ["Create New"] + list(st.session_state.dashboards.keys())
        selected_dashboard = st.selectbox("Select Dashboard", dashboard_options)
        
        if selected_dashboard == "Create New":
            new_dashboard_name = st.text_input("Dashboard Name", placeholder="Enter dashboard name")
            if st.button("Create Dashboard") and new_dashboard_name:
                if new_dashboard_name not in st.session_state.dashboards:
                    st.session_state.dashboards[new_dashboard_name] = {
                        'created': datetime.now().isoformat(),
                        'charts': {},
                        'layout': 'default',
                        'filters': {}
                    }
                    st.session_state.current_dashboard = new_dashboard_name
                    st.success(f"Dashboard '{new_dashboard_name}' created!")
                    st.rerun()
                else:
                    st.error("Dashboard name already exists!")
        else:
            st.session_state.current_dashboard = selected_dashboard
        
        if st.session_state.current_dashboard and st.session_state.current_dashboard in st.session_state.dashboards:
            st.divider()
            
            # Dashboard actions
            if st.button("🗑️ Delete Dashboard", type="secondary"):
                if st.session_state.current_dashboard in st.session_state.dashboards:
                    del st.session_state.dashboards[st.session_state.current_dashboard]
                    st.session_state.current_dashboard = None
                    st.success("Dashboard deleted!")
                    st.rerun()
            
            # Dashboard info
            dashboard_info = st.session_state.dashboards[st.session_state.current_dashboard]
            st.metric("Charts", len(dashboard_info.get('charts', {})))
            st.caption(f"Created: {dashboard_info.get('created', 'Unknown')[:10]}")
    
    # Main content
    if not st.session_state.data_sources:
        st.warning("⚠️ No data sources available. Please upload data first!")
        if st.button("Go to Data Sources"):
            st.switch_page("pages/2_Data_Sources.py")
        return
    
    if not st.session_state.current_dashboard or st.session_state.current_dashboard not in st.session_state.dashboards:
        st.info("👈 Please select or create a dashboard from the sidebar to get started.")
        
        # Show available data sources
        st.subheader("Available Data Sources")
        for name, df in st.session_state.data_sources.items():
            with st.expander(f"📁 {name} ({len(df)} rows, {len(df.columns)} columns)"):
                st.dataframe(df.head(), use_container_width=True)
        return
    
    # Dashboard builder interface
    current_dashboard = st.session_state.dashboards[st.session_state.current_dashboard]
    st.subheader(f"Building: {st.session_state.current_dashboard}")
    
    # Chart builder section
    with st.expander("➕ Add New Chart", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Data source selection
            data_source = st.selectbox("Select Data Source", list(st.session_state.data_sources.keys()))
            
            if data_source:
                df = st.session_state.data_sources[data_source]
                
                # Chart configuration
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    chart_type = st.selectbox("Chart Type", [
                        "Line Chart", "Bar Chart", "Pie Chart", "Scatter Plot", "Area Chart"
                    ])
                    x_column = st.selectbox("X-Axis", df.columns)
                    
                with chart_col2:
                    if chart_type != "Pie Chart":
                        y_column = st.selectbox("Y-Axis", df.select_dtypes(include=['number']).columns)
                    else:
                        y_column = st.selectbox("Values", df.select_dtypes(include=['number']).columns)
                    
                    color_column = st.selectbox("Color By (Optional)", 
                                              ["None"] + list(df.select_dtypes(include=['object', 'category']).columns))
                    if color_column == "None":
                        color_column = None
                
                # Chart title and preview
                chart_title = st.text_input("Chart Title", value=f"{chart_type} - {x_column} vs {y_column}")
                
        with col2:
            st.subheader("Chart Preview")
            
            if data_source and x_column and y_column:
                # Apply basic data aggregation for better visualization
                preview_df = df.copy()
                
                # For categorical x-axis, aggregate y values
                if df[x_column].dtype == 'object' or df[x_column].dtype.name == 'category':
                    if chart_type != "Scatter Plot":
                        preview_df = df.groupby(x_column)[y_column].sum().reset_index()
                        if color_column and color_column in df.columns:
                            preview_df = df.groupby([x_column, color_column])[y_column].sum().reset_index()
                
                # Limit data points for better performance
                if len(preview_df) > 1000:
                    preview_df = preview_df.sample(1000)
                
                preview_fig = create_chart(chart_type, preview_df, x_column, y_column, color_column, chart_title)
                if preview_fig:
                    preview_fig.update_layout(height=250)
                    st.plotly_chart(preview_fig, use_container_width=True)
        
        # Add chart to dashboard
        if st.button("Add Chart to Dashboard", type="primary"):
            if data_source and x_column and y_column:
                chart_id = str(uuid.uuid4())
                current_dashboard['charts'][chart_id] = {
                    'type': chart_type,
                    'data_source': data_source,
                    'x_column': x_column,
                    'y_column': y_column,
                    'color_column': color_column,
                    'title': chart_title,
                    'created': datetime.now().isoformat()
                }
                st.success(f"Chart '{chart_title}' added to dashboard!")
                st.rerun()
    
    # Display current dashboard
    if current_dashboard.get('charts'):
        st.divider()
        st.subheader("Dashboard Preview")
        
        # Enhanced Dashboard filters
        with st.expander("🔍 Dashboard Filters", expanded=False):
            st.markdown("Apply filters to all charts in this dashboard:")
            
            # Initialize filter state
            if 'dashboard_filters' not in st.session_state:
                st.session_state.dashboard_filters = {}
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            # Collect all available filter options from data sources used in dashboard
            all_date_columns = set()
            all_category_columns = set()
            all_region_columns = set()
            
            for chart_config in current_dashboard['charts'].values():
                data_source_name = chart_config['data_source']
                if data_source_name in st.session_state.data_sources:
                    df = st.session_state.data_sources[data_source_name]
                    
                    # Date columns
                    date_cols = [col for col in df.columns if 
                                df[col].dtype.name.startswith('datetime') or 
                                'date' in col.lower()]
                    all_date_columns.update(date_cols)
                    
                    # Category columns (text/object columns)
                    cat_cols = [col for col in df.columns if 
                               df[col].dtype == 'object' and 
                               ('category' in col.lower() or 'type' in col.lower() or 'class' in col.lower())]
                    all_category_columns.update(cat_cols)
                    
                    # Region columns
                    region_cols = [col for col in df.columns if 
                                  df[col].dtype == 'object' and 
                                  ('region' in col.lower() or 'location' in col.lower() or 'area' in col.lower())]
                    all_region_columns.update(region_cols)
            
            with filter_col1:
                st.subheader("📅 Date Filters")
                if all_date_columns:
                    selected_date_col = st.selectbox("Date Column", ["None"] + list(all_date_columns))
                    if selected_date_col != "None":
                        date_range = st.date_input(
                            "Select Date Range",
                            value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
                            key="dashboard_date_filter"
                        )
                        st.session_state.dashboard_filters['date_column'] = selected_date_col
                        st.session_state.dashboard_filters['date_range'] = date_range
                else:
                    st.info("No date columns found in data")
            
            with filter_col2:
                st.subheader("📊 Category Filters")
                if all_category_columns:
                    selected_cat_col = st.selectbox("Category Column", ["None"] + list(all_category_columns))
                    if selected_cat_col != "None":
                        # Get unique values for selected category column
                        cat_values = set()
                        for chart_config in current_dashboard['charts'].values():
                            data_source_name = chart_config['data_source']
                            if data_source_name in st.session_state.data_sources:
                                df = st.session_state.data_sources[data_source_name]
                                if selected_cat_col in df.columns:
                                    cat_values.update(df[selected_cat_col].dropna().unique())
                        
                        selected_categories = st.multiselect(
                            "Select Categories",
                            options=list(cat_values),
                            key="dashboard_category_filter"
                        )
                        st.session_state.dashboard_filters['category_column'] = selected_cat_col
                        st.session_state.dashboard_filters['categories'] = selected_categories
                else:
                    st.info("No category columns found")
            
            with filter_col3:
                st.subheader("🗺️ Region Filters")
                if all_region_columns:
                    selected_region_col = st.selectbox("Region Column", ["None"] + list(all_region_columns))
                    if selected_region_col != "None":
                        # Get unique values for selected region column
                        region_values = set()
                        for chart_config in current_dashboard['charts'].values():
                            data_source_name = chart_config['data_source']
                            if data_source_name in st.session_state.data_sources:
                                df = st.session_state.data_sources[data_source_name]
                                if selected_region_col in df.columns:
                                    region_values.update(df[selected_region_col].dropna().unique())
                        
                        selected_regions = st.multiselect(
                            "Select Regions",
                            options=list(region_values),
                            key="dashboard_region_filter"
                        )
                        st.session_state.dashboard_filters['region_column'] = selected_region_col
                        st.session_state.dashboard_filters['regions'] = selected_regions
                else:
                    st.info("No region columns found")
            
            # Clear filters button
            if st.button("🗑️ Clear All Filters", type="secondary"):
                st.session_state.dashboard_filters = {}
                st.rerun()
        
        # Display charts in grid layout
        charts = current_dashboard['charts']
        chart_keys = list(charts.keys())
        
        # Arrange charts in rows of 2
        for i in range(0, len(chart_keys), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(chart_keys):
                    chart_key = chart_keys[i + j]
                    chart_config = charts[chart_key]
                    
                    with col:
                        # Chart header with controls
                        chart_header_col1, chart_header_col2 = st.columns([3, 1])
                        
                        with chart_header_col1:
                            st.subheader(chart_config['title'])
                        
                        with chart_header_col2:
                            if st.button("🗑️", key=f"delete_{chart_key}", help="Delete chart"):
                                del current_dashboard['charts'][chart_key]
                                st.rerun()
                        
                        # Render chart with filters applied
                        try:
                            data_source = chart_config['data_source']
                            if data_source in st.session_state.data_sources:
                                df = st.session_state.data_sources[data_source]
                                
                                # Apply dashboard filters first
                                filtered_df = apply_dashboard_filters(df, st.session_state.get('dashboard_filters', {}))
                                
                                # Show filter status
                                if len(filtered_df) < len(df):
                                    st.caption(f"📊 Showing {len(filtered_df):,} of {len(df):,} records (filtered)")
                                
                                # Apply aggregation for better visualization
                                display_df = filtered_df.copy()
                                x_col = chart_config['x_column']
                                y_col = chart_config['y_column']
                                color_col = chart_config.get('color_column')
                                
                                if not display_df.empty:
                                    if filtered_df[x_col].dtype == 'object' and chart_config['type'] != "Scatter Plot":
                                        if color_col and color_col in filtered_df.columns:
                                            display_df = filtered_df.groupby([x_col, color_col])[y_col].sum().reset_index()
                                        else:
                                            display_df = filtered_df.groupby(x_col)[y_col].sum().reset_index()
                                    
                                    fig = create_chart(
                                        chart_config['type'],
                                        display_df,
                                        x_col,
                                        y_col,
                                        color_col,
                                        chart_config['title']
                                    )
                                    
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.error("Failed to render chart")
                                else:
                                    st.warning("No data available after applying filters")
                            else:
                                st.error(f"Data source '{data_source}' not found")
                        except Exception as e:
                            st.error(f"Error rendering chart: {str(e)}")
    else:
        st.info("No charts added yet. Use the 'Add New Chart' section above to get started!")
    
    # Dashboard actions
    if current_dashboard.get('charts'):
        st.divider()
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("💾 Save Dashboard", type="primary"):
                st.success("Dashboard saved successfully!")
        
        with action_col2:
            if st.button("📋 Generate Report"):
                st.switch_page("pages/3_Reports.py")
        
        with action_col3:
            if st.button("🔄 Refresh Data"):
                st.success("Data refreshed!")
                st.rerun()

if __name__ == "__main__":
    main()
