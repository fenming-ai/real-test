from datetime import date, timedelta

TODAY = date(2026, 9, 27)
APPOINTMENTS = []
for tenant in ("north", "south"):
    for index in range(1, 49):
        day = TODAY - timedelta(days=(index - 1) % 12)
        APPOINTMENTS.append({
            "id": (0 if tenant == "north" else 1000) + index,
            "tenant_id": tenant,
            "name": f"{'北' if tenant == 'north' else '南'}区客户 {index}",
            "email": f"{tenant}{index}@example.test",
            "starts_at": day.isoformat() + "T12:00:00Z",
            "status": ("confirmed", "pending", "cancelled")[(index - 1) % 3],
            "private_note": "INTERNAL_DO_NOT_EXPORT",
        })
APPOINTMENTS.extend([
    {"id": 101, "tenant_id": "north", "name": '张, "小明"\n同学',
     "email": 'x,"y"\n@example.test', "starts_at": "2026-09-21T00:00:00Z",
     "status": "confirmed", "private_note": "INTERNAL_DO_NOT_EXPORT"},
    {"id": 102, "tenant_id": "north", "name": "最后一秒",
     "email": "end@example.test", "starts_at": "2026-09-27T23:59:59Z",
     "status": "confirmed", "private_note": "INTERNAL_DO_NOT_EXPORT"},
    {"id": 103, "tenant_id": "north", "name": "前一天",
     "email": "before@example.test", "starts_at": "2026-09-20T23:59:59Z",
     "status": "confirmed", "private_note": "INTERNAL_DO_NOT_EXPORT"},
    {"id": 104, "tenant_id": "north", "name": "后一天",
     "email": "after@example.test", "starts_at": "2026-09-28T00:00:00Z",
     "status": "confirmed", "private_note": "INTERNAL_DO_NOT_EXPORT"},
])
INVOICES = [
    {"tenant_id": tenant, "number": f"{tenant}-01", "customer": "演示客户",
     "amount": "120.00", "issued_at": "2026-09-22T12:00:00Z"}
    for tenant in ("north", "south")
]
