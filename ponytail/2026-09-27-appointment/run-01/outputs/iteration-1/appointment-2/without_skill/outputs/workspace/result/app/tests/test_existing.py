import csv
import io
import json
import unittest
from app import dispatch
from services import export_appointments, export_invoices, list_appointments

NORTH = {"tenant_id": "north", "role": "organizer"}


class Existing(unittest.TestCase):
    def test_list_paging(self):
        one = list_appointments(NORTH, {})
        two = list_appointments(NORTH, {"page": "2"})
        self.assertEqual(one['total'], 52)
        self.assertEqual(len(one['items']), 10)
        self.assertEqual(one['items'][0]['id'], 1)
        self.assertEqual(two['items'][0]['id'], 11)
        self.assertNotIn('private_note', one['items'][0])

    def test_tenant(self):
        result = list_appointments({"tenant_id": "south", "role": "organizer"}, {})
        self.assertEqual(result['total'], 48)
        self.assertEqual(result['items'][0]['id'], 1001)

    def test_permissions(self):
        for function in (list_appointments, export_appointments, export_invoices):
            with self.assertRaises(PermissionError):
                function({"tenant_id": "north", "role": "viewer"}, {})

    def test_invoice(self):
        text = export_invoices(NORTH, {"start": "2026-09-21", "end": "2026-09-27"})
        self.assertEqual(list(csv.reader(io.StringIO(text))), [
            ['number', 'customer', 'amount'], ['north-01', '演示客户', '120.00']])

    def test_invalid_dates(self):
        for params in ({"start": "2026-09-21"}, {"start": "bad", "end": "bad"},
                       {"start": "2026-09-27", "end": "2026-09-21"}):
            with self.assertRaises(ValueError):
                export_invoices(NORTH, params)

    def test_appointment_filters_apply_before_paging(self):
        params = {"start": "2026-09-21", "end": "2026-09-27", "status": "confirmed"}
        result = list_appointments(NORTH, params)
        self.assertEqual(result["total"], 14)
        self.assertEqual(len(result["items"]), 10)
        self.assertTrue(all(row["status"] == "confirmed" for row in result["items"]))
        self.assertTrue(all("2026-09-21" <= row["starts_at"][:10] <= "2026-09-27"
                            for row in result["items"]))
        second = list_appointments(NORTH, {**params, "page": "2"})
        self.assertEqual(len(second["items"]), 4)

    def test_appointment_date_boundaries_and_all_dates(self):
        result = list_appointments(NORTH, {"start": "2026-09-21", "end": "2026-09-27"})
        ids = {row["id"] for page in range(1, 7)
               for row in list_appointments(NORTH, {
                   "start": "2026-09-21", "end": "2026-09-27", "page": str(page)
               })["items"]}
        self.assertEqual(result["total"], 30)
        self.assertIn(101, ids)
        self.assertIn(102, ids)
        self.assertNotIn(103, ids)
        self.assertNotIn(104, ids)
        self.assertEqual(list_appointments(NORTH, {"start": "", "end": ""})["total"], 52)

    def test_appointment_invalid_filters(self):
        invalid = (
            {"start": "2026-09-21"},
            {"start": "bad", "end": "bad"},
            {"start": "2026-09-27", "end": "2026-09-21"},
            {"status": "unknown"},
        )
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                list_appointments(NORTH, params)
            with self.subTest(params=params), self.assertRaises(ValueError):
                export_appointments(NORTH, params)

    def test_appointment_export_all_matches_and_csv_escaping(self):
        params = {"start": "2026-09-21", "end": "2026-09-27", "status": "confirmed",
                  "page": "2", "tenant_id": "south"}
        rows = list(csv.reader(io.StringIO(export_appointments(NORTH, params))))
        self.assertEqual(rows[0], ["id", "name", "email", "starts_at", "status"])
        self.assertEqual(len(rows) - 1, 14)
        self.assertIn(["101", '张, "小明"\n同学', 'x,"y"\n@example.test',
                       "2026-09-21T00:00:00Z", "confirmed"], rows)
        flattened = "\n".join(",".join(row) for row in rows)
        self.assertNotIn("tenant_id", flattened)
        self.assertNotIn("private_note", flattened)
        self.assertFalse(any(int(row[0]) >= 1000 for row in rows[1:]))

    def test_appointment_export_empty_keeps_header(self):
        text = export_appointments(NORTH, {
            "start": "2026-01-01", "end": "2026-01-01", "status": "cancelled"
        })
        self.assertEqual(list(csv.reader(io.StringIO(text))), [
            ["id", "name", "email", "starts_at", "status"]])

    def test_appointment_routes(self):
        kind, payload = dispatch("/api/appointments", {
            "start": "2026-09-27", "end": "2026-09-27", "status": "confirmed"
        }, NORTH)
        self.assertEqual(kind, "application/json")
        self.assertEqual(json.loads(payload)["total"], 5)
        kind, payload = dispatch("/api/appointments/export", {
            "start": "2026-09-27", "end": "2026-09-27", "status": "confirmed"
        }, NORTH)
        self.assertEqual(kind, "text/csv")
        self.assertEqual(len(list(csv.reader(io.StringIO(payload)))), 6)
