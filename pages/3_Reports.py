import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
import base64
import io
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os

st.set_page_config(page_title="Reports & Export", page_icon="📋", layout="wide")

def create_chart_image(chart_config, data_source_df, format='png'):
    """Create a chart image from chart configuration"""
    try:
        df = data_source_df.copy()
        x_col = chart_config['x_column']
        y_col = chart_config['y_column']
        color_col = chart_config.get('color_column')
        chart_type = chart_config['type']
        title = chart_config['title']
        
        # Apply data aggregation for better visualization
        if df[x_col].dtype == 'object' and chart_type != "Scatter Plot":
            if color_col:
                display_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
            else:
                display_df = df.groupby(x_col)[y_col].sum().reset_index()
        else:
            display_df = df
        
        # Create chart based on type
        if chart_type == "Line Chart":
            fig = px.line(display_df, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Bar Chart":
            fig = px.bar(display_df, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(display_df, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "Pie Chart":
            if color_col:
                fig = px.pie(display_df, values=y_col, names=color_col, title=title)
            else:
                fig = px.pie(display_df, values=y_col, names=x_col, title=title)
        elif chart_type == "Area Chart":
            fig = px.area(display_df, x=x_col, y=y_col, color=color_col, title=title)
        else:
            return None
        
        # Update layout for better export
        fig.update_layout(
            width=800,
            height=500,
            font=dict(size=12),
            title_font_size=16,
            showlegend=True
        )
        
        # Convert to image
        img_bytes = pio.to_image(fig, format=format, width=800, height=500)
        return img_bytes
        
    except Exception as e:
        st.error(f"Error creating chart image: {str(e)}")
        return None

def generate_pdf_report(dashboard_name, dashboard_data, data_sources):
    """Generate a PDF report from dashboard data"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1f77b4')
            )
            story.append(Paragraph(f"Dashboard Report: {dashboard_name}", title_style))
            story.append(Spacer(1, 20))
            
            # Report metadata
            report_info = [
                ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Dashboard Name:', dashboard_name],
                ['Number of Charts:', str(len(dashboard_data.get('charts', {})))],
                ['Data Sources Used:', ', '.join(set(chart['data_source'] for chart in dashboard_data.get('charts', {}).values()))]
            ]
            
            report_table = Table(report_info, colWidths=[2*inch, 4*inch])
            report_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(report_table)
            story.append(Spacer(1, 30))
            
            # Charts section
            story.append(Paragraph("Charts and Visualizations", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            for chart_id, chart_config in dashboard_data.get('charts', {}).items():
                # Chart title
                story.append(Paragraph(chart_config['title'], styles['Heading3']))
                story.append(Spacer(1, 10))
                
                # Chart details
                chart_details = [
                    ['Chart Type:', chart_config['type']],
                    ['Data Source:', chart_config['data_source']],
                    ['X-Axis:', chart_config['x_column']],
                    ['Y-Axis:', chart_config['y_column']],
                ]
                
                if chart_config.get('color_column'):
                    chart_details.append(['Color By:', chart_config['color_column']])
                
                detail_table = Table(chart_details, colWidths=[1.5*inch, 3*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(detail_table)
                story.append(Spacer(1, 20))
            
            # Data summary section
            story.append(Paragraph("Data Summary", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            for source_name, df in data_sources.items():
                if any(chart['data_source'] == source_name for chart in dashboard_data.get('charts', {}).values()):
                    story.append(Paragraph(f"Data Source: {source_name}", styles['Heading3']))
                    
                    summary_data = [
                        ['Total Rows:', str(len(df))],
                        ['Total Columns:', str(len(df.columns))],
                        ['Numeric Columns:', str(len(df.select_dtypes(include=['number']).columns))],
                        ['Missing Values:', str(df.isnull().sum().sum())],
                    ]
                    
                    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
                    summary_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(summary_table)
                    story.append(Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            
            # Read the file content
            with open(tmp_file.name, 'rb') as f:
                pdf_content = f.read()
            
            # Clean up
            os.unlink(tmp_file.name)
            
            return pdf_content
            
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def main():
    st.title("📋 Reports & Export")
    st.markdown("Generate and export reports from your dashboards")
    
    # Initialize session state
    if 'dashboards' not in st.session_state:
        st.session_state.dashboards = {}
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    if not st.session_state.dashboards:
        st.warning("⚠️ No dashboards available. Please create a dashboard first!")
        if st.button("Go to Dashboard Builder"):
            st.switch_page("pages/1_Dashboard_Builder.py")
        return
    
    tab1, tab2, tab3 = st.tabs(["Generate Reports", "Export Charts", "Scheduled Reports"])
    
    with tab1:
        st.header("📊 Generate Dashboard Reports")
        
        # Dashboard selection
        selected_dashboard = st.selectbox(
            "Select Dashboard",
            list(st.session_state.dashboards.keys()),
            help="Choose a dashboard to generate a report"
        )
        
        if selected_dashboard:
            dashboard_data = st.session_state.dashboards[selected_dashboard]
            charts = dashboard_data.get('charts', {})
            
            # Dashboard summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Charts", len(charts))
            with col2:
                data_sources_used = set(chart['data_source'] for chart in charts.values())
                st.metric("Data Sources", len(data_sources_used))
            with col3:
                st.metric("Created", dashboard_data.get('created', 'Unknown')[:10])
            
            st.divider()
            
            # Report generation options
            st.subheader("📋 Report Options")
            
            report_col1, report_col2 = st.columns([2, 1])
            
            with report_col1:
                report_title = st.text_input("Report Title", value=f"{selected_dashboard} Report")
                include_charts = st.checkbox("Include chart visualizations", value=True)
                include_data_summary = st.checkbox("Include data summary", value=True)
                include_metadata = st.checkbox("Include dashboard metadata", value=True)
                
                # Date range for data filtering (if applicable)
                st.subheader("📅 Data Filters")
                use_date_filter = st.checkbox("Apply date range filter")
                if use_date_filter:
                    date_col1, date_col2 = st.columns(2)
                    with date_col1:
                        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
                    with date_col2:
                        end_date = st.date_input("End Date", value=datetime.now().date())
            
            with report_col2:
                st.subheader("📊 Preview")
                
                # Show dashboard preview
                if charts:
                    st.write(f"**{len(charts)} charts** will be included:")
                    for chart_id, chart_config in list(charts.items())[:3]:
                        st.write(f"• {chart_config['title']}")
                    if len(charts) > 3:
                        st.write(f"• ... and {len(charts) - 3} more")
                else:
                    st.info("No charts in this dashboard")
            
            st.divider()
            
            # Generate reports
            st.subheader("📥 Export Options")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                if st.button("📄 Generate PDF Report", type="primary"):
                    with st.spinner("Generating PDF report..."):
                        pdf_content = generate_pdf_report(
                            selected_dashboard,
                            dashboard_data,
                            st.session_state.data_sources
                        )
                        
                        if pdf_content:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_content,
                                file_name=f"{selected_dashboard}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf"
                            )
                            st.success("PDF report generated successfully!")
                        else:
                            st.error("Failed to generate PDF report")
            
            with export_col2:
                if st.button("📊 Export Dashboard Data"):
                    # Compile all data used in dashboard
                    dashboard_data_combined = pd.DataFrame()
                    
                    for chart_config in charts.values():
                        data_source = chart_config['data_source']
                        if data_source in st.session_state.data_sources:
                            df = st.session_state.data_sources[data_source]
                            if dashboard_data_combined.empty:
                                dashboard_data_combined = df.copy()
                            # Could merge or append data from different sources
                    
                    if not dashboard_data_combined.empty:
                        csv = dashboard_data_combined.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Data CSV",
                            data=csv,
                            file_name=f"{selected_dashboard}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        st.success("Dashboard data exported!")
                    else:
                        st.error("No data available for export")
            
            with export_col3:
                if st.button("🔗 Generate Share Link"):
                    # Generate a shareable link (in a real app, this would create a unique URL)
                    share_id = f"{selected_dashboard}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    share_url = f"http://localhost:5000/?dashboard={share_id}"
                    
                    st.code(share_url, language="text")
                    st.info("💡 Share this link to give others access to your dashboard")
    
    with tab2:
        st.header("📈 Export Individual Charts")
        
        # Dashboard and chart selection
        col1, col2 = st.columns(2)
        
        with col1:
            dashboard_name = st.selectbox(
                "Select Dashboard",
                list(st.session_state.dashboards.keys()),
                key="export_dashboard"
            )
        
        with col2:
            if dashboard_name:
                charts = st.session_state.dashboards[dashboard_name].get('charts', {})
                chart_options = {f"{config['title']} ({config['type']})": chart_id 
                               for chart_id, config in charts.items()}
                
                selected_chart_display = st.selectbox("Select Chart", list(chart_options.keys()))
                selected_chart_id = chart_options.get(selected_chart_display) if chart_options else None
        
        if dashboard_name and selected_chart_id:
            chart_config = charts[selected_chart_id]
            data_source_name = chart_config['data_source']
            
            if data_source_name in st.session_state.data_sources:
                df = st.session_state.data_sources[data_source_name]
                
                # Show chart preview
                st.subheader("Chart Preview")
                try:
                    # Create and display the chart
                    display_df = df.copy()
                    x_col = chart_config['x_column']
                    y_col = chart_config['y_column']
                    color_col = chart_config.get('color_column')
                    
                    if df[x_col].dtype == 'object' and chart_config['type'] != "Scatter Plot":
                        if color_col:
                            display_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
                        else:
                            display_df = df.groupby(x_col)[y_col].sum().reset_index()
                    
                    if chart_config['type'] == "Line Chart":
                        fig = px.line(display_df, x=x_col, y=y_col, color=color_col, title=chart_config['title'])
                    elif chart_config['type'] == "Bar Chart":
                        fig = px.bar(display_df, x=x_col, y=y_col, color=color_col, title=chart_config['title'])
                    elif chart_config['type'] == "Scatter Plot":
                        fig = px.scatter(display_df, x=x_col, y=y_col, color=color_col, title=chart_config['title'])
                    elif chart_config['type'] == "Pie Chart":
                        if color_col:
                            fig = px.pie(display_df, values=y_col, names=color_col, title=chart_config['title'])
                        else:
                            fig = px.pie(display_df, values=y_col, names=x_col, title=chart_config['title'])
                    elif chart_config['type'] == "Area Chart":
                        fig = px.area(display_df, x=x_col, y=y_col, color=color_col, title=chart_config['title'])
                    
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export options
                    st.subheader("Export Options")
                    
                    export_format_col1, export_format_col2, export_format_col3 = st.columns(3)
                    
                    with export_format_col1:
                        if st.button("📸 Export as PNG"):
                            img_bytes = create_chart_image(chart_config, df, 'png')
                            if img_bytes:
                                st.download_button(
                                    label="📥 Download PNG",
                                    data=img_bytes,
                                    file_name=f"{chart_config['title']}.png",
                                    mime="image/png"
                                )
                                st.success("PNG exported successfully!")
                    
                    with export_format_col2:
                        if st.button("🖼️ Export as SVG"):
                            img_bytes = create_chart_image(chart_config, df, 'svg')
                            if img_bytes:
                                st.download_button(
                                    label="📥 Download SVG",
                                    data=img_bytes,
                                    file_name=f"{chart_config['title']}.svg",
                                    mime="image/svg+xml"
                                )
                                st.success("SVG exported successfully!")
                    
                    with export_format_col3:
                        if st.button("📊 Export Chart Data"):
                            csv_data = display_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=f"{chart_config['title']}_data.csv",
                                mime="text/csv"
                            )
                            st.success("Chart data exported!")
                            
                except Exception as e:
                    st.error(f"Error displaying chart: {str(e)}")
            else:
                st.error(f"Data source '{data_source_name}' not found")
    
    with tab3:
        st.header("⏰ Scheduled Reports")
        st.info("🚧 Scheduled reporting feature coming soon!")
        
        # Mock scheduled reports interface
        st.subheader("Create Scheduled Report")
        
        schedule_col1, schedule_col2 = st.columns(2)
        
        with schedule_col1:
            report_name = st.text_input("Report Name", placeholder="Weekly Sales Report")
            dashboard_to_schedule = st.selectbox(
                "Dashboard", 
                list(st.session_state.dashboards.keys()),
                key="schedule_dashboard"
            )
            
        with schedule_col2:
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
            email_recipients = st.text_area(
                "Email Recipients", 
                placeholder="Enter email addresses (one per line)",
                height=100
            )
        
        if st.button("📅 Schedule Report", type="primary"):
            st.info("📧 Scheduled report created! Recipients will receive reports automatically.")
            
        # Show existing scheduled reports (mock)
        st.subheader("Existing Scheduled Reports")
        
        sample_schedules = [
            {"name": "Monthly Dashboard Report", "dashboard": "Sales Analysis", "frequency": "Monthly", "next_run": "2025-09-01"},
            {"name": "Weekly Performance", "dashboard": "KPI Dashboard", "frequency": "Weekly", "next_run": "2025-08-13"}
        ]
        
        for schedule in sample_schedules:
            with st.expander(f"📋 {schedule['name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Dashboard:** {schedule['dashboard']}")
                    st.write(f"**Frequency:** {schedule['frequency']}")
                with col2:
                    st.write(f"**Next Run:** {schedule['next_run']}")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_schedule_{schedule['name']}"):
                        st.success("Scheduled report deleted!")

if __name__ == "__main__":
    main()
