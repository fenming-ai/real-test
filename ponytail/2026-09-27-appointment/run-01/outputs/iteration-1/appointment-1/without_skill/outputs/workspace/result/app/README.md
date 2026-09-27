# Workshop Desk

Small multi-tenant appointment and billing dashboard. Python standard library and
browser ES modules; no build step. All people and credentials here are synthetic.

Run `python3 app.py --port 8765`, open http://127.0.0.1:8765 .
Run regression checks: `python3 -m unittest discover -s tests -v`.

The demo clock is fixed to 2026-09-27 (UTC). Use the account picker to switch
between North organizer, South organizer, and North viewer. These are fixture
identities, not production authentication. Timestamps are ISO 8601 UTC.

API responses use JSON except CSV downloads. Errors use an appropriate HTTP
status and a JSON `error` message. Invalid query parameters must not be ignored.
Appointment pages contain 10 rows. Customer notes and tenant IDs are internal.

Current pages: appointments and invoices. Keep existing behavior working.
