import streamlit as st
import json
import uuid
from datetime import datetime

def init_drag_drop_state():
    """Initialize drag and drop state management"""
    if 'drag_drop' not in st.session_state:
        st.session_state.drag_drop = {
            'grid_layout': {},
            'selected_chart': None,
            'grid_size': {'cols': 12, 'rows': 8},
            'chart_positions': {},
            'layout_mode': 'grid'  # grid, freeform
        }

def create_grid_layout_editor(dashboard_name):
    """Create a visual grid-based layout editor"""
    init_drag_drop_state()
    
    st.subheader("🎨 Dashboard Layout Editor")
    st.markdown("Arrange your charts in a grid layout by dragging and dropping")
    
    # Layout controls
    layout_col1, layout_col2, layout_col3 = st.columns(3)
    
    with layout_col1:
        grid_cols = st.slider("Grid Columns", 2, 12, 6)
        st.session_state.drag_drop['grid_size']['cols'] = grid_cols
    
    with layout_col2:
        chart_height = st.slider("Chart Height", 200, 600, 400)
    
    with layout_col3:
        layout_mode = st.selectbox("Layout Mode", ["Grid", "Freeform"], index=0)
        st.session_state.drag_drop['layout_mode'] = layout_mode.lower()
    
    # Get current dashboard charts
    current_dashboard = st.session_state.dashboards.get(dashboard_name, {})
    charts = current_dashboard.get('charts', {})
    
    if not charts:
        st.info("Add charts to your dashboard first to use the layout editor")
        return
    
    # Visual grid editor
    st.divider()
    
    # Chart palette (available charts to drag)
    with st.expander("📊 Available Charts", expanded=True):
        st.write("**Drag these charts to your dashboard grid:**")
        
        chart_palette_cols = st.columns(min(4, len(charts)))
        for i, (chart_id, chart_config) in enumerate(charts.items()):
            with chart_palette_cols[i % len(chart_palette_cols)]:
                chart_card_html = f"""
                <div style="
                    background: linear-gradient(45deg, #f0f2f6, #ffffff);
                    border: 2px dashed #1f77b4;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    margin: 4px;
                    cursor: move;
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size: 20px; margin-bottom: 8px;">
                        {'📊' if chart_config['type'] == 'Bar Chart' else
                         '📈' if chart_config['type'] == 'Line Chart' else
                         '🔴' if chart_config['type'] == 'Pie Chart' else
                         '📉' if chart_config['type'] == 'Area Chart' else
                         '⭐' if chart_config['type'] == 'Scatter Plot' else '📊'}
                    </div>
                    <div style="font-weight: bold; font-size: 12px;">{chart_config['title'][:20]}</div>
                    <div style="font-size: 10px; color: #666;">{chart_config['type']}</div>
                </div>
                """
                st.markdown(chart_card_html, unsafe_allow_html=True)
                
                if st.button(f"Select {chart_config['title'][:15]}", key=f"select_{chart_id}"):
                    st.session_state.drag_drop['selected_chart'] = chart_id
    
    # Grid layout area
    st.subheader("🎯 Dashboard Grid")
    
    # Initialize layout if not exists
    if dashboard_name not in st.session_state.drag_drop['grid_layout']:
        st.session_state.drag_drop['grid_layout'][dashboard_name] = {}
    
    grid_layout = st.session_state.drag_drop['grid_layout'][dashboard_name]
    
    # Create visual grid
    grid_rows = max(4, (len(charts) // grid_cols) + 2)
    
    # Grid interaction interface
    st.write("**Click on grid cells to place your selected chart:**")
    
    if st.session_state.drag_drop.get('selected_chart'):
        selected_chart_config = charts[st.session_state.drag_drop['selected_chart']]
        st.info(f"🎯 Selected: {selected_chart_config['title']} - Click a grid cell to place it")
    
    # Create the interactive grid
    for row in range(grid_rows):
        grid_cols_ui = st.columns(grid_cols)
        
        for col in range(grid_cols):
            with grid_cols_ui[col]:
                grid_key = f"{row}_{col}"
                
                # Check if this grid cell is occupied
                occupied_chart = None
                for chart_id, position in grid_layout.items():
                    if position.get('row') == row and position.get('col') == col:
                        occupied_chart = chart_id
                        break
                
                if occupied_chart:
                    # Show occupied cell with chart info
                    chart_config = charts[occupied_chart]
                    chart_icon = {
                        'Bar Chart': '📊',
                        'Line Chart': '📈',
                        'Pie Chart': '🔴',
                        'Area Chart': '📉',
                        'Scatter Plot': '⭐'
                    }.get(chart_config['type'], '📊')
                    
                    occupied_html = f"""
                    <div style="
                        background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                        border: 2px solid #1f77b4;
                        border-radius: 8px;
                        padding: 8px;
                        text-align: center;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        cursor: pointer;
                    ">
                        <div style="font-size: 16px;">{chart_icon}</div>
                        <div style="font-size: 10px; font-weight: bold;">{chart_config['title'][:12]}</div>
                    </div>
                    """
                    st.markdown(occupied_html, unsafe_allow_html=True)
                    
                    # Remove button
                    if st.button("❌", key=f"remove_{grid_key}", help="Remove chart"):
                        del grid_layout[occupied_chart]
                        st.rerun()
                
                else:
                    # Show empty cell
                    empty_html = f"""
                    <div style="
                        background: #f9f9f9;
                        border: 2px dashed #cccccc;
                        border-radius: 8px;
                        height: 80px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.backgroundColor='#f0f0f0'; this.style.borderColor='#1f77b4'" 
                      onmouseout="this.style.backgroundColor='#f9f9f9'; this.style.borderColor='#cccccc'">
                        <div style="color: #999; font-size: 24px;">+</div>
                    </div>
                    """
                    st.markdown(empty_html, unsafe_allow_html=True)
                    
                    # Place chart button
                    if st.button("Place Here", key=f"place_{grid_key}", disabled=not st.session_state.drag_drop.get('selected_chart')):
                        if st.session_state.drag_drop.get('selected_chart'):
                            chart_id = st.session_state.drag_drop['selected_chart']
                            grid_layout[chart_id] = {
                                'row': row,
                                'col': col,
                                'width': 1,
                                'height': 1
                            }
                            st.session_state.drag_drop['selected_chart'] = None
                            st.rerun()
    
    # Layout actions
    st.divider()
    layout_actions_col1, layout_actions_col2, layout_actions_col3 = st.columns(3)
    
    with layout_actions_col1:
        if st.button("🔄 Auto Arrange", type="secondary"):
            # Auto-arrange charts in grid
            chart_ids = list(charts.keys())
            grid_layout.clear()
            
            for i, chart_id in enumerate(chart_ids):
                row = i // grid_cols
                col = i % grid_cols
                grid_layout[chart_id] = {
                    'row': row,
                    'col': col,
                    'width': 1,
                    'height': 1
                }
            st.rerun()
    
    with layout_actions_col2:
        if st.button("🗑️ Clear Layout", type="secondary"):
            grid_layout.clear()
            st.rerun()
    
    with layout_actions_col3:
        if st.button("💾 Save Layout", type="primary"):
            # Save layout to dashboard
            if dashboard_name in st.session_state.dashboards:
                st.session_state.dashboards[dashboard_name]['layout'] = grid_layout.copy()
                st.success("Layout saved!")

def render_dashboard_with_layout(dashboard_name):
    """Render dashboard using the saved grid layout"""
    init_drag_drop_state()
    
    current_dashboard = st.session_state.dashboards.get(dashboard_name, {})
    charts = current_dashboard.get('charts', {})
    layout = current_dashboard.get('layout', {})
    
    if not charts:
        return
    
    # If no layout is saved, use default arrangement
    if not layout:
        # Default: arrange in 2-column grid
        chart_keys = list(charts.keys())
        for i in range(0, len(chart_keys), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(chart_keys):
                    chart_key = chart_keys[i + j]
                    render_single_chart(col, chart_key, charts[chart_key])
        return
    
    # Render using saved layout
    max_row = max([pos.get('row', 0) for pos in layout.values()]) if layout else 0
    grid_cols = st.session_state.drag_drop['grid_size']['cols']
    
    for row in range(max_row + 1):
        # Find charts in this row
        row_charts = []
        for chart_id, position in layout.items():
            if position.get('row') == row:
                row_charts.append((chart_id, position.get('col', 0)))
        
        if row_charts:
            # Sort by column position
            row_charts.sort(key=lambda x: x[1])
            
            # Create columns for this row
            num_cols = len(row_charts)
            if num_cols > 0:
                cols = st.columns(num_cols)
                
                for i, (chart_id, _) in enumerate(row_charts):
                    if chart_id in charts:
                        render_single_chart(cols[i], chart_id, charts[chart_id])

def render_single_chart(container, chart_id, chart_config):
    """Render a single chart in the given container"""
    # Import locally to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from pages.dashboard_builder import create_chart, apply_dashboard_filters
    except ImportError:
        # Fallback implementation
        import plotly.express as px
        def create_chart(chart_type, data, x_col, y_col, color_col=None, title="Chart"):
            if chart_type == "Bar Chart":
                return px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "Line Chart":
                return px.line(data, x=x_col, y=y_col, color=color_col, title=title)
            return None
        
        def apply_dashboard_filters(df, filters):
            return df  # No filtering in fallback
    
    with container:
        # Chart header with controls
        chart_header_col1, chart_header_col2 = st.columns([3, 1])
        
        with chart_header_col1:
            st.subheader(chart_config['title'])
        
        with chart_header_col2:
            if st.button("🗑️", key=f"delete_{chart_id}", help="Delete chart"):
                # Remove from current dashboard
                dashboard_name = st.session_state.get('current_dashboard')
                if dashboard_name and dashboard_name in st.session_state.dashboards:
                    del st.session_state.dashboards[dashboard_name]['charts'][chart_id]
                    # Also remove from layout
                    layout = st.session_state.dashboards[dashboard_name].get('layout', {})
                    if chart_id in layout:
                        del layout[chart_id]
                st.rerun()
        
        # Render chart
        try:
            data_source = chart_config['data_source']
            if data_source in st.session_state.data_sources:
                df = st.session_state.data_sources[data_source]
                
                # Apply dashboard filters
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
                        # Apply theme to chart
                        from components.theme_manager import apply_theme_to_chart
                        fig = apply_theme_to_chart(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Failed to render chart")
                else:
                    st.warning("No data available after applying filters")
            else:
                st.error(f"Data source '{data_source}' not found")
        except Exception as e:
            st.error(f"Error rendering chart: {str(e)}")

def export_layout_config(dashboard_name):
    """Export layout configuration as JSON"""
    init_drag_drop_state()
    
    layout_config = {
        'dashboard_name': dashboard_name,
        'grid_layout': st.session_state.drag_drop['grid_layout'].get(dashboard_name, {}),
        'grid_size': st.session_state.drag_drop['grid_size'],
        'layout_mode': st.session_state.drag_drop['layout_mode'],
        'exported_at': datetime.now().isoformat()
    }
    
    return json.dumps(layout_config, indent=2)

def import_layout_config(layout_json, dashboard_name):
    """Import layout configuration from JSON"""
    init_drag_drop_state()
    
    try:
        layout_config = json.loads(layout_json)
        st.session_state.drag_drop['grid_layout'][dashboard_name] = layout_config.get('grid_layout', {})
        st.session_state.drag_drop['grid_size'] = layout_config.get('grid_size', {'cols': 6, 'rows': 4})
        st.session_state.drag_drop['layout_mode'] = layout_config.get('layout_mode', 'grid')
        return True
    except Exception as e:
        st.error(f"Failed to import layout: {str(e)}")
        return False