# Application Monitoring Center (Command Center Demo)

This is a demo Command Center dashboard built using:

- Prometheus (metrics collection)
- Node/Nginx/Process Exporters
- Alertmanager (alerts)
- Grafana (visualization)
- Flask (custom UI)

## Features
- Application health (UP/DOWN)
- Real-time alerts (Sev1, Sev2, Sev3)
- Auto-refresh with live timer
- Tickets & Release simulation

## How to Run
```bash
pip install -r requirements.txt
python app.py
