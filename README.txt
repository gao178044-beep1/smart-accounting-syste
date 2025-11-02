Smart Accounting System (AUD)
====================================

Description
-----------
A simple and interactive accounting web app built with Streamlit and Plotly. 
It records transactions, categorizes expenses, visualizes monthly trends, 
and exports summary reports in CSV format.

Installation
------------
1. Install the required dependencies:
   pip install -r requirements.txt

2. Run the app:
   streamlit run web_app.py

   Then open the URL shown in the terminal (usually http://localhost:8501).

Files
-----
- web_app.py: The main Streamlit app.
- requirements.txt: Python package dependencies.
- data/: Folder containing example data (transactions.csv, budgets.csv).
- reports/: Folder where summary reports and charts are saved.
- .streamlit/config.toml: Streamlit theme configuration (dark mode).

Notes for Tutor
---------------
This app was built by Ge Gao (Gavin) as part of COMP9001 Final Project at the University of Sydney (2025).
The web UI and deployment setup were assisted using ChatGPT for guidance and formatting. 
The core Python logic and data structure design were implemented independently.
