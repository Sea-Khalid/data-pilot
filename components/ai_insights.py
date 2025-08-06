import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def analyze_dataframe_insights(df, chart_config=None):
    """Generate AI-powered insights from dataframe"""
    if not openai_client:
        return generate_rule_based_insights(df, chart_config)
    
    try:
        # Prepare data summary for AI analysis
        summary = prepare_data_summary(df, chart_config)
        
        prompt = f"""Analyze this dataset and provide 3-5 key business insights. Be specific with numbers and trends.

Dataset Summary:
{summary}

Chart Configuration: {chart_config if chart_config else 'General analysis'}

Provide insights in this JSON format:
{{
    "insights": [
        {{
            "type": "trend|anomaly|comparison|correlation",
            "title": "Brief title",
            "description": "Detailed insight with specific numbers",
            "severity": "high|medium|low",
            "action": "Suggested action or investigation"
        }}
    ]
}}

Focus on:
- Significant changes or trends
- Outliers or anomalies
- Correlations between variables
- Business implications
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data analyst expert. Provide clear, actionable business insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("insights", [])
        
    except Exception as e:
        st.warning(f"AI insights unavailable: {str(e)}")
        return generate_rule_based_insights(df, chart_config)

def prepare_data_summary(df, chart_config=None):
    """Prepare a concise summary of the dataframe for AI analysis"""
    summary = []
    
    # Basic info
    summary.append(f"Dataset: {len(df)} rows, {len(df.columns)} columns")
    
    # Column analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    if numeric_cols:
        summary.append(f"Numeric columns: {', '.join(numeric_cols[:5])}")
        for col in numeric_cols[:3]:
            stats = df[col].describe()
            summary.append(f"{col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
    
    if categorical_cols:
        summary.append(f"Categorical columns: {', '.join(categorical_cols[:5])}")
        for col in categorical_cols[:2]:
            top_values = df[col].value_counts().head(3)
            summary.append(f"{col} top values: {dict(top_values)}")
    
    if date_cols:
        summary.append(f"Date columns: {', '.join(date_cols)}")
        for col in date_cols[:1]:
            date_range = f"{df[col].min()} to {df[col].max()}"
            summary.append(f"{col} range: {date_range}")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        summary.append(f"Missing values: {dict(missing[missing > 0])}")
    
    # Chart-specific analysis
    if chart_config:
        x_col = chart_config.get('x_column')
        y_col = chart_config.get('y_column')
        if x_col in df.columns and y_col in df.columns:
            if df[y_col].dtype in ['int64', 'float64']:
                correlation_data = df[[x_col, y_col]].corr().iloc[0, 1] if len(df) > 1 else 0
                summary.append(f"Correlation between {x_col} and {y_col}: {correlation_data:.3f}")
    
    return "\n".join(summary)

def generate_rule_based_insights(df, chart_config=None):
    """Generate insights using rule-based analysis when AI is not available"""
    insights = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Trend analysis
    if len(numeric_cols) > 0:
        for col in numeric_cols[:2]:
            std_dev = df[col].std()
            mean_val = df[col].mean()
            cv = std_dev / mean_val if mean_val != 0 else 0
            
            if cv > 1.0:
                insights.append({
                    "type": "anomaly",
                    "title": f"High Variability in {col}",
                    "description": f"{col} shows high variability (CV: {cv:.2f}). Values range from {df[col].min():.2f} to {df[col].max():.2f}.",
                    "severity": "medium",
                    "action": "Investigate outliers and data quality"
                })
    
    # Missing data analysis
    missing_pct = (df.isnull().sum() / len(df) * 100)
    high_missing = missing_pct[missing_pct > 10]
    
    if not high_missing.empty:
        col_name = high_missing.index[0]
        pct = high_missing.iloc[0]
        insights.append({
            "type": "anomaly",
            "title": f"Missing Data in {col_name}",
            "description": f"{col_name} has {pct:.1f}% missing values ({int(pct/100*len(df))} out of {len(df)} records).",
            "severity": "high" if pct > 25 else "medium",
            "action": "Consider data imputation or investigate data collection process"
        })
    
    # Data distribution analysis
    if chart_config and chart_config.get('y_column') in numeric_cols:
        y_col = chart_config['y_column']
        q1 = df[y_col].quantile(0.25)
        q3 = df[y_col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[y_col] < q1 - 1.5*iqr) | (df[y_col] > q3 + 1.5*iqr)]
        
        if len(outliers) > 0:
            insights.append({
                "type": "anomaly",
                "title": f"Outliers Detected in {y_col}",
                "description": f"Found {len(outliers)} outliers in {y_col} ({len(outliers)/len(df)*100:.1f}% of data).",
                "severity": "low",
                "action": "Review outlier values for data quality or business significance"
            })
    
    # Growth/decline analysis for time series
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if date_cols and chart_config and chart_config.get('y_column') in numeric_cols:
        date_col = date_cols[0]
        y_col = chart_config['y_column']
        
        if len(df) > 1:
            df_sorted = df.sort_values(date_col)
            first_half = df_sorted.iloc[:len(df_sorted)//2][y_col].mean()
            second_half = df_sorted.iloc[len(df_sorted)//2:][y_col].mean()
            
            if first_half > 0:
                change_pct = ((second_half - first_half) / first_half) * 100
                if abs(change_pct) > 10:
                    trend = "increased" if change_pct > 0 else "decreased"
                    insights.append({
                        "type": "trend",
                        "title": f"{y_col} {trend.title()} Over Time",
                        "description": f"{y_col} {trend} by {abs(change_pct):.1f}% from first half to second half of the period.",
                        "severity": "high" if abs(change_pct) > 25 else "medium",
                        "action": f"Investigate factors behind the {trend}"
                    })
    
    return insights[:5]  # Limit to 5 insights

def display_insights_panel(df, chart_config=None):
    """Display the AI insights panel in Streamlit"""
    st.subheader("🧠 AI Insights")
    
    with st.spinner("Generating insights..."):
        insights = analyze_dataframe_insights(df, chart_config)
    
    if not insights:
        st.info("No significant insights found for this data.")
        return
    
    for i, insight in enumerate(insights):
        # Color code by severity
        if insight['severity'] == 'high':
            alert_type = 'error'
            icon = '🔴'
        elif insight['severity'] == 'medium':
            alert_type = 'warning'
            icon = '🟡'
        else:
            alert_type = 'info'
            icon = '🔵'
        
        with st.expander(f"{icon} {insight['title']}", expanded=i==0):
            st.write(insight['description'])
            if insight.get('action'):
                st.info(f"**Suggested Action:** {insight['action']}")
            
            # Add insight type badge
            st.caption(f"Type: {insight['type'].title()} | Severity: {insight['severity'].title()}")

def generate_dashboard_summary_insights(dashboards, data_sources):
    """Generate insights about the overall dashboard collection"""
    if not dashboards or not data_sources:
        return []
    
    insights = []
    total_charts = sum(len(d.get('charts', {})) for d in dashboards.values())
    total_data_points = sum(len(df) for df in data_sources.values())
    
    # Dashboard usage insights
    if total_charts > 10:
        insights.append({
            "type": "summary",
            "title": "Comprehensive Analytics Setup",
            "description": f"You have {len(dashboards)} dashboards with {total_charts} charts analyzing {total_data_points:,} data points.",
            "severity": "low",
            "action": "Consider organizing dashboards by business function"
        })
    
    # Data source insights
    avg_rows_per_source = total_data_points / len(data_sources) if data_sources else 0
    if avg_rows_per_source > 10000:
        insights.append({
            "type": "performance",
            "title": "Large Datasets Detected",
            "description": f"Average of {avg_rows_per_source:,.0f} rows per data source. Consider data sampling for better performance.",
            "severity": "medium",
            "action": "Implement data pagination or filtering"
        })
    
    return insights