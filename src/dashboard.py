import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import time

# Constants
RESOURCE_TYPE_MAP = {
    1: 'Internal',
    2: 'External',
    3: 'Mixed'
}

PHASE_ORDER = ['Planning', 'In Progress', 'On Hold', 'Completed']

# Set page config
st.set_page_config(
    page_title="Project Portfolio Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database connection with shorter cache
@st.cache_resource(ttl=60)  # Cache expires after 60 seconds
def get_db_connection():
    try:
        db_path = Path("data/project_tracker.db")
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return None

# Load data with shorter cache
@st.cache_data(ttl=60)  # Cache expires after 60 seconds
def load_data():
    conn = get_db_connection()
    if conn is not None:
        try:
            df = pd.read_sql_query("SELECT * FROM idea_store", conn)
            df['resource_type_label'] = df['resource_type'].map(RESOURCE_TYPE_MAP)
            return df
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()

def render_dashboard_tab(df):
    # Top level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(df))
    with col2:
        st.metric("High Priority Projects", len(df[df['priority_level'] >= 3]))
    with col3:
        st.metric("Active Projects", len(df[df['project_phase'] == 'In Progress']))
    with col4:
        st.metric("Categories", df['category'].nunique())

    # Two columns layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # Project Distribution by Category and Priority
        st.subheader("Project Distribution")
        if not df.empty:
            fig = px.treemap(
                df,
                path=['category', 'project_name'],
                values='priority_level',
                color='priority_level',
                color_continuous_scale='viridis',
                title='Projects by Category and Priority'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Project Phase Pipeline - Updated version
        st.subheader("Project Pipeline")
        phase_counts = df['project_phase'].value_counts().reindex(PHASE_ORDER).fillna(0)
        
        # Create a more appealing Sankey-like pipeline
        fig = go.Figure()
        
        # Add the main bars
        fig.add_trace(go.Bar(
            x=phase_counts.values,
            y=PHASE_ORDER,
            orientation='h',
            text=phase_counts.values,
            textposition='auto',
            marker=dict(
                color=['#2ecc71', '#3498db', '#f1c40f', '#9b59b6'],  # Different color for each phase
                line=dict(color='rgba(0,0,0,0)', width=1)
            ),
            hovertemplate="Phase: %{y}<br>Projects: %{x}<extra></extra>"
        ))
        
        # Update layout for better appearance
        fig.update_layout(
            title=dict(
                text="Project Pipeline Status",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=20)
            ),
            xaxis=dict(
                title="Number of Projects",
                showgrid=True,
                gridcolor='rgba(211,211,211,0.3)',
                zeroline=False
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                zeroline=False
            ),
            plot_bgcolor='white',
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            bargap=0.3
        )
        
        # Add percentage annotations
        total_projects = phase_counts.sum()
        if total_projects > 0:
            percentages = (phase_counts / total_projects * 100).round(1)
            for i, (count, percentage) in enumerate(zip(phase_counts, percentages)):
                if count > 0:
                    fig.add_annotation(
                        x=count,
                        y=PHASE_ORDER[i],
                        text=f"{percentage}%",
                        showarrow=False,
                        xanchor='left',
                        xshift=10,
                        font=dict(size=12)
                    )
        
        st.plotly_chart(fig, use_container_width=True)

        # Add phase transition metrics
        st.caption("Pipeline Health")
        metric_cols = st.columns(4)
        with metric_cols[0]:
            planning_ratio = len(df[df['project_phase'] == 'Planning']) / len(df) * 100 if len(df) > 0 else 0
            st.metric("Planning", f"{planning_ratio:.1f}%", 
                     help="Percentage of projects in planning phase")
        with metric_cols[1]:
            progress_ratio = len(df[df['project_phase'] == 'In Progress']) / len(df) * 100 if len(df) > 0 else 0
            st.metric("In Progress", f"{progress_ratio:.1f}%",
                     help="Percentage of projects in progress")
        with metric_cols[2]:
            hold_ratio = len(df[df['project_phase'] == 'On Hold']) / len(df) * 100 if len(df) > 0 else 0
            st.metric("On Hold", f"{hold_ratio:.1f}%",
                     help="Percentage of projects on hold")
        with metric_cols[3]:
            completion_ratio = len(df[df['project_phase'] == 'Completed']) / len(df) * 100 if len(df) > 0 else 0
            st.metric("Completed", f"{completion_ratio:.1f}%",
                     help="Percentage of completed projects")

    with right_col:
        # Risk vs Impact Matrix
        st.subheader("Risk vs Impact Matrix")
        risk_impact_df = df.groupby(['risk_level', 'business_impact']).size().reset_index(name='count')
        fig = px.scatter(
            risk_impact_df,
            x='risk_level',
            y='business_impact',
            size='count',
            color='count',
            title='Risk vs Business Impact',
            labels={'risk_level': 'Risk Level', 'business_impact': 'Business Impact'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Resource Type Distribution
        resource_df = pd.DataFrame({
            'type': list(RESOURCE_TYPE_MAP.values()),
            'count': [len(df[df['resource_type'] == i]) for i in RESOURCE_TYPE_MAP.keys()]
        })
        fig = px.pie(
            resource_df,
            values='count',
            names='type',
            title='Resource Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_projects_tab(df):
    # Project Details Table
    st.subheader("Project Details")
    
    # Filters in a single row
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            options=sorted(df['category'].unique())
        )
    with col2:
        phase_filter = st.multiselect(
            "Filter by Phase",
            options=PHASE_ORDER
        )
    with col3:
        priority_filter = st.slider(
            "Minimum Priority Level",
            min_value=1,
            max_value=4,
            value=1
        )

    # Apply filters
    filtered_df = df.copy()
    if category_filter:
        filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
    if phase_filter:
        filtered_df = filtered_df[filtered_df['project_phase'].isin(phase_filter)]
    filtered_df = filtered_df[filtered_df['priority_level'] >= priority_filter]

    # Display filtered table with enhanced styling
    st.dataframe(
        filtered_df[[
            'project_name', 'category', 'priority_level', 'project_phase',
            'business_impact', 'risk_level', 'notes'
        ]],
        hide_index=True,
        use_container_width=True,
        column_config={
            'project_name': 'Project Name',
            'category': 'Category',
            'priority_level': st.column_config.NumberColumn('Priority', help='1-4 (higher is more important)'),
            'project_phase': 'Phase',
            'business_impact': st.column_config.NumberColumn('Impact', help='1-4 (higher is more impactful)'),
            'risk_level': st.column_config.NumberColumn('Risk', help='1-3 (higher is riskier)'),
            'notes': 'Notes'
        }
    )

def main():
    st.title("🚀 Project Portfolio Dashboard")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please check your database connection.")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Project Details"])
    
    with tab1:
        render_dashboard_tab(df)
        
    with tab2:
        render_projects_tab(df)
    
    # Add refresh button at the bottom
    st.divider()  # Add a visual separator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        st.caption("Data automatically refreshes every 60 seconds", help="The dashboard will update with any new data every minute")

if __name__ == "__main__":
    main() 
