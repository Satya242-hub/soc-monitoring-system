SOC Monitoring System

A Security Operations Center (SOC) monitoring system built with FastAPI and Streamlit.

Features
- Real-time log ingestion
- Brute force detection
- Malware detection
- Port scan detection
- Live dashboard with alerts

Tech Stack
- FastAPI (Backend)
- SQLAlchemy (Database)
- Streamlit (Dashboard)
- Python 3.10

Installation

pip install fastapi uvicorn sqlalchemy streamlit requests pandas

Run

Start Backend:
cd backend
python -m uvicorn main:app --reload

Start Dashboard:
python -m streamlit run dashboard.py

Dashboard
- Total Logs
- Total Alerts
- Open / Closed Alerts
- Active Alerts Table
- Recent Logs Table
