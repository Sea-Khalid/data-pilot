import streamlit as st
import json
from datetime import datetime
import zipfile
import io

st.set_page_config(page_title="Deploy & Share", page_icon="🚀", layout="wide")

def main():
    st.title("🚀 Deploy & Share Your Analytics Platform")
    st.markdown("Prepare your analytics platform for deployment and sharing")
    
    # Initialize session state
    if 'dashboards' not in st.session_state:
        st.session_state.dashboards = {}
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Replit Deploy", "📦 Export Package", "⚙️ Settings", "👥 User Management"])
    
    with tab1:
        st.header("Deploy to Replit")
        st.markdown("""
        ### Ready to deploy your analytics platform?
        
        Your platform is built with Streamlit and ready for deployment on Replit.
        """)
        
        # Deployment checklist
        st.subheader("📋 Pre-Deployment Checklist")
        
        checklist_items = [
            ("Data Sources", len(st.session_state.data_sources) > 0, "Upload at least one data source"),
            ("Dashboards", len(st.session_state.dashboards) > 0, "Create at least one dashboard"),
            ("Charts", sum(len(d.get('charts', {})) for d in st.session_state.dashboards.values()) > 0, "Add charts to your dashboards"),
        ]
        
        all_ready = True
        for item, status, description in checklist_items:
            col1, col2 = st.columns([1, 4])
            with col1:
                if status:
                    st.success("✅")
                else:
                    st.error("❌")
                    all_ready = False
            with col2:
                st.write(f"**{item}**: {description}")
        
        st.divider()
        
        if all_ready:
            st.success("🎉 Your platform is ready for deployment!")
            
            # Deployment instructions
            st.subheader("🚀 Deployment Steps")
            st.markdown("""
            1. **Click the Deploy button** in your Replit interface
            2. **Choose deployment settings**:
               - Set your app name
               - Configure custom domain (optional)
               - Set resource limits
            3. **Environment variables** (if needed):
               - No additional environment variables required for basic deployment
            4. **Deploy and share** your analytics platform!
            
            ### Deployment Features Available:
            - **Automatic HTTPS** and SSL certificates
            - **Custom domains** for professional URLs
            - **Automatic scaling** based on usage
            - **Health monitoring** and uptime tracking
            """)
            
            # Show deployment button simulation
            st.info("💡 **Next Step**: Click the 'Deploy' button in your Replit sidebar to start the deployment process!")
            
        else:
            st.warning("⚠️ Complete the checklist above before deploying")
    
    with tab2:
        st.header("📦 Export Deployment Package")
        st.markdown("Create a complete package of your platform for deployment elsewhere")
        
        if not st.session_state.dashboards:
            st.warning("No dashboards to export. Create some dashboards first!")
        else:
            # Export options
            st.subheader("Export Options")
            
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                include_sample_data = st.checkbox("Include sample data", value=True)
                include_config = st.checkbox("Include dashboard configurations", value=True)
                include_documentation = st.checkbox("Include documentation", value=True)
            
            with export_col2:
                export_format = st.selectbox("Export Format", ["ZIP Package", "JSON Config Only"])
                include_dependencies = st.checkbox("Include requirements.txt", value=True)
            
            # Generate export package
            if st.button("📦 Generate Export Package", type="primary"):
                try:
                    # Create ZIP package
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        # Add dashboard configurations
                        if include_config:
                            for dashboard_name, dashboard_data in st.session_state.dashboards.items():
                                config_json = json.dumps(dashboard_data, indent=2, default=str)
                                zip_file.writestr(f"dashboards/{dashboard_name}.json", config_json)
                        
                        # Add data sources
                        if include_sample_data:
                            for source_name, df in st.session_state.data_sources.items():
                                csv_content = df.to_csv(index=False)
                                zip_file.writestr(f"data/{source_name}.csv", csv_content)
                        
                        # Add requirements.txt
                        if include_dependencies:
                            requirements = """streamlit
pandas
plotly
numpy
reportlab
openpyxl"""
                            zip_file.writestr("requirements.txt", requirements)
                        
                        # Add documentation
                        if include_documentation:
                            readme_content = f"""# Analytics Platform Export
                            
## Contents
- dashboards/: Dashboard configurations in JSON format
- data/: Sample data sources in CSV format
- requirements.txt: Python dependencies

## Deployment Instructions

### Local Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `streamlit run app.py`
3. Access at http://localhost:8501

### Cloud Deployment
- **Replit**: Upload files and click Deploy
- **Streamlit Cloud**: Connect GitHub repo and deploy
- **Heroku**: Use Procfile with `web: streamlit run app.py --server.port=$PORT`

## Data Sources
{len(st.session_state.data_sources)} data sources included:
{chr(10).join(f'- {name} ({len(df)} rows)' for name, df in st.session_state.data_sources.items())}

## Dashboards
{len(st.session_state.dashboards)} dashboards included:
{chr(10).join(f'- {name} ({len(data.get("charts", {}))} charts)' for name, data in st.session_state.dashboards.items())}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                            zip_file.writestr("README.md", readme_content)
                    
                    zip_buffer.seek(0)
                    
                    # Offer download
                    st.download_button(
                        label="📥 Download Export Package",
                        data=zip_buffer.getvalue(),
                        file_name=f"analytics_platform_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )
                    st.success("Export package created successfully!")
                    
                except Exception as e:
                    st.error(f"Failed to create export package: {str(e)}")
    
    with tab3:
        st.header("⚙️ Platform Settings")
        
        # App configuration
        st.subheader("🎨 App Configuration")
        app_col1, app_col2 = st.columns(2)
        
        with app_col1:
            app_title = st.text_input("Application Title", value="Data Analytics Platform")
            app_description = st.text_area("Description", value="Build custom dashboards and reports with ease")
            enable_dark_mode = st.checkbox("Enable dark mode option")
        
        with app_col2:
            default_chart_height = st.slider("Default Chart Height", 300, 800, 400)
            auto_refresh = st.checkbox("Enable auto-refresh")
            if auto_refresh:
                refresh_interval = st.slider("Refresh Interval (seconds)", 30, 300, 60)
        
        # Performance settings
        st.subheader("⚡ Performance Settings")
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            max_data_rows = st.number_input("Max rows per data source", value=100000, min_value=1000)
            enable_caching = st.checkbox("Enable data caching", value=True)
        
        with perf_col2:
            chart_render_limit = st.number_input("Max data points per chart", value=5000, min_value=100)
            lazy_loading = st.checkbox("Enable lazy loading", value=True)
        
        # Security settings
        st.subheader("🔒 Security Settings")
        security_col1, security_col2 = st.columns(2)
        
        with security_col1:
            require_auth = st.checkbox("Require user authentication")
            allow_data_export = st.checkbox("Allow data export", value=True)
        
        with security_col2:
            session_timeout = st.slider("Session timeout (hours)", 1, 24, 8)
            max_file_size = st.slider("Max upload file size (MB)", 1, 100, 10)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            settings = {
                "app_title": app_title,
                "app_description": app_description,
                "enable_dark_mode": enable_dark_mode,
                "default_chart_height": default_chart_height,
                "auto_refresh": auto_refresh,
                "refresh_interval": refresh_interval if auto_refresh else None,
                "max_data_rows": max_data_rows,
                "enable_caching": enable_caching,
                "chart_render_limit": chart_render_limit,
                "lazy_loading": lazy_loading,
                "require_auth": require_auth,
                "allow_data_export": allow_data_export,
                "session_timeout": session_timeout,
                "max_file_size": max_file_size,
                "saved_at": datetime.now().isoformat()
            }
            
            # Store in session state (in production, this would be stored in a database)
            st.session_state.app_settings = settings
            st.success("Settings saved successfully!")
    
    with tab4:
        st.header("👥 User Management")
        st.markdown("Simple user management for your analytics platform")
        
        # User authentication info
        st.subheader("🔐 Authentication Options")
        
        auth_option = st.selectbox(
            "Choose Authentication Method",
            ["None (Public Access)", "Simple Username/Password", "Firebase Auth", "Auth0", "Custom SSO"]
        )
        
        if auth_option == "None (Public Access)":
            st.info("Your platform will be accessible to anyone with the URL")
            st.markdown("""
            **Pros:**
            - Easy to deploy and share
            - No setup required
            - Good for demos and internal tools
            
            **Cons:**
            - No user-specific data
            - No access control
            - Data visible to all users
            """)
            
        elif auth_option == "Simple Username/Password":
            st.info("Basic authentication with predefined users")
            
            # Simple user management
            st.subheader("👤 Manage Users")
            
            if 'users' not in st.session_state:
                st.session_state.users = {"admin": {"password": "admin123", "role": "admin"}}
            
            # Add new user
            with st.expander("➕ Add New User"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["viewer", "editor", "admin"])
                
                if st.button("Add User"):
                    if new_username and new_password:
                        st.session_state.users[new_username] = {
                            "password": new_password,
                            "role": new_role
                        }
                        st.success(f"User '{new_username}' added successfully!")
                    else:
                        st.error("Please provide username and password")
            
            # Display current users
            st.subheader("Current Users")
            if st.session_state.users:
                user_data = []
                for username, user_info in st.session_state.users.items():
                    user_data.append([username, user_info.get('role', 'viewer'), '••••••••'])
                
                import pandas as pd
                user_df = pd.DataFrame(user_data, columns=["Username", "Role", "Password"])
                st.dataframe(user_df, use_container_width=True)
            
        elif auth_option in ["Firebase Auth", "Auth0"]:
            st.info(f"Integration with {auth_option} requires additional setup")
            st.markdown(f"""
            **{auth_option} Setup Steps:**
            1. Create account with {auth_option}
            2. Configure authentication settings
            3. Add API keys to environment variables
            4. Implement authentication hooks in the application
            
            **Benefits:**
            - Professional authentication
            - Social login options
            - User management dashboard
            - Secure token-based auth
            """)
            
            # Configuration inputs
            if auth_option == "Firebase Auth":
                st.subheader("Firebase Configuration")
                firebase_api_key = st.text_input("Firebase API Key", type="password")
                firebase_auth_domain = st.text_input("Auth Domain")
                firebase_project_id = st.text_input("Project ID")
                
            elif auth_option == "Auth0":
                st.subheader("Auth0 Configuration")
                auth0_domain = st.text_input("Auth0 Domain")
                auth0_client_id = st.text_input("Client ID")
                auth0_client_secret = st.text_input("Client Secret", type="password")
        
        # Role-based access control
        st.subheader("🛡️ Access Control")
        st.markdown("""
        **Role Permissions:**
        
        **Viewer**
        - View dashboards
        - Use filters
        - Export reports
        
        **Editor**
        - All Viewer permissions
        - Create/edit dashboards
        - Upload data sources
        - Manage charts
        
        **Admin**
        - All Editor permissions
        - User management
        - Platform settings
        - Data source management
        """)

if __name__ == "__main__":
    main()