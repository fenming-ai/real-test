from auth import require_organizer
from data import APPOINTMENTS, INVOICES
from exports import render_csv
from query import date_window, in_window, paginate, tenant_rows

PUBLIC_FIELDS = ("id", "name", "email", "starts_at", "status")
APPOINTMENT_STATUSES = {"confirmed", "pending", "cancelled"}


def filtered_appointments(actor, params):
    require_organizer(actor)
    start, end = date_window(params)
    status = params.get("status", "")
    if status and status not in APPOINTMENT_STATUSES:
        raise ValueError("Status must be confirmed, pending, cancelled, or empty")
    return [row for row in sorted(tenant_rows(APPOINTMENTS, actor), key=lambda row: row["id"])
            if in_window(row["starts_at"], start, end)
            and (not status or row["status"] == status)]


def list_appointments(actor, params):
    rows = filtered_appointments(actor, params)
    page = paginate(rows, params)
    page["items"] = [{key: row[key] for key in PUBLIC_FIELDS} for row in page["items"]]
    return page


def export_appointments(actor, params):
    rows = filtered_appointments(actor, params)
    return render_csv(rows, PUBLIC_FIELDS)


def export_invoices(actor, params):
    require_organizer(actor)
    start, end = date_window(params)
    rows = [row for row in tenant_rows(INVOICES, actor)
            if in_window(row["issued_at"], start, end)]
    return render_csv(rows, ("number", "customer", "amount"))
