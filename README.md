# 🏥 Outpatient No-Show Predictor

A data-driven dashboard designed to visualize patient attendance trends and estimate the risk of future appointment "no-shows." Built with Python and Streamlit.

🔗 **[Live Demo](YOUR_STREAMLIT_APP_LINK_HERE)** *(Replace the link above once you deploy your app)*

---

## 📖 Overview
This application helps hospital administrators and staff understand why patients miss appointments. It allows users to filter historical data, view attendance metrics, and uses a basic probability model to predict the likelihood of a specific patient missing their visit based on the day of the week and the reason for the visit.

## ✨ Key Features
* **Interactive Dashboard:** View real-time metrics for Total Appointments, Missed Appointments, and No-Show Rates.
* **🔮 Risk Predictor:** A sidebar tool that calculates the probability of a "No-Show" based on historical patterns (Day of Week + Reason).
* **Data Visualizations:**
    * *Attendance Status:* Donut chart showing the split between Scheduled, No-show, and Cancelled.
    * *Missed Appointment Analysis:* Bar chart breaking down the reasons behind no-shows.
    * *Trend Analysis:* Line chart tracking attendance status over time.
* **Filtering:** Filter the entire dashboard by Date Range and Appointment Status.
* **Export Data:** Download the filtered dataset as a CSV file.

## 🛠️ Technologies Used
* **Streamlit:** For the web application interface.
* **Pandas:** For data manipulation and processing.
* **Plotly Express:** For interactive charts and graphs.

## 📂 Project Structure
```text
├── appointments.csv     # The dataset (Required)
├── app.py               # Main application code
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
