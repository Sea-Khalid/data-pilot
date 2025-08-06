import streamlit as st
import json
import time
import uuid
from datetime import datetime

def init_collaboration_state():
    """Initialize collaboration features in session state"""
    if 'collaboration' not in st.session_state:
        st.session_state.collaboration = {
            'active_users': {},
            'dashboard_locks': {},
            'real_time_changes': [],
            'share_links': {},
            'user_id': str(uuid.uuid4()),
            'user_name': f"User_{str(uuid.uuid4())[:8]}"
        }

def add_user_activity(activity_type, details):
    """Track user activity for collaboration"""
    if 'collaboration' not in st.session_state:
        init_collaboration_state()
    
    activity = {
        'id': str(uuid.uuid4()),
        'user_id': st.session_state.collaboration['user_id'],
        'user_name': st.session_state.collaboration['user_name'],
        'type': activity_type,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    
    st.session_state.collaboration['real_time_changes'].append(activity)
    
    # Keep only last 50 activities
    if len(st.session_state.collaboration['real_time_changes']) > 50:
        st.session_state.collaboration['real_time_changes'] = \
            st.session_state.collaboration['real_time_changes'][-50:]

def display_collaboration_panel():
    """Display real-time collaboration features"""
    init_collaboration_state()
    
    with st.sidebar:
        st.divider()
        st.subheader("👥 Collaboration")
        
        # User identity
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write("🎭")
        with col2:
            user_name = st.text_input(
                "Your name",
                value=st.session_state.collaboration['user_name'],
                key="collab_user_name",
                label_visibility="collapsed"
            )
            if user_name != st.session_state.collaboration['user_name']:
                st.session_state.collaboration['user_name'] = user_name
        
        # Active users (simulated)
        st.write("**👥 Active Users:**")
        st.session_state.collaboration['active_users'][st.session_state.collaboration['user_id']] = {
            'name': st.session_state.collaboration['user_name'],
            'last_seen': datetime.now().isoformat(),
            'activity': 'Online'
        }
        
        for user_id, user_info in st.session_state.collaboration['active_users'].items():
            status_color = "🟢" if user_id == st.session_state.collaboration['user_id'] else "🔵"
            st.write(f"{status_color} {user_info['name']} (You)" if user_id == st.session_state.collaboration['user_id'] else f"{status_color} {user_info['name']}")
        
        # Recent activity
        st.write("**📝 Recent Activity:**")
        recent_activities = st.session_state.collaboration['real_time_changes'][-5:]
        
        if recent_activities:
            for activity in reversed(recent_activities):
                time_ago = "Just now"
                activity_icon = {
                    'chart_added': '📊',
                    'chart_deleted': '🗑️',
                    'dashboard_created': '✨',
                    'data_uploaded': '📁',
                    'filter_applied': '🔍'
                }.get(activity['type'], '📝')
                
                st.caption(f"{activity_icon} {activity['user_name']}: {activity['details']}")
        else:
            st.caption("No recent activity")

def generate_share_link(dashboard_name, access_level="view"):
    """Generate a shareable link for a dashboard"""
    init_collaboration_state()
    
    share_id = str(uuid.uuid4())
    share_link = {
        'id': share_id,
        'dashboard_name': dashboard_name,
        'access_level': access_level,  # view, edit, admin
        'created_by': st.session_state.collaboration['user_id'],
        'created_at': datetime.now().isoformat(),
        'expires_at': None,  # No expiration by default
        'password': None,
        'embed_code': f'<iframe src="https://your-app.replit.app/embed/{share_id}" width="100%" height="600" frameborder="0"></iframe>'
    }
    
    st.session_state.collaboration['share_links'][share_id] = share_link
    return share_link

def display_sharing_options(dashboard_name):
    """Display sharing and embedding options"""
    st.subheader("🔗 Share & Embed")
    
    share_col1, share_col2 = st.columns(2)
    
    with share_col1:
        st.write("**👥 Collaborative Sharing**")
        access_level = st.selectbox(
            "Access Level",
            ["view", "edit", "admin"],
            format_func=lambda x: {"view": "View Only", "edit": "Can Edit", "admin": "Full Access"}[x]
        )
        
        password_protected = st.checkbox("Password protect")
        password = st.text_input("Password", type="password") if password_protected else None
        
        expires = st.checkbox("Set expiration")
        expiry_days = st.number_input("Days until expiration", min_value=1, max_value=365, value=30) if expires else None
        
        if st.button("🔗 Generate Share Link", type="primary"):
            share_link = generate_share_link(dashboard_name, access_level)
            
            # Display the share link
            share_url = f"https://your-app.replit.app/dashboard/{share_link['id']}"
            st.success("Share link generated!")
            st.code(share_url)
            
            # Copy to clipboard functionality (would need additional JS)
            st.info("💡 Copy this link to share with others")
            
            add_user_activity("link_generated", f"Generated share link for '{dashboard_name}'")
    
    with share_col2:
        st.write("**🌐 Embed Dashboard**")
        
        iframe_width = st.slider("Width", 400, 1200, 800)
        iframe_height = st.slider("Height", 300, 800, 600)
        
        show_toolbar = st.checkbox("Show toolbar", value=True)
        auto_refresh = st.checkbox("Auto-refresh", value=False)
        
        if st.button("📋 Generate Embed Code"):
            # Generate embed code
            embed_params = []
            if not show_toolbar:
                embed_params.append("toolbar=false")
            if auto_refresh:
                embed_params.append("refresh=30")
            
            param_string = "&".join(embed_params)
            embed_url = f"https://your-app.replit.app/embed/{dashboard_name}"
            if param_string:
                embed_url += f"?{param_string}"
            
            embed_code = f'''<iframe 
    src="{embed_url}" 
    width="{iframe_width}" 
    height="{iframe_height}" 
    frameborder="0"
    allowfullscreen>
</iframe>'''
            
            st.success("Embed code generated!")
            st.code(embed_code, language="html")
            
            add_user_activity("embed_generated", f"Generated embed code for '{dashboard_name}'")

def display_collaborative_editing():
    """Show collaborative editing indicators"""
    init_collaboration_state()
    
    # Dashboard lock status
    if st.session_state.get('current_dashboard'):
        dashboard_name = st.session_state.current_dashboard
        locks = st.session_state.collaboration.get('dashboard_locks', {})
        
        if dashboard_name in locks:
            lock_info = locks[dashboard_name]
            if lock_info['user_id'] != st.session_state.collaboration['user_id']:
                st.warning(f"⚠️ {lock_info['user_name']} is currently editing this dashboard")
                return False
        else:
            # Acquire lock for current user
            st.session_state.collaboration['dashboard_locks'][dashboard_name] = {
                'user_id': st.session_state.collaboration['user_id'],
                'user_name': st.session_state.collaboration['user_name'],
                'locked_at': datetime.now().isoformat()
            }
    
    return True

def simulate_other_users():
    """Simulate other users for demo purposes"""
    import random
    
    if random.random() < 0.1:  # 10% chance to add simulated activity
        simulated_users = [
            {"name": "Alice Johnson", "id": "user_alice"},
            {"name": "Bob Smith", "id": "user_bob"},
            {"name": "Carol Davis", "id": "user_carol"}
        ]
        
        user = random.choice(simulated_users)
        activities = [
            ("chart_added", f"added a new bar chart"),
            ("filter_applied", f"applied date filter"),
            ("data_uploaded", f"uploaded new dataset"),
            ("dashboard_created", f"created 'Q4 Results' dashboard")
        ]
        
        activity_type, description = random.choice(activities)
        
        # Add to active users occasionally
        if random.random() < 0.3:
            st.session_state.collaboration['active_users'][user['id']] = {
                'name': user['name'],
                'last_seen': datetime.now().isoformat(),
                'activity': 'Online'
            }
        
        # Add activity
        activity = {
            'id': str(uuid.uuid4()),
            'user_id': user['id'],
            'user_name': user['name'],
            'type': activity_type,
            'details': description,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.collaboration['real_time_changes'].append(activity)

def cleanup_old_users():
    """Remove inactive users from collaboration state"""
    current_time = datetime.now()
    active_users = st.session_state.collaboration.get('active_users', {})
    
    # Remove users not seen in last 5 minutes (simulated)
    users_to_remove = []
    for user_id, user_info in active_users.items():
        if user_id != st.session_state.collaboration['user_id']:  # Don't remove current user
            users_to_remove.append(user_id)
    
    # Remove some users randomly to simulate leaving
    import random
    if users_to_remove and random.random() < 0.2:
        user_to_remove = random.choice(users_to_remove)
        del st.session_state.collaboration['active_users'][user_to_remove]