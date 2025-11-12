import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

from utility import check_password

# region <--------- Streamlit Page Configuration --------->

st.set_page_config(
    layout="centered",
    page_title="My Streamlit App"
)

# Do not continue if valid_password is not True.
if not check_password():
    st.stop()

# endregion <--------- Streamlit Page Configuration --------->


# Load and prepare data
@st.cache_data

def load_actual_data():
    
    file_path = os.path.join("Unfunded prog db data - sample.csv")
    df = pd.read_csv(file_path)

    return df

# Main dashboard
def main():
    st.title("📊 Unfunded Programmes Dashboard")
    st.markdown("---")
    
    # Load data
    df = load_actual_data()  # Replace with load_actual_data() when ready
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Service User filter
    service_users = st.sidebar.multiselect(
        "Select Primary Service User:",
        options=df['Primary Service User'].unique(),
        default=df['Primary Service User'].unique()
    )
    
    # Service Type filter
    service_types = st.sidebar.multiselect(
        "Select Primary Service Type:",
        options=df['Primary Service Type'].unique(),
        default=df['Primary Service Type'].unique()[:5]  # Limit default selection
    )
    
    # Expenditure range filter
    expenditure_ranges = st.sidebar.multiselect(
        "Select Expenditure Range:",
        options=df['Programme expenditure (range)'].unique(),
        default=df['Programme expenditure (range)'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['Primary Service User'].isin(service_users)) &
        (df['Primary Service Type'].isin(service_types)) &
        (df['Programme expenditure (range)'].isin(expenditure_ranges))
    ]
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Programmes",
            value=len(filtered_df),
            delta=f"{len(filtered_df) - len(df)} from total"
        )
    
    with col2:
        st.metric(
            label="Total Agencies",
            value=filtered_df['Agency Name'].nunique(),
            delta=f"{filtered_df['Agency Name'].nunique() - df['Agency Name'].nunique()} from total"
        )
    
    with col3:
        st.metric(
            label="Total Service Users",
            value=f"{filtered_df['Number of service users'].sum():,}",
            delta=f"{filtered_df['Number of service users'].sum() - df['Number of service users'].sum():,} from total"
        )
    
    with col4:
        st.metric(
            label="Avg Users per Programme",
            value=f"{filtered_df['Number of service users'].mean():.0f}",
            delta=f"{filtered_df['Number of service users'].mean() - df['Number of service users'].mean():.0f} from total"
        )
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Programme Distribution by Expenditure Range")
        
        # Donut chart for expenditure distribution
        expenditure_counts = filtered_df['Programme expenditure (range)'].value_counts()
        
        fig_donut = px.pie(
            values=expenditure_counts.values,
            names=expenditure_counts.index,
            hole=0.4,
            title="Programme Distribution by Expenditure Range"
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(height=400)
        st.plotly_chart(fig_donut, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Top 10 Agencies by Programme Count")
        
        # Bar chart for top agencies
        top_agencies = filtered_df['Agency Name'].value_counts().head(10)
        
        fig_bar = px.bar(
            x=top_agencies.values,
            y=top_agencies.index,
            orientation='h',
            title="Top 10 Agencies by Number of Programmes",
            labels={'x': 'Number of Programmes', 'y': 'Agency Name'}
        )
        fig_bar.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Second row of visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Service Users by Primary Service User")
        
        user_distribution = filtered_df.groupby('Primary Service User')['Number of service users'].sum().reset_index()
        
        fig_pie = px.pie(
            user_distribution,
            values='Number of service users',
            names='Primary Service User',
            title="Distribution of Service Users by Category"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Service Types Analysis")
        
        service_analysis = filtered_df.groupby('Primary Service Type').agg({
            'Programme Name': 'count',
            'Number of service users': 'sum'
        }).reset_index()
        service_analysis.columns = ['Service Type', 'Programme Count', 'Total Users']
        
        fig_scatter = px.scatter(
            service_analysis,
            x='Programme Count',
            y='Total Users',
            size='Total Users',
            hover_name='Service Type',
            title="Service Types: Programme Count vs Total Users"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Expenditure vs Service Users Analysis
    st.subheader("💰 Expenditure Range vs Service Users")
    
    expenditure_analysis = filtered_df.groupby(['Programme expenditure (range)', 'Primary Service User']).agg({
        'Number of service users': 'sum',
        'Programme Name': 'count'
    }).reset_index()
    
    fig_stacked = px.bar(
        expenditure_analysis,
        x='Programme expenditure (range)',
        y='Number of service users',
        color='Primary Service User',
        title="Service Users by Expenditure Range and User Category",
        labels={'Number of service users': 'Total Service Users'}
    )
    fig_stacked.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig_stacked, use_container_width=True)
    
    # Data table
    st.subheader("📋 Filtered Data")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search programmes or agencies:")
    if search_term:
        mask = (
            filtered_df['Programme Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['Agency Name'].str.contains(search_term, case=False, na=False)
        )
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    
    # Display options
    col1, col2 = st.columns(2)
    with col1:
        show_rows = st.selectbox("Rows to display:", [10, 25, 50, 100], index=1)
    with col2:
        sort_by = st.selectbox("Sort by:", ['Number of service users', 'Agency Name', 'Programme Name'])
    
    # Sort and display
    display_df = display_df.sort_values(sort_by, ascending=False).head(show_rows)
    
    st.dataframe(
        display_df[['Agency Name', 'Programme Name', 'Primary Service User', 
                   'Primary Service Type', 'Number of service users', 'Programme expenditure (range)']],
        use_container_width=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name='filtered_programmes.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()
st.title("Streamlit App")
form = st.form(key="form")
form.subheader("Prompt")

user_prompt = form.text_area("Enter your prompt here", height=200)


if form.form_submit_button("Submit"):
    st.toast(f"User has submitted {user_prompt}")
