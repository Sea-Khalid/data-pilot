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
    
    # Professional header with hero section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 3rem; margin: 0; font-weight: 700;">📊 Analytics Platform</h1>
        <p style="font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;">Enterprise-grade data analytics with AI insights and real-time collaboration</p>
        <div style="margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; font-size: 0.9rem;">AI-Powered</span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; font-size: 0.9rem;">Real-time Collaboration</span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; font-size: 0.9rem;">Drag & Drop</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Feature showcase section
    st.markdown("## 🌟 Platform Capabilities")
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
    
    with feature_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧠</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">AI Insights</h4>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Intelligent trend analysis and business recommendations powered by OpenAI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">👥</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">Collaboration</h4>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Real-time multi-user editing with activity tracking and sharing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎨</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">Drag & Drop</h4>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Visual dashboard editor with grid-based layout arrangement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col4:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔗</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">Share & Embed</h4>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Generate iframe codes and shareable links with access controls</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.data_sources:
        # Getting started section
        st.markdown("## 🚀 Get Started")
        st.markdown("Choose how you'd like to begin your analytics journey:")
        
        start_col1, start_col2, start_col3 = st.columns(3)
        
        with start_col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h3 style="margin: 0.5rem 0;">Upload Data</h3>
                <p style="margin: 0; opacity: 0.9;">Start by uploading your CSV, Excel, or JSON files</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Upload Data", type="primary", use_container_width=True):
                st.switch_page("pages/2_Data_Sources.py")
        
        with start_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📈</div>
                <h3 style="margin: 0.5rem 0;">Create Dashboard</h3>
                <p style="margin: 0; opacity: 0.9;">Build interactive dashboards with drag-and-drop</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Dashboard", use_container_width=True):
                st.switch_page("pages/1_Dashboard_Builder.py")
        
        with start_col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <h3 style="margin: 0.5rem 0;">Generate Reports</h3>
                <p style="margin: 0; opacity: 0.9;">Create professional PDF reports with AI insights</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Reports", use_container_width=True):
                st.switch_page("pages/3_Reports.py")
        
        # Demo section
        st.markdown("---")
        st.markdown("## 💡 Why Choose Our Platform?")
        
        demo_col1, demo_col2 = st.columns([1, 1])
        
        with demo_col1:
            st.markdown("""
            ### Enterprise Features
            - **AI-Powered Analysis**: Automatic trend detection and business insights
            - **Real-time Collaboration**: Multi-user editing with activity tracking  
            - **Advanced Theming**: Dark mode and custom styling options
            - **Smart Data Cleaning**: Automated data validation and optimization
            - **Embedded Sharing**: iframe generation with access controls
            """)
        
        with demo_col2:
            st.markdown("""
            ### Technical Excellence
            - **Interactive Visualizations**: Plotly-powered charts and graphs
            - **Drag & Drop Editor**: Visual dashboard layout management
            - **Multiple Export Formats**: PDF, PNG, CSV, and JSON support
            - **Session Persistence**: Never lose your work
            - **Responsive Design**: Works on all device sizes
            """)
    
    else:
        # Dashboard overview for existing users
        st.markdown("## 📊 Your Analytics Workspace")
        
        if st.session_state.dashboards:
            workspace_col1, workspace_col2 = st.columns([2, 1])
            
            with workspace_col1:
                st.markdown("### Active Dashboards")
                for name, dashboard in st.session_state.dashboards.items():
                    with st.container():
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">📈 {name}</h4>
                            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">
                                {len(dashboard.get('charts', {}))} charts • Created {dashboard.get('created', 'Unknown')[:10]}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                        with action_col1:
                            if st.button("✏️ Edit", key=f"edit_{name}", use_container_width=True):
                                st.session_state.current_dashboard = name
                                st.switch_page("pages/1_Dashboard_Builder.py")
                        with action_col2:
                            if st.button("📋 Report", key=f"report_{name}", use_container_width=True):
                                st.switch_page("pages/3_Reports.py")
                        with action_col3:
                            if st.button("🔗 Share", key=f"share_{name}", use_container_width=True):
                                st.session_state.current_dashboard = name
                                st.switch_page("pages/1_Dashboard_Builder.py")
                        with action_col4:
                            if st.button("🚀 Deploy", key=f"deploy_{name}", use_container_width=True):
                                st.switch_page("pages/4_Deploy.py")
            
            with workspace_col2:
                st.markdown("### Workspace Stats")
                
                # Professional metrics cards
                total_charts = sum(len(d.get('charts', {})) for d in st.session_state.dashboards.values())
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; font-weight: bold;">{len(st.session_state.dashboards)}</div>
                    <div>Dashboards</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; font-weight: bold;">{len(st.session_state.data_sources)}</div>
                    <div>Data Sources</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; font-weight: bold;">{total_charts}</div>
                    <div>Total Charts</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Quick Actions")
                if st.button("➕ New Dashboard", type="primary", use_container_width=True):
                    st.switch_page("pages/1_Dashboard_Builder.py")
                if st.button("📊 Add Data Source", use_container_width=True):
                    st.switch_page("pages/2_Data_Sources.py")
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
                <h3 style="color: #2c3e50;">Ready to Create Your First Dashboard?</h3>
                <p style="color: #7f8c8d; margin-bottom: 2rem;">You have data sources ready. Let's build something amazing!</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Create First Dashboard", type="primary", use_container_width=True):
                st.switch_page("pages/1_Dashboard_Builder.py")
    
    # Professional footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
        <h4 style="color: #2c3e50; margin-bottom: 1rem;">Ready to Transform Your Data Analytics?</h4>
        <p style="color: #7f8c8d; margin-bottom: 1.5rem;">Join thousands of analysts using our platform to create stunning dashboards and gain actionable insights.</p>
        <div style="margin-bottom: 1rem;">
            <span style="background: #667eea; color: white; padding: 0.5rem 1rem; margin: 0.2rem; border-radius: 5px; font-size: 0.9rem;">📊 Dashboard Builder</span>
            <span style="background: #11998e; color: white; padding: 0.5rem 1rem; margin: 0.2rem; border-radius: 5px; font-size: 0.9rem;">🧠 AI Insights</span>
            <span style="background: #fd79a8; color: white; padding: 0.5rem 1rem; margin: 0.2rem; border-radius: 5px; font-size: 0.9rem;">👥 Collaboration</span>
            <span style="background: #fdcb6e; color: white; padding: 0.5rem 1rem; margin: 0.2rem; border-radius: 5px; font-size: 0.9rem;">🚀 Deploy</span>
        </div>
        <p style="color: #95a5a6; font-size: 0.9rem; margin: 0;">Built with Streamlit • Powered by OpenAI • Enterprise Ready</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
