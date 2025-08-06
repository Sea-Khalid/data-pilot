import streamlit as st
import json
from datetime import datetime

def init_theme_state():
    """Initialize theme management in session state"""
    if 'theme_settings' not in st.session_state:
        st.session_state.theme_settings = {
            'dark_mode': False,
            'primary_color': '#1f77b4',
            'background_color': 'white',
            'text_color': 'black',
            'chart_theme': 'plotly_white',
            'custom_css': '',
            'font_family': 'sans-serif'
        }

def apply_dark_mode():
    """Apply dark mode styling"""
    dark_css = """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    .stSidebar {
        background-color: #262730;
    }
    
    .stSelectbox > div > div {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4F4F4F;
    }
    
    .stButton > button {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4F4F4F;
    }
    
    .stButton > button:hover {
        background-color: #4F4F4F;
        border: 1px solid #FAFAFA;
    }
    
    .stMetric {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #4F4F4F;
    }
    
    .stExpander {
        background-color: #262730;
        border: 1px solid #4F4F4F;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #262730;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    .stDataFrame {
        background-color: #262730;
    }
    
    /* Custom dashboard styling */
    .dashboard-card {
        background-color: #262730;
        border: 1px solid #4F4F4F;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chart-container {
        background-color: #262730;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .insights-panel {
        background-color: #1a1d24;
        border-left: 3px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """
    return dark_css

def apply_light_mode():
    """Apply light mode styling"""
    light_css = """
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #262730;
    }
    
    .stMetric {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #E6E6E6;
    }
    
    .dashboard-card {
        background-color: #FFFFFF;
        border: 1px solid #E6E6E6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chart-container {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .insights-panel {
        background-color: #f8f9fa;
        border-left: 3px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .collaboration-user {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    </style>
    """
    return light_css

def get_plotly_theme():
    """Get the appropriate Plotly theme based on current mode"""
    if st.session_state.theme_settings['dark_mode']:
        return 'plotly_dark'
    else:
        return 'plotly_white'

def apply_custom_styling():
    """Apply custom CSS and theming"""
    init_theme_state()
    
    # Apply base theme
    if st.session_state.theme_settings['dark_mode']:
        css = apply_dark_mode()
    else:
        css = apply_light_mode()
    
    # Add custom CSS if provided
    custom_css = st.session_state.theme_settings.get('custom_css', '')
    if custom_css:
        css += f"\n<style>\n{custom_css}\n</style>"
    
    # Apply primary color customization
    primary_color = st.session_state.theme_settings.get('primary_color', '#1f77b4')
    css += f"""
    <style>
    .stButton > button[kind="primary"] {{
        background-color: {primary_color};
        border-color: {primary_color};
    }}
    
    .stSelectbox > div > div {{
        border-color: {primary_color};
    }}
    
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {primary_color};
        color: {primary_color};
    }}
    
    .stProgress > div > div {{
        background-color: {primary_color};
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def display_theme_settings():
    """Display theme customization options"""
    init_theme_state()
    
    st.subheader("🎨 Theme Settings")
    
    # Dark mode toggle
    current_dark_mode = st.session_state.theme_settings['dark_mode']
    dark_mode = st.toggle("🌙 Dark Mode", value=current_dark_mode)
    
    if dark_mode != current_dark_mode:
        st.session_state.theme_settings['dark_mode'] = dark_mode
        st.rerun()
    
    # Color customization
    theme_col1, theme_col2 = st.columns(2)
    
    with theme_col1:
        st.write("**Colors**")
        primary_color = st.color_picker(
            "Primary Color",
            value=st.session_state.theme_settings['primary_color'],
            help="Main accent color for buttons and highlights"
        )
        st.session_state.theme_settings['primary_color'] = primary_color
        
        font_family = st.selectbox(
            "Font Family",
            ["sans-serif", "serif", "monospace", "Arial", "Helvetica", "Georgia"],
            index=0
        )
        st.session_state.theme_settings['font_family'] = font_family
    
    with theme_col2:
        st.write("**Chart Theme**")
        chart_theme = st.selectbox(
            "Chart Style",
            ["plotly_white", "plotly_dark", "simple_white", "presentation", "ggplot2"],
            index=1 if dark_mode else 0
        )
        st.session_state.theme_settings['chart_theme'] = chart_theme
        
        # Chart color scheme
        color_scheme = st.selectbox(
            "Color Palette",
            ["Default", "Viridis", "Plasma", "Set1", "Pastel", "Dark2"],
            help="Color scheme for charts and visualizations"
        )
    
    # Advanced customization
    with st.expander("🔧 Advanced Customization"):
        st.write("**Custom CSS**")
        custom_css = st.text_area(
            "Add custom CSS",
            value=st.session_state.theme_settings.get('custom_css', ''),
            height=100,
            help="Add custom CSS to further customize the appearance"
        )
        st.session_state.theme_settings['custom_css'] = custom_css
        
        # Animation settings
        enable_animations = st.checkbox("Enable animations", value=True)
        animation_speed = st.slider("Animation Speed", 0.1, 2.0, 1.0, 0.1)
        
        # Layout settings
        compact_mode = st.checkbox("Compact layout", value=False)
        sidebar_width = st.slider("Sidebar Width", 200, 400, 300)
    
    # Theme presets
    st.write("**Quick Presets**")
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    
    with preset_col1:
        if st.button("🌊 Ocean Theme"):
            st.session_state.theme_settings.update({
                'dark_mode': False,
                'primary_color': '#0077be',
                'chart_theme': 'plotly_white'
            })
            st.rerun()
    
    with preset_col2:
        if st.button("🌙 Dark Pro"):
            st.session_state.theme_settings.update({
                'dark_mode': True,
                'primary_color': '#00d4aa',
                'chart_theme': 'plotly_dark'
            })
            st.rerun()
    
    with preset_col3:
        if st.button("🍃 Nature"):
            st.session_state.theme_settings.update({
                'dark_mode': False,
                'primary_color': '#2e8b57',
                'chart_theme': 'ggplot2'
            })
            st.rerun()
    
    # Save theme settings
    if st.button("💾 Save Theme", type="primary"):
        # In a real app, this would save to a database
        st.success("Theme settings saved!")
        
        # Export theme as JSON
        theme_json = json.dumps(st.session_state.theme_settings, indent=2)
        st.download_button(
            "📥 Export Theme",
            data=theme_json,
            file_name=f"theme_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def create_theme_switcher():
    """Create a compact theme switcher for the sidebar"""
    init_theme_state()
    
    with st.sidebar:
        st.divider()
        
        # Quick dark mode toggle
        current_mode = st.session_state.theme_settings['dark_mode']
        
        col1, col2 = st.columns([1, 2])
        with col1:
            mode_icon = "🌙" if current_mode else "☀️"
            st.write(mode_icon)
        
        with col2:
            if st.button("Toggle Theme", key="theme_toggle"):
                st.session_state.theme_settings['dark_mode'] = not current_mode
                st.rerun()
        
        # Theme status
        mode_text = "Dark" if current_mode else "Light"
        st.caption(f"Current: {mode_text} Mode")

def get_chart_colors(num_colors=10):
    """Get color palette based on current theme"""
    if st.session_state.theme_settings['dark_mode']:
        # Dark mode colors - brighter for visibility
        return [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    else:
        # Light mode colors - standard palette
        return [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]

def apply_theme_to_chart(fig):
    """Apply current theme settings to a Plotly figure"""
    init_theme_state()
    
    # Get theme settings
    dark_mode = st.session_state.theme_settings['dark_mode']
    primary_color = st.session_state.theme_settings['primary_color']
    
    # Apply theme template
    theme_template = 'plotly_dark' if dark_mode else 'plotly_white'
    fig.update_layout(template=theme_template)
    
    # Apply custom colors
    colors = get_chart_colors()
    if hasattr(fig, 'data') and fig.data:
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'marker'):
                trace.marker.color = colors[i % len(colors)]
    
    # Custom layout adjustments for dark mode
    if dark_mode:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA')
        )
    else:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    return fig