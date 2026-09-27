from datetime import date


def date_window(params, start_key="start", end_key="end"):
    start, end = params.get(start_key, ""), params.get(end_key, "")
    if bool(start) != bool(end):
        raise ValueError("Start and end dates must be supplied together")
    if not start:
        return None, None
    for value in (start, end):
        if len(value) != 10 or date.fromisoformat(value).isoformat() != value:
            raise ValueError("Use YYYY-MM-DD dates")
    if start > end:
        raise ValueError("Start date must not be after end date")
    return start, end


def in_window(timestamp, start, end):
    return not start or start <= timestamp[:10] <= end


def tenant_rows(rows, actor):
    return [row for row in rows if row["tenant_id"] == actor["tenant_id"]]


def paginate(rows, params):
    page = int(params.get("page", "1"))
    if page < 1:
        raise ValueError("Page must be positive")
    size = 10
    return {"items": rows[(page - 1) * size:page * size],
            "total": len(rows), "page": page, "page_size": size}
