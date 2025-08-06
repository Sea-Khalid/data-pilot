import streamlit as st
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import pickle
import os

class DataStorageManager:
    """Manage data storage and caching for the application"""
    
    @staticmethod
    def initialize_storage():
        """Initialize data storage session state"""
        if 'data_sources' not in st.session_state:
            st.session_state.data_sources = {}
        
        if 'data_metadata' not in st.session_state:
            st.session_state.data_metadata = {}
        
        if 'data_cache' not in st.session_state:
            st.session_state.data_cache = {}
    
    @staticmethod
    def add_data_source(name, dataframe, metadata=None):
        """Add a new data source"""
        if metadata is None:
            metadata = {}
        
        # Generate hash for data integrity
        data_hash = DataStorageManager.generate_data_hash(dataframe)
        
        # Store dataframe
        st.session_state.data_sources[name] = dataframe
        
        # Store metadata
        st.session_state.data_metadata[name] = {
            'name': name,
            'hash': data_hash,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'rows': len(dataframe),
            'columns': len(dataframe.columns),
            'size_mb': dataframe.memory_usage(deep=True).sum() / 1024 / 1024,
            'column_types': {col: str(dtype) for col, dtype in dataframe.dtypes.items()},
            'missing_values': dataframe.isnull().sum().to_dict(),
            'custom_metadata': metadata
        }
        
        return True, f"Data source '{name}' added successfully"
    
    @staticmethod
    def remove_data_source(name):
        """Remove a data source"""
        if name not in st.session_state.data_sources:
            return False, "Data source not found"
        
        # Check if data source is being used in any dashboard
        dependencies = DataStorageManager.check_data_dependencies(name)
        if dependencies:
            return False, f"Cannot delete: Data source is used in dashboards: {', '.join(dependencies)}"
        
        del st.session_state.data_sources[name]
        del st.session_state.data_metadata[name]
        
        # Clean up cache
        DataStorageManager.clear_cache_for_data_source(name)
        
        return True, f"Data source '{name}' removed successfully"
    
    @staticmethod
    def update_data_source(name, dataframe, preserve_metadata=True):
        """Update an existing data source"""
        if name not in st.session_state.data_sources:
            return False, "Data source not found"
        
        # Generate new hash
        new_hash = DataStorageManager.generate_data_hash(dataframe)
        
        # Update dataframe
        st.session_state.data_sources[name] = dataframe
        
        # Update metadata
        if preserve_metadata:
            existing_metadata = st.session_state.data_metadata[name]
            existing_metadata.update({
                'hash': new_hash,
                'modified': datetime.now().isoformat(),
                'rows': len(dataframe),
                'columns': len(dataframe.columns),
                'size_mb': dataframe.memory_usage(deep=True).sum() / 1024 / 1024,
                'column_types': {col: str(dtype) for col, dtype in dataframe.dtypes.items()},
                'missing_values': dataframe.isnull().sum().to_dict()
            })
        else:
            DataStorageManager.add_data_source(name, dataframe)
        
        # Clear cache for this data source
        DataStorageManager.clear_cache_for_data_source(name)
        
        return True, f"Data source '{name}' updated successfully"
    
    @staticmethod
    def generate_data_hash(dataframe):
        """Generate a hash for data integrity checking"""
        try:
            # Create a string representation of the dataframe
            data_string = f"{dataframe.shape}_{dataframe.dtypes.to_string()}_{dataframe.head().to_string()}"
            return hashlib.md5(data_string.encode()).hexdigest()
        except:
            return hashlib.md5(str(datetime.now()).encode()).hexdigest()
    
    @staticmethod
    def check_data_integrity(name):
        """Check if data source integrity is maintained"""
        if name not in st.session_state.data_sources:
            return False, "Data source not found"
        
        if name not in st.session_state.data_metadata:
            return False, "Metadata not found"
        
        current_hash = DataStorageManager.generate_data_hash(st.session_state.data_sources[name])
        stored_hash = st.session_state.data_metadata[name].get('hash')
        
        return current_hash == stored_hash, current_hash
    
    @staticmethod
    def check_data_dependencies(data_source_name):
        """Check which dashboards depend on a data source"""
        dependencies = []
        
        if 'dashboards' in st.session_state:
            for dashboard_name, dashboard_data in st.session_state.dashboards.items():
                charts = dashboard_data.get('charts', {})
                for chart_config in charts.values():
                    if chart_config.get('data_source') == data_source_name:
                        dependencies.append(dashboard_name)
                        break
        
        return dependencies
    
    @staticmethod
    def get_data_source_info(name):
        """Get detailed information about a data source"""
        if name not in st.session_state.data_sources:
            return None
        
        df = st.session_state.data_sources[name]
        metadata = st.session_state.data_metadata.get(name, {})
        
        info = {
            'name': name,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'null_counts': df.isnull().sum().to_dict(),
            'sample_data': df.head().to_dict('records'),
            'metadata': metadata,
            'dependencies': DataStorageManager.check_data_dependencies(name)
        }
        
        # Add summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            info['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return info
    
    @staticmethod
    def cache_processed_data(cache_key, data, expiry_minutes=30):
        """Cache processed data for performance"""
        expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        
        st.session_state.data_cache[cache_key] = {
            'data': data,
            'expiry': expiry_time.isoformat(),
            'created': datetime.now().isoformat()
        }
        
        # Clean up old cache entries
        DataStorageManager.cleanup_cache()
    
    @staticmethod
    def get_cached_data(cache_key):
        """Retrieve cached data if valid"""
        if cache_key not in st.session_state.data_cache:
            return None
        
        cache_entry = st.session_state.data_cache[cache_key]
        expiry_time = datetime.fromisoformat(cache_entry['expiry'])
        
        if datetime.now() > expiry_time:
            del st.session_state.data_cache[cache_key]
            return None
        
        return cache_entry['data']
    
    @staticmethod
    def clear_cache_for_data_source(data_source_name):
        """Clear cache entries related to a specific data source"""
        keys_to_remove = []
        
        for cache_key in st.session_state.data_cache.keys():
            if data_source_name in cache_key:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del st.session_state.data_cache[key]
    
    @staticmethod
    def cleanup_cache():
        """Remove expired cache entries"""
        current_time = datetime.now()
        keys_to_remove = []
        
        for cache_key, cache_entry in st.session_state.data_cache.items():
            expiry_time = datetime.fromisoformat(cache_entry['expiry'])
            if current_time > expiry_time:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del st.session_state.data_cache[key]
    
    @staticmethod
    def export_data_sources():
        """Export all data sources as a package"""
        try:
            export_data = {
                'data_sources': {},
                'metadata': st.session_state.data_metadata,
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Convert dataframes to JSON-serializable format
            for name, df in st.session_state.data_sources.items():
                export_data['data_sources'][name] = {
                    'data': df.to_dict('records'),
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
            
            return json.dumps(export_data, indent=2, default=str)
            
        except Exception as e:
            return None
    
    @staticmethod
    def import_data_sources(json_data):
        """Import data sources from JSON"""
        try:
            import_data = json.loads(json_data)
            
            if 'data_sources' not in import_data:
                return False, "Invalid data format"
            
            imported_count = 0
            
            for name, source_data in import_data['data_sources'].items():
                # Reconstruct dataframe
                df = pd.DataFrame(source_data['data'])
                
                # Restore data types
                if 'dtypes' in source_data:
                    for col, dtype in source_data['dtypes'].items():
                        if col in df.columns:
                            try:
                                if dtype.startswith('datetime'):
                                    df[col] = pd.to_datetime(df[col])
                                elif dtype in ['int64', 'float64']:
                                    df[col] = pd.to_numeric(df[col], errors='coerce')
                                # Add more type conversions as needed
                            except:
                                pass  # Keep original type if conversion fails
                
                # Add to storage
                success, message = DataStorageManager.add_data_source(name, df)
                if success:
                    imported_count += 1
            
            # Import metadata
            if 'metadata' in import_data:
                for name, metadata in import_data['metadata'].items():
                    if name in st.session_state.data_metadata:
                        st.session_state.data_metadata[name].update(metadata)
            
            return True, f"Imported {imported_count} data sources successfully"
            
        except Exception as e:
            return False, f"Import failed: {str(e)}"
    
    @staticmethod
    def get_storage_stats():
        """Get statistics about data storage"""
        total_sources = len(st.session_state.data_sources)
        total_rows = sum(len(df) for df in st.session_state.data_sources.values())
        total_memory = sum(df.memory_usage(deep=True).sum() for df in st.session_state.data_sources.values())
        
        cache_entries = len(st.session_state.data_cache)
        
        return {
            'total_sources': total_sources,
            'total_rows': total_rows,
            'total_memory_mb': total_memory / 1024 / 1024,
            'cache_entries': cache_entries,
            'largest_source': max(st.session_state.data_sources.items(), 
                                 key=lambda x: len(x[1]), default=('None', pd.DataFrame()))[0] if total_sources > 0 else 'None'
        }
