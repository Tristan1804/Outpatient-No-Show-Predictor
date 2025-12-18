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
    # Get Day of Week (Monday, Tuesday, etc.)
    df["day_of_week"] = df["appointment_date"].dt.day_name()
    return df

df = load_data()

# --- CUSTOM COLOR MAP ---
custom_colors = {
    "Scheduled": "#2A9D8F",  # Teal
    "No-show": "#E76F51",    # Salmon Red
    "Cancelled": "#E9C46A"   # Yellow
}

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🔍 Filter Options")
    
    # Date Filter
    min_date = df["appointment_date"].min()
    max_date = df["appointment_date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Status Filter
    status_options = st.multiselect(
        "Status",
        options=df["status"].unique(),
        default=df["status"].unique()
    )
    
    st.markdown("---")
    
    # --- NEW FEATURE: THE PREDICTOR ---
    st.header("🔮 Risk Predictor")
    st.write("Estimate no-show risk for a new patient:")
    
    # User inputs for prediction
    pred_reason = st.selectbox("Reason for Visit", df["reason_for_visit"].unique())
    pred_day = st.selectbox("Day of Week", df["day_of_week"].unique())
    
    # Prediction Logic
    # 1. Filter data for this specific Day + Reason
    risk_data = df[
        (df["reason_for_visit"] == pred_reason) & 
        (df["day_of_week"] == pred_day)
    ]
    
    # 2. Calculate Probability
    if len(risk_data) > 0:
        risk_count = len(risk_data[risk_data["status"] == "No-show"])
        total_risk_cases = len(risk_data)
        prob = (risk_count / total_risk_cases) * 100
        
        # Display the "Prediction"
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
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data",
        data=csv,
        file_name='no_show_data.csv',
        mime='text/csv'
    )

# Apply Filters for Main Dashboard
filtered_df = df.query(
    "status in @status_options and "
    "@date_range[0] <= appointment_date <= @date_range[1]"
)

# --- MAIN DASHBOARD ---
st.title("Outpatient No-Show Predictor")
st.markdown("### Visualizing and predicting patient attendance patterns")
st.markdown("---")

# Metrics
total = len(filtered_df)
no_shows = len(filtered_df[filtered_df["status"] == "No-show"])
rate = (no_shows / total * 100) if total > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Appointments", total)
c2.metric("Missed Appointments", no_shows)
c3.metric("No-Show Rate", f"{rate:.1f}%")

st.markdown("---")

# --- VISUALIZATIONS ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Attendance Status")
    fig_pie = px.pie(
        filtered_df, 
        names="status", 
        hole=0.5,
        color="status",
        color_discrete_map=custom_colors,
        template="plotly_white"
    )
    fig_pie.update_layout(showlegend=True, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Missed Appointments")
    # Filter only No-Shows
    reason_df = filtered_df[filtered_df["status"]=="No-show"]
    
    if not reason_df.empty:
        reason_counts = reason_df["reason_for_visit"].value_counts().reset_index()
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
        fig_bar.update_layout(coloraxis_showscale=False, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No 'No-Show' data available for current selection.")

# Row 2: Trend Line
st.subheader("Daily Trends: Scheduled vs. No-Show")
daily_trend = filtered_df.groupby(["appointment_date", "status"]).size().reset_index(name="count")

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