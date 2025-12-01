Simple Lead Manager
===================

How to run (locally)
--------------------
1. Create a virtualenv: python -m venv venv
2. Activate it: venv\Scripts\activate  (PowerShell: .\venv\Scripts\Activate.ps1)
3. Install deps: pip install -r requirements.txt
4. Run: python app.py
5. Open http://127.0.0.1:5000/ and login with admin / password

Notes
-----
- This is a minimal demo app—change secret key and secure passwords for production.
- Leads are stored in an SQLite file 'leads.db' next to app.py.
