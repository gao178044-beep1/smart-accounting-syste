
import os, csv, json
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
REPORT_DIR = os.path.join(ROOT, "reports")
TXN_CSV = os.path.join(DATA_DIR, "transactions.csv")
KW_JSON = os.path.join(ROOT, "keywords_en.json")

def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    if not os.path.exists(TXN_CSV):
        with open(TXN_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["date","amount","category","note","account"])

@st.cache_data
def load_keywords():
    with open(KW_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def auto_category(note: str) -> str:
    note_low = (note or "").lower()
    for cat, words in load_keywords().items():
        for w in words:
            if w in note_low:
                return cat
    return "Other"

def read_txns():
    ensure_files()
    return pd.read_csv(TXN_CSV, parse_dates=["date"])

def write_txn_row(row):
    with open(TXN_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

def month_period(s: str) -> str:
    try:
        dt = datetime.strptime(s, "%Y-%m")
        return dt.strftime("%Y-%m")
    except Exception:
        return datetime.now().strftime("%Y-%m")

st.set_page_config(page_title="Smart Accounting System (AUD)", page_icon="💸", layout="wide")

st.title("Smart Accounting System (AUD)")
st.caption("Record expenses, analyze spending, visualize monthly trends, and export CSV.")

with st.sidebar:
    st.header("Add Transaction")
    amt = st.number_input("Amount (AUD)", min_value=0.0, step=1.0, format="%.2f")
    categories = list(load_keywords().keys())
    categories = ["Auto (by Note)"] + categories
    cat = st.selectbox("Category", categories, index=0)
    note = st.text_input("Note", placeholder="e.g., Starbucks latte / Uber to campus")
    account = st.text_input("Account", value="default")
    date_input = st.date_input("Date", value=datetime.now())
    if st.button("➕ Add"):
        chosen_cat = auto_category(note) if cat == "Auto (by Note)" else cat
        write_txn_row([date_input.strftime("%Y-%m-%d"), float(amt), chosen_cat, note, account])
        st.success(f"Added: {date_input} | AUD {amt:.2f} | {chosen_cat} | {note or ''} | {account}")

st.divider()

col1, col2, col3, col4 = st.columns([1.2,1,1,1.2])
with col1:
    month_str = st.text_input("Month (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))
with col2:
    if st.button("Show Monthly Summary"):
        st.session_state['do_summary'] = True
with col3:
    if st.button("Generate Chart"):
        st.session_state['do_chart'] = True
with col4:
    st.download_button("⬇️ Export All Transactions (CSV)",
                       data=open(TXN_CSV, "r", encoding="utf-8").read(),
                       file_name=f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       mime="text/csv")

df = read_txns()
if not df.empty:
    df['ym'] = df['date'].dt.to_period('M').astype(str)
else:
    df['ym'] = []

if st.session_state.get('do_summary'):
    month = month_period(month_str)
    dfm = df[df['ym'] == month]
    st.subheader(f"Monthly Summary — {month}")
    if dfm.empty:
        st.info("No data found for this month.")
    else:
        grp = dfm.groupby('category')['amount'].sum().sort_values(ascending=False).round(2)
        st.dataframe(grp.rename("Amount (AUD)").to_frame())
        st.download_button("⬇️ Export Monthly Summary (CSV)",
                           data=grp.to_csv().encode("utf-8"),
                           file_name=f"summary_{month}.csv",
                           mime="text/csv")

if st.session_state.get('do_chart'):
    month = month_period(month_str)
    dfm = df[df['ym'] == month]
    st.subheader(f"Monthly Spending by Category — {month}")
    if dfm.empty:
        st.info("No data for this month.")
    else:
        s = dfm.groupby('category')['amount'].sum().reset_index()
        fig = px.bar(s, x='category', y='amount',
                     labels={'category': 'Category', 'amount': 'Amount (AUD)'},
                     text='amount',
                     title=f"Monthly Spending by Category — {month}")
        fig.update_traces(texttemplate="AUD %{y:.2f}", textposition="outside")
        fig.update_layout(yaxis_tickprefix="AUD ", uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)
        html_out = os.path.join(REPORT_DIR, f"spending_{month}.html")
        with open(html_out, "w", encoding="utf-8") as f:
            f.write(fig.to_html(include_plotlyjs="cdn"))
        st.caption(f"Chart saved to reports/spending_{month}.html")
