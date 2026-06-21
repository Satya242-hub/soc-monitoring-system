import streamlit as st
import requests
import pandas as pd

API_URL = https://soc-monitoring-system.onrender.com

st.set_page_config(page_title="SOC Dashboard", layout="wide")
st.title("🛡️ SOC Monitoring Dashboard")

# =========================
# FETCH DATA
# =========================
def get_logs():
    try:
        return requests.get(f"{API_URL}/logs", timeout=3).json()
    except:
        return []

def get_alerts():
    try:
        return requests.get(f"{API_URL}/alerts", timeout=3).json()
    except:
        return []

def get_stats():
    try:
        return requests.get(f"{API_URL}/dashboard/stats", timeout=3).json()
    except:
        return {}

def close_alert(alert_id):
    try:
        requests.put(f"{API_URL}/alerts/{alert_id}/close", timeout=3)
    except:
        pass

# =========================
# STATS SECTION
# =========================
stats = get_stats()

if not stats:
    st.error("⚠️ Backend offline. Run: python -m uvicorn main:app --reload")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Logs",    stats.get("total_logs", 0))
col2.metric("Total Alerts",  stats.get("total_alerts", 0))
col3.metric("Open Alerts",   stats.get("open_alerts", 0))
col4.metric("Closed Alerts", stats.get("closed_alerts", 0))

st.divider()

# =========================
# ALERTS SECTION
# =========================
st.subheader("🚨 Active Alerts")

alerts = get_alerts()

if alerts:
    for a in alerts:
        col1, col2 = st.columns([6, 1])
        sev = a.get("severity", "").upper()
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
        col1.write(f"{icon} **{sev}** · {a.get('message', '')} · IP: `{a.get('source_ip', '')}` · {a.get('status', '')}")
        if a.get("status") == "OPEN":                          # ✅ uppercase
            if col2.button("Close", key=f"close_{a.get('alert_id')}"):
                close_alert(a.get("alert_id"))                 # ✅ alert_id
                st.rerun()
else:
    st.warning("No active alerts found")

st.divider()

# =========================
# LOGS SECTION
# =========================
st.subheader("📄 Recent Logs")

logs = get_logs()

if logs:
    df_logs = pd.DataFrame(logs)
    st.dataframe(df_logs.tail(20), use_container_width=True)
else:
    st.warning("No logs found")

st.divider()

# =========================
# REFRESH BUTTON
# =========================
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
