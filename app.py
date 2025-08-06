import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
import json

# Configure page
st.set_page_config(
    page_title="Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'dashboards' not in st.session_state:
    st.session_state.dashboards = {}
if 'data_sources' not in st.session_state:
    st.session_state.data_sources = {}
if 'current_dashboard' not in st.session_state:
    st.session_state.current_dashboard = None

def main():
    # Initialize theme and collaboration features
    try:
        from components.theme_manager import apply_custom_styling, create_theme_switcher
        from components.collaboration import init_collaboration_state, display_collaboration_panel
        
        init_collaboration_state()
        apply_custom_styling()
    except ImportError:
        pass  # Fallback if components not available
    
    st.title("📊 Data Analytics Platform")
    st.markdown("### Build custom dashboards and reports with AI insights and real-time collaboration")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Add theme switcher
        try:
            create_theme_switcher()
        except:
            pass
        
        # Quick stats
        st.metric("Dashboards Created", len(st.session_state.dashboards))
        st.metric("Data Sources", len(st.session_state.data_sources))
        
        st.divider()
        
        # Recent dashboards
        if st.session_state.dashboards:
            st.subheader("Recent Dashboards")
            for name, dashboard in list(st.session_state.dashboards.items())[-3:]:
                if st.button(f"📈 {name}", key=f"recent_{name}"):
                    st.session_state.current_dashboard = name
                    st.switch_page("pages/1_Dashboard_Builder.py")
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Dashboard", use_container_width=True):
                st.switch_page("pages/1_Dashboard_Builder.py")
        with col2:
            if st.button("📁 Add Data", use_container_width=True):
                st.switch_page("pages/2_Data_Sources.py")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Overview", "Sample Dashboard", "Getting Started"])
    
    with tab1:
        st.header("Platform Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Charts", sum(len(d.get('charts', {})) for d in st.session_state.dashboards.values()))
        with col2:
            st.metric("Data Points", sum(len(df) for df in st.session_state.data_sources.values()))
        with col3:
            st.metric("Active Filters", 0)  # Could be expanded
        with col4:
            st.metric("Reports Generated", 0)  # Could be tracked
        
        st.subheader("Platform Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            **📊 Dashboard Builder**
            - Drag & drop interface
            - Multiple chart types
            - Real-time updates
            - Custom layouts
            """)
        
        with feature_col2:
            st.markdown("""
            **📁 Data Integration**
            - CSV file uploads
            - Data transformations
            - Multiple data sources
            - Data validation
            """)
        
        with feature_col3:
            st.markdown("""
            **📋 Reports & Export**
            - PDF generation
            - Image exports
            - Scheduled reports
            - Share dashboards
            """)
    
    with tab2:
        st.header("Sample Dashboard")
        
        # Create sample data if no data sources exist
        if not st.session_state.data_sources:
            # Generate sample sales data
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            sample_data = pd.DataFrame({
                'Date': dates,
                'Sales': [1000 + i*10 + (i%7)*50 + np.random.randint(-200, 200) for i in range(len(dates))],
                'Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], len(dates)),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
                'Customer_Satisfaction': np.random.uniform(3.5, 5.0, len(dates))
            })
            
            # Display sample charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_line = px.line(
                    sample_data.groupby('Date')['Sales'].sum().reset_index(),
                    x='Date', y='Sales',
                    title='Sales Trend Over Time'
                )
                fig_line.update_layout(height=400)
                st.plotly_chart(fig_line, use_container_width=True)
                
                fig_pie = px.pie(
                    sample_data.groupby('Category')['Sales'].sum().reset_index(),
                    values='Sales', names='Category',
                    title='Sales by Category'
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    sample_data.groupby('Region')['Sales'].sum().reset_index(),
                    x='Region', y='Sales',
                    title='Sales by Region'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                fig_scatter = px.scatter(
                    sample_data.sample(100),
                    x='Sales', y='Customer_Satisfaction',
                    color='Category',
                    title='Sales vs Customer Satisfaction'
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            st.info("💡 This is a sample dashboard with generated data. Upload your own data to create custom dashboards!")
        else:
            st.info("You have data sources available! Go to Dashboard Builder to create your custom dashboards.")
    
    with tab3:
        st.header("Getting Started")
        
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Add Your Data** 📁
           - Go to "Data Sources" page
           - Upload CSV files
           - Preview and validate your data
        
        2. **Build Dashboard** 📊
           - Navigate to "Dashboard Builder"
           - Create a new dashboard
           - Add charts using drag & drop
           - Customize appearance and filters
        
        3. **Generate Reports** 📋
           - Visit "Reports" page
           - Export dashboards as PDF or images
           - Schedule automated reports
           - Share dashboard links
        
        ### 📖 Supported Features
        
        **Chart Types:**
        - Line charts for trends
        - Bar charts for comparisons
        - Pie charts for distributions
        - Scatter plots for correlations
        - Data tables for detailed views
        
        **Data Formats:**
        - CSV files
        - Excel files (coming soon)
        - Database connections (coming soon)
        
        **Export Formats:**
        - PDF reports
        - PNG/JPG images
        - Interactive HTML
        """)
        
        st.success("Ready to get started? Use the navigation in the sidebar to begin building your analytics platform!")

if __name__ == "__main__":
    main()
