import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os
import base64
from datetime import datetime
import json
import zipfile
import io

class ExportUtils:
    """Utility class for exporting dashboards and charts"""
    
    @staticmethod
    def export_chart_as_image(fig, format='png', width=800, height=600):
        """Export a plotly figure as an image"""
        try:
            # Update figure layout for better export
            fig.update_layout(
                width=width,
                height=height,
                font=dict(size=12),
                title_font_size=16
            )
            
            # Convert to image bytes
            img_bytes = pio.to_image(fig, format=format, width=width, height=height)
            return img_bytes
        except Exception as e:
            st.error(f"Failed to export chart as {format}: {str(e)}")
            return None
    
    @staticmethod
    def create_dashboard_pdf(dashboard_name, dashboard_data, data_sources):
        """Create a comprehensive PDF report from dashboard"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                doc = SimpleDocTemplate(tmp_file.name, pagesize=A4, topMargin=1*inch)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                    textColor=colors.HexColor('#1f77b4'),
                    alignment=1  # Center alignment
                )
                
                subtitle_style = ParagraphStyle(
                    'CustomSubtitle',
                    parent=styles['Heading2'],
                    fontSize=16,
                    spaceBefore=20,
                    spaceAfter=15,
                    textColor=colors.HexColor('#333333')
                )
                
                # Title page
                story.append(Paragraph(f"Dashboard Report", title_style))
                story.append(Paragraph(f"{dashboard_name}", subtitle_style))
                story.append(Spacer(1, 30))
                
                # Executive summary table
                summary_data = [
                    ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    ['Dashboard Name:', dashboard_name],
                    ['Total Charts:', str(len(dashboard_data.get('charts', {})))],
                    ['Data Sources Used:', ', '.join(set(chart['data_source'] for chart in dashboard_data.get('charts', {}).values()))]
                ]
                
                summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 40))
                
                # Chart details section
                story.append(Paragraph("Chart Overview", subtitle_style))
                story.append(Spacer(1, 15))
                
                charts = dashboard_data.get('charts', {})
                for i, (chart_id, chart_config) in enumerate(charts.items(), 1):
                    # Chart information
                    chart_title = chart_config.get('title', f'Chart {i}')
                    story.append(Paragraph(f"{i}. {chart_title}", styles['Heading3']))
                    
                    chart_details = [
                        ['Chart Type:', chart_config.get('type', 'Unknown')],
                        ['Data Source:', chart_config.get('data_source', 'Unknown')],
                        ['X-Axis Column:', chart_config.get('x_column', 'N/A')],
                        ['Y-Axis Column:', chart_config.get('y_column', 'N/A')],
                    ]
                    
                    if chart_config.get('color_column'):
                        chart_details.append(['Color Grouping:', chart_config['color_column']])
                    
                    chart_table = Table(chart_details, colWidths=[2*inch, 3.5*inch])
                    chart_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(chart_table)
                    story.append(Spacer(1, 20))
                
                # Data sources section
                story.append(Paragraph("Data Sources Summary", subtitle_style))
                story.append(Spacer(1, 15))
                
                for source_name, df in data_sources.items():
                    # Only include data sources used in the dashboard
                    if any(chart['data_source'] == source_name for chart in charts.values()):
                        story.append(Paragraph(f"Data Source: {source_name}", styles['Heading3']))
                        
                        # Data source statistics
                        source_stats = [
                            ['Total Rows:', str(len(df))],
                            ['Total Columns:', str(len(df.columns))],
                            ['Numeric Columns:', str(len(df.select_dtypes(include=['number']).columns))],
                            ['Text Columns:', str(len(df.select_dtypes(include=['object']).columns))],
                            ['Missing Values:', str(df.isnull().sum().sum())],
                            ['Date Columns:', str(len(df.select_dtypes(include=['datetime']).columns))]
                        ]
                        
                        stats_table = Table(source_stats, colWidths=[2*inch, 2*inch])
                        stats_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(stats_table)
                        
                        # Sample data preview
                        if not df.empty:
                            story.append(Spacer(1, 10))
                            story.append(Paragraph("Sample Data (First 5 Rows):", styles['Heading4']))
                            
                            # Create sample data table
                            sample_df = df.head(5)
                            table_data = [list(sample_df.columns)]
                            for _, row in sample_df.iterrows():
                                table_data.append([str(val)[:20] + '...' if len(str(val)) > 20 else str(val) for val in row])
                            
                            # Adjust column widths based on number of columns
                            num_cols = len(sample_df.columns)
                            col_width = 6.5 * inch / num_cols if num_cols > 0 else 1 * inch
                            
                            sample_table = Table(table_data, colWidths=[col_width] * num_cols)
                            sample_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('TOPPADDING', (0, 0), (-1, -1), 4),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            story.append(sample_table)
                        
                        story.append(Spacer(1, 25))
                
                # Footer
                story.append(Spacer(1, 30))
                footer_text = f"Generated by Data Analytics Platform on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}"
                story.append(Paragraph(footer_text, styles['Normal']))
                
                # Build the PDF
                doc.build(story)
                
                # Read and return the PDF content
                with open(tmp_file.name, 'rb') as f:
                    pdf_content = f.read()
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
                return pdf_content
                
        except Exception as e:
            st.error(f"Failed to generate PDF report: {str(e)}")
            return None
    
    @staticmethod
    def export_dashboard_config(dashboard_name, dashboard_data):
        """Export dashboard configuration as JSON"""
        try:
            config = {
                'dashboard_name': dashboard_name,
                'export_timestamp': datetime.now().isoformat(),
                'dashboard_data': dashboard_data,
                'version': '1.0',
                'format': 'streamlit_dashboard_config'
            }
            
            return json.dumps(config, indent=2, default=str)
        except Exception as e:
            st.error(f"Failed to export dashboard configuration: {str(e)}")
            return None
    
    @staticmethod
    def create_dashboard_zip(dashboard_name, dashboard_data, data_sources, include_charts=True):
        """Create a ZIP file with dashboard data and configurations"""
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add dashboard configuration
                config_json = ExportUtils.export_dashboard_config(dashboard_name, dashboard_data)
                if config_json:
                    zip_file.writestr(f"{dashboard_name}_config.json", config_json)
                
                # Add data sources used in dashboard
                charts = dashboard_data.get('charts', {})
                data_sources_used = set(chart['data_source'] for chart in charts.values())
                
                for source_name in data_sources_used:
                    if source_name in data_sources:
                        df = data_sources[source_name]
                        csv_content = df.to_csv(index=False)
                        zip_file.writestr(f"data/{source_name}.csv", csv_content)
                
                # Add chart configurations
                for chart_id, chart_config in charts.items():
                    chart_json = json.dumps(chart_config, indent=2, default=str)
                    zip_file.writestr(f"charts/{chart_id}.json", chart_json)
                
                # Add README file
                readme_content = f"""# Dashboard Export: {dashboard_name}

## Contents:
- {dashboard_name}_config.json: Complete dashboard configuration
- data/: CSV files for data sources used in the dashboard
- charts/: Individual chart configurations
- This README file

## Import Instructions:
1. Upload the data CSV files to your Data Analytics Platform
2. Import the dashboard configuration using the dashboard builder
3. Individual chart configurations can be used to recreate specific visualizations

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dashboard Version: 1.0
"""
                zip_file.writestr("README.md", readme_content)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            st.error(f"Failed to create dashboard ZIP: {str(e)}")
            return None
    
    @staticmethod
    def get_download_link(data, filename, link_text="Download"):
        """Generate a download link for data"""
        try:
            if isinstance(data, str):
                data = data.encode()
            
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
            return href
        except Exception as e:
            st.error(f"Failed to create download link: {str(e)}")
            return None
    
    @staticmethod
    def export_chart_data(chart_config, data_source_df, format='csv'):
        """Export the data used in a specific chart"""
        try:
            # Process data the same way it's processed for the chart
            df = data_source_df.copy()
            x_col = chart_config.get('x_column')
            y_col = chart_config.get('y_column')
            color_col = chart_config.get('color_column')
            chart_type = chart_config.get('type')
            
            # Apply same aggregation logic as used in chart creation
            if chart_type == "pie":
                if color_col:
                    processed_df = df.groupby(color_col)[y_col].sum().reset_index()
                else:
                    processed_df = df.groupby(x_col)[y_col].sum().reset_index()
            elif chart_type in ["bar", "line", "area"] and df[x_col].dtype == 'object':
                if color_col:
                    processed_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
                else:
                    processed_df = df.groupby(x_col)[y_col].sum().reset_index()
            else:
                processed_df = df[[col for col in [x_col, y_col, color_col] if col]]
            
            if format == 'csv':
                return processed_df.to_csv(index=False)
            elif format == 'json':
                return processed_df.to_json(orient='records', indent=2)
            elif format == 'excel':
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    processed_df.to_excel(writer, index=False, sheet_name='Chart Data')
                return output.getvalue()
            else:
                return processed_df.to_csv(index=False)
                
        except Exception as e:
            st.error(f"Failed to export chart data: {str(e)}")
            return None
