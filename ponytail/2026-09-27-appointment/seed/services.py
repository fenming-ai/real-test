from auth import require_organizer
from data import APPOINTMENTS, INVOICES
from exports import render_csv
from query import date_window, in_window, paginate, tenant_rows

PUBLIC_FIELDS = ("id", "name", "email", "starts_at", "status")


def list_appointments(actor, params):
    require_organizer(actor)
    rows = sorted(tenant_rows(APPOINTMENTS, actor), key=lambda row: row["id"])
    page = paginate(rows, params)
    page["items"] = [{key: row[key] for key in PUBLIC_FIELDS} for row in page["items"]]
    return page


def export_invoices(actor, params):
    require_organizer(actor)
    start, end = date_window(params)
    rows = [row for row in tenant_rows(INVOICES, actor)
            if in_window(row["issued_at"], start, end)]
    return render_csv(rows, ("number", "customer", "amount"))
