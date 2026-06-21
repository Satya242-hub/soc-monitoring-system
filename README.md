SOC Monitoring System

A Security Operations Center (SOC) monitoring system built with FastAPI and Streamlit.

Live Demo
- Dashboard: https://satya242-hub-soc-monitoring-system-dashboard-41gtly.streamlit.app
- API Docs: https://soc-monitoring-system.onrender.com/docs

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

pip install -r requirements.txt

Run

Start Backend:
uvicorn main:app --reload

Start Dashboard:
python -m streamlit run dashboard.py
