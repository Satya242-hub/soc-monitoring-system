from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime
 
from database import engine, SessionLocal, Base
from models import Log
 
Base.metadata.create_all(bind=engine)
 
app = FastAPI(title="SOC Monitoring System")
 
# ==========================
# MEMORY STORAGE
# ==========================
alerts = []
failed_logins = defaultdict(list)
ip_activity = defaultdict(list)
 
alert_counter = 1
active_alerts = set()
 
 
# ==========================
# DB SESSION
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
# ==========================
# ROOT
# ==========================
@app.get("/")
def root():
    return {"status": "running", "system": "SOC Monitoring System"}
 
 
# ==========================
# LOG INGESTION
# ==========================
@app.post("/logs")
def create_log(log: dict, db: Session = Depends(get_db)):
 
    global alert_counter
 
    ip = log.get("source_ip")
    event = log.get("event_type", "").lower().strip()
    severity = log.get("severity", "low").lower()
 
    if not ip or not event:
        return {"error": "source_ip and event_type are required"}
 
    current_time = datetime.now()
 
    new_log = Log(source_ip=ip, event_type=event, severity=severity)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
 
    ip_activity[ip].append(current_time)
 
    # ==========================
    # BRUTE FORCE DETECTION
    # ==========================
    if "failed" in event:
        failed_logins[ip].append(current_time)
        if len(failed_logins[ip]) >= 5:
            key = f"bruteforce_{ip}"
            if key not in active_alerts:
                alerts.append({
                    "alert_id": alert_counter,
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "OPEN",
                    "type": "Brute Force Attack",
                    "source_ip": ip,
                    "severity": "HIGH",
                    "message": f"Multiple failed login attempts detected from {ip}"
                })
                active_alerts.add(key)
                alert_counter += 1
            failed_logins[ip] = []
 
    # ==========================
    # MALWARE DETECTION
    # ==========================
    if "malware" in event:
        key = f"malware_{ip}"
        if key not in active_alerts:
            alerts.append({
                "alert_id": alert_counter,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "OPEN",
                "type": "Malware Detected",
                "source_ip": ip,
                "severity": "CRITICAL",
                "message": f"Malware activity detected from {ip}"
            })
            active_alerts.add(key)
            alert_counter += 1
 
    # ==========================
    # PORT SCAN DETECTION
    # ==========================
    ip_activity[ip] = [
        t for t in ip_activity[ip]
        if (current_time - t).seconds <= 10
    ]
    if len(ip_activity[ip]) >= 8:
        key = f"portscan_{ip}"
        if key not in active_alerts:
            alerts.append({
                "alert_id": alert_counter,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "OPEN",
                "type": "Port Scan Detected",
                "source_ip": ip,
                "severity": "MEDIUM",
                "message": f"High frequency activity detected from {ip}"
            })
            active_alerts.add(key)
            alert_counter += 1
            ip_activity[ip] = []
 
    return {"message": "log stored", "id": new_log.id}
 
 
# ==========================
# GET LOGS
# ==========================
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    return db.query(Log).all()
 
 
# ==========================
# GET ALERTS
# ==========================
@app.get("/alerts")
def get_alerts():
    return alerts
 
 
# ==========================
# CLOSE ALERT ✅ FIXED
# ==========================
@app.put("/alerts/{alert_id}/close")
def close_alert(alert_id: int):
    for alert in alerts:
        if alert["alert_id"] == alert_id:
            alert["status"] = "CLOSED"
 
            # ✅ match exact keys used during alert creation
            ip = alert["source_ip"]
            type_map = {
                "Brute Force Attack": f"bruteforce_{ip}",
                "Malware Detected":   f"malware_{ip}",
                "Port Scan Detected": f"portscan_{ip}",
            }
            key = type_map.get(alert["type"], "")
            active_alerts.discard(key)
 
            return {"message": f"Alert {alert_id} closed"}
 
    return {"message": "Alert not found"}
 
 
# ==========================
# DASHBOARD STATS
# ==========================
@app.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total_logs = db.query(Log).count()
    return {
        "total_logs": total_logs,
        "total_alerts": len(alerts),
        "open_alerts":   len([a for a in alerts if a["status"] == "OPEN"]),
        "closed_alerts": len([a for a in alerts if a["status"] == "CLOSED"]),
        "high_severity_alerts": len([a for a in alerts if a["severity"].upper() == "HIGH"]),
        "critical_alerts":      len([a for a in alerts if a["severity"].upper() == "CRITICAL"]),
        "medium_alerts":        len([a for a in alerts if a["severity"].upper() == "MEDIUM"])
    }