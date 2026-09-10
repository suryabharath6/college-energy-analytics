# College Campus Energy Consumption Analytics Dashboard ⚡

An interactive web application built with **Streamlit**, **Pandas**, and **Plotly** to analyze college campus electricity usage patterns, detect peak hourly loads, and evaluate departmental consumption.

## 🚀 Features
- **Dynamic CSV File Ingestion:** Upload any campus meter reading CSV file and map columns on the fly.
- **Key Performance Indicators (KPIs):** Displays Total Usage (kWh), Average Consumption, Peak Usage (kWh), and Peak Operational Hour.
- **Interactive Visualizations:**
  - **Line Chart:** Tracks overall energy demand and consumption trends over time.
  - **Bar Chart:** Compares total power usage across different campus buildings/departments.
  - **Heatmap:** Highlights peak hourly usage intensity across days of the week.
  - **Pie Chart:** Shows percentage distribution of energy consumption per facility.
- **Actionable Recommendations:** Suggests load-shifting and automated shutdown strategies to optimize energy efficiency.

## 🛠️ Tech Stack
- **Language:** Python
- **Web Framework:** Streamlit
- **Data Manipulation:** Pandas & NumPy
- **Data Visualization:** Plotly Express

## 📂 Project Structure
```text
├── app.py              # Main Streamlit web application script
├── requirements.txt    # Python library dependencies for deployment
├── .gitignore          # Git ignore file for python caches
└── README.md           # Project documentation
