# ============================================================
# CAMPUS ENERGY ANALYTICS
# ============================================================

# ---------------- IMPORTS ----------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import hashlib
import os
import psycopg2


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Campus Energy Analytics",
    layout="wide"
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_db_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


def initialize_database():

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                activity VARCHAR(255),
                activity_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:

        print("Database initialization error:", e)


# Create table when application starts
initialize_database()


def log_activity(username, activity):

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_activities
            (username, activity)
            VALUES (%s, %s)
            """,
            (username, activity)
        )

        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:

        print("Activity logging error:", e)


# ============================================================
# LOGIN SYSTEM
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def check_login(username, password):

    users = st.secrets["users"]

    if username in users:

        return users[username] == hash_password(password)

    return False


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "username" not in st.session_state:

    st.session_state.username = ""


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title("🔐 Campus Energy Analytics")

    st.subheader("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        type="primary"
    ):

        if check_login(
            username,
            password
        ):

            # Save login state
            st.session_state.logged_in = True

            st.session_state.username = username

            # Record successful login
            log_activity(
                username,
                "Login successful"
            )

            # Reload application
            st.rerun()

        else:

            # Record failed login
            log_activity(
                username,
                "Failed login attempt"
            )

            st.error(
                "❌ Invalid username or password"
            )

    # Stop dashboard from loading
    st.stop()


# ============================================================
# LOGGED-IN USER
# ============================================================

st.sidebar.success(
    f"👤 Logged in as: {st.session_state.username}"
)


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button("🚪 Logout"):

    log_activity(
        st.session_state.username,
        "Logout"
    )

    st.session_state.logged_in = False

    st.session_state.username = ""

    st.rerun()


# ============================================================
# DASHBOARD TITLE
# ============================================================

st.title("⚡ Campus Energy Analytics Dashboard")

st.write(
    "Analyze electricity consumption across campus buildings."
)


# ============================================================
# CSV UPLOAD
# ============================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Electricity CSV",
    type=["csv"]
)


if uploaded_file is not None:

    # Record file upload
    log_activity(
        st.session_state.username,
        f"Uploaded CSV: {uploaded_file.name}"
    )

    # Read CSV
    df = pd.read_csv(uploaded_file)


    # ========================================================
    # DISPLAY RAW DATA
    # ========================================================

    st.subheader("📋 Uploaded Data")

    st.dataframe(
        df,
        use_container_width=True
    )


    # ========================================================
    # SELECT COLUMNS
    # ========================================================

    st.subheader("⚙️ Select Columns")


    columns = df.columns.tolist()


    timestamp_column = st.selectbox(
        "Select Timestamp Column",
        columns
    )


    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()


    if len(numeric_columns) == 0:

        st.error(
            "❌ No numeric column found for electricity usage."
        )

        st.stop()


    usage_column = st.selectbox(
        "Select Electricity Usage Column",
        numeric_columns
    )


    building_column = st.selectbox(
        "Select Building Column",
        columns
    )


    # ========================================================
    # DATA PREPROCESSING
    # ========================================================

    df[timestamp_column] = pd.to_datetime(
        df[timestamp_column],
        errors="coerce"
    )


    df[usage_column] = pd.to_numeric(
        df[usage_column],
        errors="coerce"
    )


    # Remove invalid rows
    df = df.dropna(
        subset=[
            timestamp_column,
            usage_column
        ]
    )


    # ========================================================
    # TIME FEATURES
    # ========================================================

    df["Hour"] = df[
        timestamp_column
    ].dt.hour


    df["DayOfWeek"] = df[
        timestamp_column
    ].dt.day_name()


    df["Month"] = df[
        timestamp_column
    ].dt.month_name()


    # ========================================================
    # KEY METRICS
    # ========================================================

    st.subheader("📊 Energy Consumption Metrics")


    total_usage = df[
        usage_column
    ].sum()


    average_usage = df[
        usage_column
    ].mean()


    peak_usage = df[
        usage_column
    ].max()


    peak_hour = df.loc[
        df[usage_column].idxmax(),
        "Hour"
    ]


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Total Energy Usage",
            f"{total_usage:,.2f}"
        )


    with col2:

        st.metric(
            "Average Energy Usage",
            f"{average_usage:,.2f}"
        )


    with col3:

        st.metric(
            "Peak Energy Usage",
            f"{peak_usage:,.2f}"
        )


    with col4:

        st.metric(
            "Peak Usage Hour",
            f"{int(peak_hour)}:00"
        )


    # ========================================================
    # VISUALIZATIONS
    # ========================================================

    st.subheader("📈 Energy Consumption Visualizations")


    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📈 Line Chart",
            "📊 Bar Chart",
            "🔥 Heatmap",
            "🥧 Pie Chart"
        ]
    )


    # ========================================================
    # LINE CHART
    # ========================================================

    with tab1:

        line_data = df.sort_values(
            timestamp_column
        )


        fig_line = px.line(
            line_data,
            x=timestamp_column,
            y=usage_column,
            title="Electricity Consumption Over Time",
            markers=True
        )


        fig_line.update_layout(
            xaxis_title="Time",
            yaxis_title="Energy Usage"
        )


        st.plotly_chart(
            fig_line,
            use_container_width=True
        )


    # ========================================================
    # BAR CHART
    # ========================================================

    with tab2:

        building_usage = (
            df.groupby(building_column)[usage_column]
            .sum()
            .reset_index()
        )


        fig_bar = px.bar(
            building_usage,
            x=building_column,
            y=usage_column,
            title="Energy Consumption by Building"
        )


        fig_bar.update_layout(
            xaxis_title="Building",
            yaxis_title="Total Energy Usage"
        )


        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )


    # ========================================================
    # HEATMAP
    # ========================================================

    with tab3:

        heatmap_data = df.pivot_table(
            index="DayOfWeek",
            columns="Hour",
            values=usage_column,
            aggfunc="mean"
        )


        # Arrange weekdays correctly
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]


        heatmap_data = heatmap_data.reindex(
            weekday_order
        )


        fig_heatmap = px.imshow(
            heatmap_data,
            title="Average Energy Usage by Day and Hour",
            labels={
                "x": "Hour",
                "y": "Day",
                "color": "Energy Usage"
            },
            aspect="auto"
        )


        st.plotly_chart(
            fig_heatmap,
            use_container_width=True
        )


    # ========================================================
    # PIE CHART
    # ========================================================

    with tab4:

        pie_data = (
            df.groupby(building_column)[usage_column]
            .sum()
            .reset_index()
        )


        fig_pie = px.pie(
            pie_data,
            names=building_column,
            values=usage_column,
            title="Energy Consumption Distribution by Building"
        )


        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.subheader("💡 Energy Saving Recommendations")


    if peak_usage > average_usage * 1.5:

        st.warning(
            "⚠️ Peak consumption is significantly higher "
            "than average consumption. Consider reducing "
            "energy usage during peak hours."
        )

    else:

        st.success(
            "✅ Energy consumption is relatively stable."
        )


    # Find building with highest usage
    highest_building = (
        df.groupby(building_column)[usage_column]
        .sum()
        .idxmax()
    )


    highest_building_usage = (
        df.groupby(building_column)[usage_column]
        .sum()
        .max()
    )


    st.info(
        f"🏢 **Highest Energy Consumption:** "
        f"{highest_building} "
        f"({highest_building_usage:,.2f})"
    )


    st.write(
        "Consider monitoring lighting, HVAC systems, "
        "computers, and other electrical equipment in "
        "high-consumption buildings."
    )


    # ========================================================
    # PROCESSED DATA
    # ========================================================

    st.subheader("📋 Processed Data")

    st.dataframe(
        df,
        use_container_width=True
    )


else:

    st.info(
        "👈 Please upload an electricity consumption CSV "
        "file from the sidebar to start the analysis."
    )
