# ArtiSoul — The Heritage Sphere

Responsive React/Vite client with Django REST API, JWT auth, persistent learning, commerce and event models. Demo translation is explicitly simulated. No real payment or government certificate claim is made.

The original static HTML prototype remains in `Heritage Sphere/` from the repository's existing history; the full-stack application in this directory is the expanded platform implementation.

## Local setup

Requirements: Python 3.11+, Node 20+, npm. Django defaults to SQLite locally; Docker starts PostgreSQL.

1. Copy `.env.example` to `.env`; set a strong `DJANGO_SECRET_KEY` outside local development.
2. Backend: `cd backend; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; python manage.py makemigrations core; python manage.py migrate; python manage.py seed_demo; python manage.py runserver`
3. Frontend: `cd frontend; npm install; npm run dev` (Vite proxies API requests to port 8000).
4. Demo users: `learner@artisoul.in`, `creator@artisoul.in`, `admin@artisoul.in`; password `Heritage123!`.

Docker: `docker compose up --build`. UI at `localhost:5173`, API at `localhost:8000/api/`, admin at `/admin/`. Demo admin login is `admin@artisoul.in` / `Heritage123!`.

API includes auth/register, JWT token/refresh, workshops/enrollment, products/orders, events/bookings, tickets/verification, certificates/verification, recommendations, and translation/demo. DRF browsable API is enabled.

Payments, Azure Speech, streaming and blob storage are provider seams; no credentials or provider confirmation are assumed. Orders/tickets remain pending until confirmation. Real payment acceptance requires verified webhooks. Certificates are ArtiSoul-issued; no government recognition is implied. Production requires managed Postgres, secure secrets, HTTPS, storage, backups, monitoring and integration hardening.
