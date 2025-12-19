import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Outpatient No-Show Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("appointments.csv")
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    df["day_of_week"] = df["appointment_date"].dt.day_name()
    return df

df = load_data()

# --- CUSTOM COLOR MAP ---
custom_colors = {
    "Scheduled": "#2A9D8F",  # Teal
    "No-show": "#E76F51",    # Salmon Red
    "Cancelled": "#E9C46A"   # Yellow
}

# --- 2. SIDEBAR (PREDICTOR & DOWNLOAD) ---
with st.sidebar:
    # --- PREDICTOR ---
    st.header("🔮 Risk Predictor")
    st.write("Estimate no-show risk for a new patient:")
    
    pred_reason = st.selectbox("Reason for Visit", df["reason_for_visit"].unique())
    pred_day = st.selectbox("Day of Week", df["day_of_week"].unique())
    
    risk_data = df[(df["reason_for_visit"] == pred_reason) & (df["day_of_week"] == pred_day)]
    
    if len(risk_data) > 0:
        risk_count = len(risk_data[risk_data["status"] == "No-show"])
        total_risk_cases = len(risk_data)
        prob = (risk_count / total_risk_cases) * 100
        
        if prob > 50:
            st.error(f"⚠️ High Risk: {prob:.1f}% chance of No-Show")
        elif prob > 20:
            st.warning(f"⚠️ Moderate Risk: {prob:.1f}% chance")
        else:
            st.success(f"✅ Low Risk: {prob:.1f}% chance")
        st.caption(f"Based on {total_risk_cases} past records.")
    else:
        st.info("Insufficient data for this combination.")

    st.markdown("---")
    
    # --- DOWNLOAD BUTTON ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data",
        data=csv,
        file_name='no_show_data.csv',
        mime='text/csv'
    )

# --- MAIN DASHBOARD ---
st.title("Outpatient No-Show Predictor")
st.markdown("### Visualizing patient appointment attendance patterns")

# --- TOP PAGE FILTERS (DATE ONLY) ---
min_date = df["appointment_date"].min()
max_date = df["appointment_date"].max()
date_range = st.date_input(
    "Select Appointment Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply Global Date Filter
filtered_df = df[
    (df["appointment_date"] >= pd.Timestamp(date_range[0])) & 
    (df["appointment_date"] <= pd.Timestamp(date_range[1]))
]

# Metrics
total = len(filtered_df)
no_shows = len(filtered_df[filtered_df["status"] == "No-show"])
rate = (no_shows / total * 100) if total > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Appointments", total)
c2.metric("Missed Appointments", no_shows)
c3.metric("No-Show Rate", f"{rate:.1f}%")

st.markdown("---")

# --- VISUALIZATIONS WITH INDIVIDUAL FILTERS ---

col1, col2 = st.columns([1, 1])

# helper for "All" option
def get_options_with_all(column_name):
    options = list(df[column_name].unique())
    options.sort()
    return ["All"] + options

with col1:
    st.subheader("Attendance Status")
    # Local Filter for Pie
    status_choice = st.multiselect("Filter Status:", get_options_with_all("status"), default=["All"], key="pie_status")
    
    pie_data = filtered_df.copy()
    if "All" not in status_choice:
        pie_data = pie_data[pie_data["status"].isin(status_choice)]

    fig_pie = px.pie(
        pie_data, 
        names="status", 
        hole=0.5,
        color="status",
        color_discrete_map=custom_colors,
        template="plotly_white"
    )
    fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Missed Appointments by Reason")
    # Local Filter for Bar
    reason_choice = st.multiselect("Filter Reason:", get_options_with_all("reason_for_visit"), default=["All"], key="bar_reason")
    
    bar_data = filtered_df[filtered_df["status"] == "No-show"]
    if "All" not in reason_choice:
        bar_data = bar_data[bar_data["reason_for_visit"].isin(reason_choice)]
    
    if not bar_data.empty:
        reason_counts = bar_data["reason_for_visit"].value_counts().reset_index()
        reason_counts.columns = ["Reason", "Count"]
        
        fig_bar = px.bar(
            reason_counts, 
            x="Reason", 
            y="Count", 
            color="Count",
            color_continuous_scale="Reds",
            text_auto=True,
            template="plotly_white"
        )
        fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data for current selection.")

# Row 2: Trend Line
st.subheader("Daily Trends: Scheduled vs. No-Show")
# Local Filter for Trend Line
day_choice = st.multiselect("Filter Day of Week:", get_options_with_all("day_of_week"), default=["All"], key="line_day")

trend_data = filtered_df.copy()
if "All" not in day_choice:
    trend_data = trend_data[trend_data["day_of_week"].isin(day_choice)]

daily_trend = trend_data.groupby(["appointment_date", "status"]).size().reset_index(name="count")

if not daily_trend.empty:
    fig_line = px.line(
        daily_trend, 
        x="appointment_date", 
        y="count", 
        color="status",
        color_discrete_map=custom_colors,
        markers=True,
        template="plotly_white"
    )
    # Ensure base is zero
    fig_line.update_yaxes(rangemode="tozero")
    fig_line.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No data available for trend analysis.")

# --- FOOTER ---
st.markdown("---")
st.caption(
    "**Data Source:** [Kaggle - Hospital Management Dataset]"
    "(https://www.kaggle.com/datasets/kanakbaghel/hospital-management-dataset?resource=download)"
)
