
# Client Portal Pro (Streamlit) — Login + Packages + Expiry + Admin

**Purpose:** Give each client a simple login and show only the tools in their package.  
Includes **expiry/active** controls and a tiny **admin panel** so you can **suspend on non‑payment**.

## Features
- 🔐 Username/password login (Streamlit Authenticator)
- 🎯 Package-based access (Starter/Business/Agency) or per-user tool list
- ⏳ **Expiry date** & **Active toggle** — blocks access automatically
- 🛠️ **Admin Panel** (for usernames in `ADMIN_USERS` env var): edit users, toggle active, set expiry
- 🧭 Tool cards open your deployed apps in new tabs
- ⚙️ YAML config (`users.yaml`, `packages.yaml`, `tools.yaml`)

## Quick Start
```bash
pip install -r requirements.txt
export ADMIN_USERS="owner,admin"          # usernames with admin rights
export PORTAL_COOKIE_KEY="supersecret"    # any random string
streamlit run app.py
```

## Configure
- Create password hashes with: `python hash_passwords.py`
- Edit `users.yaml` and paste hash into `password` field.
- Set `package:` OR `allowed_tools:` and **expiry/active** per user.

> Note: File writes persist on your server/VM. On Streamlit Cloud, edits persist until the app is redeployed; for long-term storage use a small DB or push changes back to Git via API.
