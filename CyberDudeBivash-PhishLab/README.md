# CyberDudeBivash Phishing Simulation Lab
A secure, legal, and enterprise-grade phishing awareness & behavioral analysis simulation platform developed by **CyberDudeBivash**.

This application allows red-team operators and security teams to:
- Create phishing simulation campaigns
- Generate unique training links for targets
- Host generic “training login pages”
- Track user behaviour (clicked, submitted, reported)
- Produce awareness scoring and campaign statistics
⚠️ **IMPORTANT:**  
This project performs *simulated* phishing flows ONLY.  
It does **not** proxy or interact with real authentication systems or capture real credentials.

---

## Features
- Create training campaigns via /admin API
- Add targets (email/name) with unique links
- User-friendly simulated login page
- Tracks:
  - Who clicked
  - Who submitted the form
  - Timestamps
- No credential storage (safety-first, compliance-friendly)
- Templates using sleek CyberDudeBivash dark theme

---

## Tech Stack
### Backend
- Python 3.x
- Flask
- SQLAlchemy
- SQLite (MVP)

### Frontend
- HTML/CSS (Flask templates)
- Optional migration to React later

---

## Project Structure
```
cdb_phishlab/
  backend/
    app.py
    models.py
    routes_public.py
    routes_admin.py
    config.py
    templates/
      landing_generic.html
      landing_success.html
    __init__.py
  requirements.txt
  README.md
```

---

## Installation

### 1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install requirements
```bash
pip install -r requirements.txt
```

### 3. Initialize the database
```bash
flask --app backend/app.py init-db
```

### 4. Run the application
```bash
flask --app backend/app.py run
```

App will start at:
```
http://127.0.0.1:5000
```

---

## API Overview

### Create a Campaign
```
POST /admin/campaigns
{
  "name": "November Awareness Test",
  "description": "Wave 1"
}
```

### Add Targets
```
POST /admin/campaigns/<id>/targets
{
  "targets": [
    { "email": "user@example.com", "name": "Alice" },
    { "email": "bob@example.com" }
  ]
}
```

### Campaign Training Link
```
GET /t/<unique_token>
```

---

## Templates
- `/templates/landing_generic.html` → Simulated login page  
- `/templates/landing_success.html` → Training completion page  

These are customizable and support full theming.

---

## Security Notes
- No passwords or credentials are stored.
- No reverse-proxy or interception logic exists.
- All interactions remain inside a controlled simulation environment.

---

## License
Private, internal use for **CyberDudeBivash Pvt Ltd** only.

---

## Author
**Bivash Kumar Nayak**  
CyberDudeBivash Pvt Ltd  
https://cyberdudebivash.com

