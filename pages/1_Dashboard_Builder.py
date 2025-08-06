import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import uuid

st.set_page_config(page_title="Dashboard Builder", page_icon="📊", layout="wide")

# Import utility functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        
        # Dashboard filters
        with st.expander("🔍 Dashboard Filters"):
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                # Date range filter (if applicable)
                date_columns = []
                for data_source in st.session_state.data_sources.values():
                    date_columns.extend([col for col in data_source.columns if 
                                       data_source[col].dtype.name.startswith('datetime') or 
                                       'date' in col.lower()])
                
                if date_columns:
                    st.date_input("Date Range", value=datetime.now().date(), key="date_filter")
            
            with filter_col2:
                # Category filter
                category_columns = []
                for data_source in st.session_state.data_sources.values():
                    category_columns.extend([col for col in data_source.columns if 
                                           data_source[col].dtype == 'object'])
                
                if category_columns:
                    st.multiselect("Filter by Category", options=[], key="category_filter")
        
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
                        
                        # Render chart
                        try:
                            data_source = chart_config['data_source']
                            if data_source in st.session_state.data_sources:
                                df = st.session_state.data_sources[data_source]
                                
                                # Apply aggregation for better visualization
                                display_df = df.copy()
                                x_col = chart_config['x_column']
                                y_col = chart_config['y_column']
                                color_col = chart_config.get('color_column')
                                
                                if df[x_col].dtype == 'object' and chart_config['type'] != "Scatter Plot":
                                    if color_col:
                                        display_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
                                    else:
                                        display_df = df.groupby(x_col)[y_col].sum().reset_index()
                                
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
