from datetime import date


APPOINTMENT_STATUSES = ("confirmed", "pending", "cancelled")


def date_window(params, start_key="start", end_key="end"):
    start, end = params.get(start_key, ""), params.get(end_key, "")
    if bool(start) != bool(end):
        raise ValueError("开始日期和结束日期必须同时填写")
    if not start:
        return None, None
    for value in (start, end):
        try:
            valid = len(value) == 10 and date.fromisoformat(value).isoformat() == value
        except (TypeError, ValueError):
            valid = False
        if not valid:
            raise ValueError("日期格式必须为 YYYY-MM-DD")
    if start > end:
        raise ValueError("开始日期不能晚于结束日期")
    return start, end


def appointment_status(params):
    status = params.get("status", "")
    if status and status not in APPOINTMENT_STATUSES:
        raise ValueError(f"未知预约状态：{status}")
    return status


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
