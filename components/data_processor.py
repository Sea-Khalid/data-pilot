import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class DataProcessor:
    """Component for processing and transforming data"""
    
    @staticmethod
    def detect_data_types(df):
        """Automatically detect and suggest data types"""
        suggestions = {}
        
        for col in df.columns:
            current_type = str(df[col].dtype)
            suggestion = current_type
            
            # Skip if already processed correctly
            if current_type.startswith('datetime'):
                continue
                
            # Try to detect dates
            if current_type == 'object':
                sample_values = df[col].dropna().head(100)
                
                # Check for date patterns
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                    r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
                    r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
                ]
                
                date_like_count = 0
                for value in sample_values.astype(str):
                    for pattern in date_patterns:
                        if re.match(pattern, value):
                            date_like_count += 1
                            break
                
                if date_like_count / len(sample_values) > 0.7:
                    suggestion = 'datetime64[ns]'
                
                # Check for numeric values stored as strings
                try:
                    pd.to_numeric(sample_values, errors='raise')
                    suggestion = 'float64'
                except:
                    pass
            
            if suggestion != current_type:
                suggestions[col] = suggestion
        
        return suggestions
    
    @staticmethod
    def clean_column_names(df):
        """Clean and standardize column names"""
        cleaned_df = df.copy()
        
        # Store original names for reference
        original_names = list(cleaned_df.columns)
        
        # Clean column names
        new_names = []
        for col in original_names:
            # Remove special characters and replace with underscore
            clean_name = re.sub(r'[^a-zA-Z0-9]', '_', str(col))
            # Remove multiple underscores
            clean_name = re.sub(r'_+', '_', clean_name)
            # Remove leading/trailing underscores
            clean_name = clean_name.strip('_')
            # Ensure it starts with a letter
            if clean_name and clean_name[0].isdigit():
                clean_name = 'col_' + clean_name
            # Handle empty names
            if not clean_name:
                clean_name = f'col_{len(new_names)}'
            
            new_names.append(clean_name)
        
        # Handle duplicates
        final_names = []
        for name in new_names:
            if name in final_names:
                counter = 1
                while f"{name}_{counter}" in final_names:
                    counter += 1
                final_names.append(f"{name}_{counter}")
            else:
                final_names.append(name)
        
        cleaned_df.columns = final_names
        return cleaned_df, dict(zip(final_names, original_names))
    
    @staticmethod
    def handle_missing_values(df, strategy='auto'):
        """Handle missing values in the dataset"""
        cleaned_df = df.copy()
        
        if strategy == 'auto':
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype in ['object', 'category']:
                    # Fill categorical columns with mode or 'Unknown'
                    if not cleaned_df[col].mode().empty:
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
                    else:
                        cleaned_df[col] = cleaned_df[col].fillna('Unknown')
                else:
                    # Fill numeric columns with median
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
        
        elif strategy == 'drop':
            cleaned_df = cleaned_df.dropna()
        
        elif strategy == 'forward_fill':
            cleaned_df = cleaned_df.fillna(method='ffill')
        
        elif strategy == 'backward_fill':
            cleaned_df = cleaned_df.fillna(method='bfill')
        
        return cleaned_df
    
    @staticmethod
    def remove_outliers(df, columns=None, method='iqr', threshold=1.5):
        """Remove outliers from numeric columns"""
        cleaned_df = df.copy()
        
        if columns is None:
            columns = cleaned_df.select_dtypes(include=[np.number]).columns
        
        outlier_indices = set()
        
        for col in columns:
            if col in cleaned_df.columns and cleaned_df[col].dtype in [np.number]:
                if method == 'iqr':
                    Q1 = cleaned_df[col].quantile(0.25)
                    Q3 = cleaned_df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    col_outliers = cleaned_df[(cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)].index
                    outlier_indices.update(col_outliers)
                
                elif method == 'zscore':
                    z_scores = np.abs((cleaned_df[col] - cleaned_df[col].mean()) / cleaned_df[col].std())
                    col_outliers = cleaned_df[z_scores > threshold].index
                    outlier_indices.update(col_outliers)
        
        # Remove outliers
        cleaned_df = cleaned_df.drop(outlier_indices)
        
        return cleaned_df, len(outlier_indices)
    
    @staticmethod
    def convert_data_types(df, type_mapping):
        """Convert data types based on mapping"""
        converted_df = df.copy()
        conversion_results = {}
        
        for col, target_type in type_mapping.items():
            if col not in converted_df.columns:
                continue
                
            try:
                if target_type == 'datetime64[ns]':
                    converted_df[col] = pd.to_datetime(converted_df[col], errors='coerce')
                elif target_type == 'float64':
                    converted_df[col] = pd.to_numeric(converted_df[col], errors='coerce')
                elif target_type == 'int64':
                    converted_df[col] = pd.to_numeric(converted_df[col], errors='coerce').astype('Int64')
                elif target_type == 'category':
                    converted_df[col] = converted_df[col].astype('category')
                
                conversion_results[col] = 'success'
            except Exception as e:
                conversion_results[col] = f'failed: {str(e)}'
        
        return converted_df, conversion_results
    
    @staticmethod
    def create_derived_columns(df, operations):
        """Create derived columns based on operations"""
        enhanced_df = df.copy()
        
        for operation in operations:
            try:
                col_name = operation['name']
                expr = operation['expression']
                
                # Simple expression evaluation (could be expanded)
                if 'date_part' in operation:
                    # Extract date parts
                    date_col = operation['source_column']
                    if date_col in enhanced_df.columns and enhanced_df[date_col].dtype.name.startswith('datetime'):
                        if operation['date_part'] == 'year':
                            enhanced_df[col_name] = enhanced_df[date_col].dt.year
                        elif operation['date_part'] == 'month':
                            enhanced_df[col_name] = enhanced_df[date_col].dt.month
                        elif operation['date_part'] == 'day':
                            enhanced_df[col_name] = enhanced_df[date_col].dt.day
                        elif operation['date_part'] == 'weekday':
                            enhanced_df[col_name] = enhanced_df[date_col].dt.day_name()
                        elif operation['date_part'] == 'quarter':
                            enhanced_df[col_name] = enhanced_df[date_col].dt.quarter
                
                elif 'calculation' in operation:
                    # Simple mathematical operations
                    col1 = operation['column1']
                    col2 = operation['column2']
                    op = operation['calculation']
                    
                    if col1 in enhanced_df.columns and col2 in enhanced_df.columns:
                        if op == 'add':
                            enhanced_df[col_name] = enhanced_df[col1] + enhanced_df[col2]
                        elif op == 'subtract':
                            enhanced_df[col_name] = enhanced_df[col1] - enhanced_df[col2]
                        elif op == 'multiply':
                            enhanced_df[col_name] = enhanced_df[col1] * enhanced_df[col2]
                        elif op == 'divide':
                            enhanced_df[col_name] = enhanced_df[col1] / enhanced_df[col2]
                        elif op == 'percentage':
                            enhanced_df[col_name] = (enhanced_df[col1] / enhanced_df[col2]) * 100
                
            except Exception as e:
                st.warning(f"Failed to create column {operation.get('name', 'unknown')}: {str(e)}")
        
        return enhanced_df
    
    @staticmethod
    def generate_data_profile(df):
        """Generate a comprehensive data profile"""
        profile = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'duplicate_rows': df.duplicated().sum()
            },
            'column_info': {},
            'data_quality': {}
        }
        
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].notna().sum(),
                'null_count': df[col].isna().sum(),
                'null_percentage': (df[col].isna().sum() / len(df)) * 100
            }
            
            if df[col].dtype in ['object', 'category']:
                col_info.update({
                    'unique_values': df[col].nunique(),
                    'most_frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'frequency_of_most': df[col].value_counts().iloc[0] if not df[col].empty else 0
                })
            elif df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'zeros': (df[col] == 0).sum()
                })
            elif df[col].dtype.name.startswith('datetime'):
                col_info.update({
                    'min_date': df[col].min(),
                    'max_date': df[col].max(),
                    'date_range_days': (df[col].max() - df[col].min()).days if df[col].notna().any() else 0
                })
            
            profile['column_info'][col] = col_info
        
        return profile
