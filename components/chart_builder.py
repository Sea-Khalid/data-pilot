import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

class ChartBuilder:
    """Component for building and customizing charts"""
    
    @staticmethod
    def create_chart(chart_type, data, config):
        """Create a plotly chart based on configuration"""
        try:
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            color_col = config.get('color_column')
            title = config.get('title', 'Chart')
            
            if chart_type == "line":
                fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "bar":
                fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "scatter":
                fig = px.scatter(data, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "pie":
                if color_col:
                    fig = px.pie(data, values=y_col, names=color_col, title=title)
                else:
                    fig = px.pie(data, values=y_col, names=x_col, title=title)
            elif chart_type == "area":
                fig = px.area(data, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "histogram":
                fig = px.histogram(data, x=x_col, color=color_col, title=title)
            elif chart_type == "box":
                fig = px.box(data, x=x_col, y=y_col, color=color_col, title=title)
            else:
                return None
                
            # Apply styling
            fig.update_layout(
                height=config.get('height', 400),
                showlegend=config.get('show_legend', True),
                font=dict(size=config.get('font_size', 12))
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
            return None
    
    @staticmethod
    def chart_configuration_ui(data_sources, existing_config=None):
        """UI for configuring chart parameters"""
        
        # Initialize config
        config = existing_config or {}
        
        # Data source selection
        data_source = st.selectbox(
            "Data Source",
            list(data_sources.keys()),
            index=list(data_sources.keys()).index(config.get('data_source', list(data_sources.keys())[0])) if config.get('data_source') in data_sources else 0
        )
        
        if not data_source:
            return None
        
        df = data_sources[data_source]
        
        # Chart type selection
        chart_types = {
            "Line Chart": "line",
            "Bar Chart": "bar", 
            "Scatter Plot": "scatter",
            "Pie Chart": "pie",
            "Area Chart": "area",
            "Histogram": "histogram",
            "Box Plot": "box"
        }
        
        chart_type_display = st.selectbox(
            "Chart Type",
            list(chart_types.keys()),
            index=list(chart_types.values()).index(config.get('chart_type', 'bar')) if config.get('chart_type') in chart_types.values() else 0
        )
        chart_type = chart_types[chart_type_display]
        
        # Column selections
        col1, col2 = st.columns(2)
        
        with col1:
            if chart_type == "histogram":
                x_column = st.selectbox("Column", df.columns)
                y_column = None
            elif chart_type == "pie":
                x_column = st.selectbox("Categories", df.select_dtypes(include=['object', 'category']).columns)
                y_column = st.selectbox("Values", df.select_dtypes(include=['number']).columns)
            else:
                x_column = st.selectbox("X-Axis", df.columns)
                if chart_type == "box":
                    y_column = st.selectbox("Y-Axis", df.select_dtypes(include=['number']).columns)
                else:
                    y_column = st.selectbox("Y-Axis", df.select_dtypes(include=['number']).columns)
        
        with col2:
            # Color/grouping column
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            color_options = ["None"] + list(categorical_cols)
            color_column = st.selectbox(
                "Color By (Optional)",
                color_options,
                index=color_options.index(config.get('color_column', 'None')) if config.get('color_column') in color_options else 0
            )
            if color_column == "None":
                color_column = None
        
        # Chart customization
        st.subheader("Chart Customization")
        
        custom_col1, custom_col2 = st.columns(2)
        
        with custom_col1:
            title = st.text_input(
                "Chart Title",
                value=config.get('title', f"{chart_type_display} - {x_column} vs {y_column if y_column else x_column}")
            )
            height = st.slider("Chart Height", 300, 800, config.get('height', 400))
        
        with custom_col2:
            show_legend = st.checkbox("Show Legend", value=config.get('show_legend', True))
            font_size = st.slider("Font Size", 8, 20, config.get('font_size', 12))
        
        # Build configuration
        final_config = {
            'data_source': data_source,
            'chart_type': chart_type,
            'x_column': x_column,
            'y_column': y_column,
            'color_column': color_column,
            'title': title,
            'height': height,
            'show_legend': show_legend,
            'font_size': font_size
        }
        
        return final_config
    
    @staticmethod
    def render_chart_preview(config, data_sources):
        """Render a preview of the chart"""
        if not config or config['data_source'] not in data_sources:
            st.error("Invalid configuration or data source not found")
            return
        
        df = data_sources[config['data_source']]
        
        # Apply data processing for better visualization
        processed_df = ChartBuilder.process_data_for_chart(df, config)
        
        if processed_df is not None:
            fig = ChartBuilder.create_chart(config['chart_type'], processed_df, config)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to create chart")
        else:
            st.error("Failed to process data for chart")
    
    @staticmethod
    def process_data_for_chart(df, config):
        """Process data based on chart type and configuration"""
        try:
            processed_df = df.copy()
            
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            color_col = config.get('color_column')
            chart_type = config.get('chart_type')
            
            # Handle different chart types
            if chart_type == "histogram":
                # No aggregation needed for histogram
                return processed_df
            
            elif chart_type == "pie":
                # Aggregate data for pie charts
                if color_col:
                    processed_df = df.groupby(color_col)[y_col].sum().reset_index()
                else:
                    processed_df = df.groupby(x_col)[y_col].sum().reset_index()
                return processed_df
            
            elif chart_type in ["bar", "line", "area"]:
                # Aggregate categorical x-axis data
                if df[x_col].dtype == 'object' or df[x_col].dtype.name == 'category':
                    if color_col:
                        processed_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
                    else:
                        processed_df = df.groupby(x_col)[y_col].sum().reset_index()
                
                # Sort by x_column for better visualization
                if processed_df[x_col].dtype in ['int64', 'float64', 'datetime64[ns]']:
                    processed_df = processed_df.sort_values(x_col)
                
                return processed_df
            
            else:
                # For scatter plots and other chart types, return original data
                # Limit to reasonable number of points for performance
                if len(processed_df) > 5000:
                    processed_df = processed_df.sample(5000)
                
                return processed_df
                
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return None
