import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="College Energy Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Clean CSS (Hides Streamlit branding, keeps sidebar collapse/expand & upload widget)
hide_branding_keep_uploader = """
    <style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Ensure sidebar toggle button stays visible */
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        display: block !important;
    }
    </style>
"""
st.markdown(hide_branding_keep_uploader, unsafe_allow_html=True)

# 3. Sidebar File Uploader
st.sidebar.title("Navigation & Data")
uploaded_file = st.sidebar.file_uploader("Upload Energy Consumption CSV", type=["csv"])

# 4. App Main Content Logic
if uploaded_file is not None:
    st.title("College Campus Energy Analytics Dashboard")
    # Insert your dataframe processing & plot code here
else:
    st.title("College Campus Energy Analytics Dashboard")
    st.info("Please upload a CSV file in the left sidebar to view energy consumption analytics.")
import pandas as pd
import numpy as np
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Campus Energy Analytics", layout="wide")

st.title("⚡ College Campus Energy Consumption Analytics")
st.markdown("Analyze electricity consumption across campus facilities, identify peak hours, and view trends.")

# Sidebar - File Upload & Controls
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Electricity CSV", type=["csv"])

if uploaded_file is not None:
    # Load Data
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")
    
    # Column Mapper Section
    st.sidebar.subheader("⚙️ Select Dataset Columns")
    
    # Pre-select defaults if common column names exist
    col_names = df.columns.tolist()
    
    time_col = st.sidebar.selectbox("Timestamp / Date Column", options=col_names, index=0)
    usage_col = st.sidebar.selectbox("Energy Consumption (kWh) Column", options=col_names, index=1 if len(col_names) > 1 else 0)
    building_col = st.sidebar.selectbox("Building / Department Column (Optional)", options=["None"] + col_names)

    # Process Timestamp Column
    try:
        df[time_col] = pd.to_datetime(df[time_col])
        df['Hour'] = df[time_col].dt.hour
        df['DayOfWeek'] = df[time_col].dt.day_name()
        df['Month'] = df[time_col].dt.strftime('%Y-%m')
    except Exception as e:
        st.warning("Could not convert date column to Datetime format automatically. Basic parsing applied.")

    # Convert usage column to numeric
    df[usage_col] = pd.to_numeric(df[usage_col], errors='coerce').fillna(0)

    # --- TOP METRICS DASHBOARD ---
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Consumption", f"{df[usage_col].sum():,.2f} kWh")
    m2.metric("Average Consumption", f"{df[usage_col].mean():,.2f} kWh")
    m3.metric("Peak Usage", f"{df[usage_col].max():,.2f} kWh")
    
    # Detect Peak Hour
    peak_hour = df.groupby('Hour')[usage_col].mean().idxmax()
    m4.metric("Peak Usage Hour", f"{peak_hour}:00 hrs")

    # --- MAIN VISUALIZATIONS ---
    st.markdown("### 📊 Energy Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Line Chart (Trends)", "Bar Chart (Comparisons)", "Heatmap (Peak Usage)", "Pie Chart (Distribution)"])

    # 1. Line Chart - Consumption Over Time
    with tab1:
        st.subheader("Consumption Trends Over Time")
        fig_line = px.line(df, x=time_col, y=usage_col, color=None if building_col == "None" else building_col,
                           title="Electricity Usage Trend", labels={usage_col: "Energy (kWh)"})
        st.plotly_chart(fig_line, use_container_width=True)

    # 2. Bar Chart - Department / Building Comparison
    with tab2:
        st.subheader("Department / Building Consumption Comparison")
        if building_col != "None":
            dept_df = df.groupby(building_col)[usage_col].sum().reset_index()
            fig_bar = px.bar(dept_df, x=building_col, y=usage_col, color=building_col,
                             title="Total Energy Consumption by Building/Department")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Select a 'Building / Department Column' in the sidebar to view building comparison bar charts.")

    # 3. Heatmap - Hourly Usage vs Day of Week
    with tab3:
        st.subheader("Peak Usage Periods Heatmap")
        if 'DayOfWeek' in df.columns and 'Hour' in df.columns:
            heatmap_data = df.pivot_table(index='DayOfWeek', columns='Hour', values=usage_col, aggfunc='mean')
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex([d for d in days_order if d in heatmap_data.index])
            
            fig_heat = px.imshow(heatmap_data, labels=dict(x="Hour of Day", y="Day of Week", color="Avg kWh"),
                                 x=heatmap_data.columns, y=heatmap_data.index, color_continuous_scale="Viridis")
            st.plotly_chart(fig_heat, use_container_width=True)

    # 4. Pie Chart - Distribution
    with tab4:
        st.subheader("Energy Distribution")
        if building_col != "None":
            fig_pie = px.pie(df, names=building_col, values=usage_col, title="Energy Share by Building")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Select a 'Building / Department Column' in the sidebar to view energy distribution pie charts.")

    # --- INSIGHTS & RECOMMENDATIONS ---
    st.markdown("---")
    st.markdown("### 💡 Recommendations & Insights")
    st.write(f"- **Peak Hour Alert:** High electricity usage consistently occurs around **{peak_hour}:00**. Consider load-shifting high-power laboratory equipment outside this peak window.")
    st.write("- **Energy Saving Strategy:** Schedule automated HVAC and lighting shutdowns in unoccupied lecture halls during off-peak hours.")

    # Raw Data Preview
    with st.expander("View Uploaded Raw Data"):
        st.dataframe(df)

else:
    # Instructions when no file is uploaded
    st.info("👋 Welcome! Please upload your campus energy dataset (CSV file) using the sidebar to generate analysis.")
    st.markdown("""
    **Expected CSV Structure:**
    - A column for **Date/Time** (e.g., `Timestamp`, `Date`, `Time`)
    - A column for **Energy Reading** (e.g., `kWh`, `Consumption`, `Usage`)
    - *(Optional)* A column for **Building/Location** (e.g., `Building`, `Department`, `Hostel`)
    """)
