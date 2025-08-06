import streamlit as st
import json
from datetime import datetime
import uuid

class DashboardStateManager:
    """Manage dashboard state and persistence"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        if 'dashboards' not in st.session_state:
            st.session_state.dashboards = {}
        
        if 'data_sources' not in st.session_state:
            st.session_state.data_sources = {}
        
        if 'current_dashboard' not in st.session_state:
            st.session_state.current_dashboard = None
        
        if 'dashboard_history' not in st.session_state:
            st.session_state.dashboard_history = []
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'default_chart_height': 400,
                'default_color_scheme': 'plotly',
                'auto_refresh_interval': 30,
                'show_data_preview': True
            }
    
    @staticmethod
    def create_dashboard(name, description=""):
        """Create a new dashboard"""
        if name in st.session_state.dashboards:
            return False, "Dashboard name already exists"
        
        dashboard_id = str(uuid.uuid4())
        dashboard_data = {
            'id': dashboard_id,
            'name': name,
            'description': description,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'charts': {},
            'layout': {
                'columns': 2,
                'spacing': 'medium'
            },
            'filters': {},
            'settings': {
                'auto_refresh': False,
                'refresh_interval': 300,  # 5 minutes
                'theme': 'default'
            }
        }
        
        st.session_state.dashboards[name] = dashboard_data
        DashboardStateManager.add_to_history(name, 'created')
        
        return True, "Dashboard created successfully"
    
    @staticmethod
    def delete_dashboard(name):
        """Delete a dashboard"""
        if name not in st.session_state.dashboards:
            return False, "Dashboard not found"
        
        del st.session_state.dashboards[name]
        
        # Clear current dashboard if it was deleted
        if st.session_state.current_dashboard == name:
            st.session_state.current_dashboard = None
        
        DashboardStateManager.add_to_history(name, 'deleted')
        
        return True, "Dashboard deleted successfully"
    
    @staticmethod
    def add_chart_to_dashboard(dashboard_name, chart_config):
        """Add a chart to a dashboard"""
        if dashboard_name not in st.session_state.dashboards:
            return False, "Dashboard not found"
        
        chart_id = str(uuid.uuid4())
        chart_config['id'] = chart_id
        chart_config['created'] = datetime.now().isoformat()
        
        st.session_state.dashboards[dashboard_name]['charts'][chart_id] = chart_config
        st.session_state.dashboards[dashboard_name]['modified'] = datetime.now().isoformat()
        
        DashboardStateManager.add_to_history(dashboard_name, 'chart_added')
        
        return True, chart_id
    
    @staticmethod
    def remove_chart_from_dashboard(dashboard_name, chart_id):
        """Remove a chart from a dashboard"""
        if dashboard_name not in st.session_state.dashboards:
            return False, "Dashboard not found"
        
        if chart_id not in st.session_state.dashboards[dashboard_name]['charts']:
            return False, "Chart not found"
        
        del st.session_state.dashboards[dashboard_name]['charts'][chart_id]
        st.session_state.dashboards[dashboard_name]['modified'] = datetime.now().isoformat()
        
        DashboardStateManager.add_to_history(dashboard_name, 'chart_removed')
        
        return True, "Chart removed successfully"
    
    @staticmethod
    def update_chart_config(dashboard_name, chart_id, new_config):
        """Update chart configuration"""
        if dashboard_name not in st.session_state.dashboards:
            return False, "Dashboard not found"
        
        if chart_id not in st.session_state.dashboards[dashboard_name]['charts']:
            return False, "Chart not found"
        
        # Preserve original creation info
        original_config = st.session_state.dashboards[dashboard_name]['charts'][chart_id]
        new_config['id'] = chart_id
        new_config['created'] = original_config.get('created')
        new_config['modified'] = datetime.now().isoformat()
        
        st.session_state.dashboards[dashboard_name]['charts'][chart_id] = new_config
        st.session_state.dashboards[dashboard_name]['modified'] = datetime.now().isoformat()
        
        return True, "Chart updated successfully"
    
    @staticmethod
    def duplicate_dashboard(original_name, new_name):
        """Duplicate an existing dashboard"""
        if original_name not in st.session_state.dashboards:
            return False, "Original dashboard not found"
        
        if new_name in st.session_state.dashboards:
            return False, "Dashboard name already exists"
        
        # Deep copy the original dashboard
        original = st.session_state.dashboards[original_name]
        duplicated = json.loads(json.dumps(original, default=str))
        
        # Update metadata
        duplicated['id'] = str(uuid.uuid4())
        duplicated['name'] = new_name
        duplicated['created'] = datetime.now().isoformat()
        duplicated['modified'] = datetime.now().isoformat()
        
        # Generate new IDs for charts
        new_charts = {}
        for chart_id, chart_config in duplicated['charts'].items():
            new_chart_id = str(uuid.uuid4())
            chart_config['id'] = new_chart_id
            chart_config['created'] = datetime.now().isoformat()
            new_charts[new_chart_id] = chart_config
        
        duplicated['charts'] = new_charts
        
        st.session_state.dashboards[new_name] = duplicated
        DashboardStateManager.add_to_history(new_name, 'duplicated')
        
        return True, "Dashboard duplicated successfully"
    
    @staticmethod
    def add_to_history(dashboard_name, action):
        """Add an action to dashboard history"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'dashboard': dashboard_name,
            'action': action
        }
        
        st.session_state.dashboard_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(st.session_state.dashboard_history) > 100:
            st.session_state.dashboard_history = st.session_state.dashboard_history[-100:]
    
    @staticmethod
    def get_dashboard_stats():
        """Get statistics about dashboards"""
        total_dashboards = len(st.session_state.dashboards)
        total_charts = sum(len(d['charts']) for d in st.session_state.dashboards.values())
        data_sources_used = set()
        
        for dashboard in st.session_state.dashboards.values():
            for chart in dashboard['charts'].values():
                data_sources_used.add(chart.get('data_source', ''))
        
        return {
            'total_dashboards': total_dashboards,
            'total_charts': total_charts,
            'data_sources_used': len(data_sources_used),
            'total_data_sources': len(st.session_state.data_sources)
        }
    
    @staticmethod
    def export_dashboard_state():
        """Export all dashboard state as JSON"""
        try:
            state_data = {
                'dashboards': st.session_state.dashboards,
                'user_preferences': st.session_state.user_preferences,
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            return json.dumps(state_data, indent=2, default=str)
        except Exception as e:
            return None
    
    @staticmethod
    def import_dashboard_state(json_data):
        """Import dashboard state from JSON"""
        try:
            state_data = json.loads(json_data)
            
            # Validate the data structure
            if 'dashboards' not in state_data:
                return False, "Invalid data format: missing dashboards"
            
            # Import dashboards (merge with existing)
            for name, dashboard_data in state_data['dashboards'].items():
                st.session_state.dashboards[name] = dashboard_data
            
            # Import user preferences if available
            if 'user_preferences' in state_data:
                st.session_state.user_preferences.update(state_data['user_preferences'])
            
            return True, f"Imported {len(state_data['dashboards'])} dashboards successfully"
        
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, f"Import failed: {str(e)}"
    
    @staticmethod
    def cleanup_session_state():
        """Clean up session state (remove old/unused data)"""
        # Remove dashboards with no charts that are older than 24 hours
        current_time = datetime.now()
        dashboards_to_remove = []
        
        for name, dashboard in st.session_state.dashboards.items():
            if not dashboard.get('charts'):
                created_time = datetime.fromisoformat(dashboard.get('created', current_time.isoformat()))
                hours_old = (current_time - created_time).total_seconds() / 3600
                
                if hours_old > 24:
                    dashboards_to_remove.append(name)
        
        for name in dashboards_to_remove:
            del st.session_state.dashboards[name]
        
        # Clean up history (keep only last 50 entries)
        if len(st.session_state.dashboard_history) > 50:
            st.session_state.dashboard_history = st.session_state.dashboard_history[-50:]
        
        return len(dashboards_to_remove)
