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

    def test_appointment_filters_and_paging(self):
        params = {"start": "2026-09-21", "end": "2026-09-27", "status": "confirmed"}
        one = list_appointments(NORTH, params)
        two = list_appointments(NORTH, {**params, "page": "2", "tenant_id": "south"})
        self.assertEqual(one["total"], 14)
        self.assertEqual(len(one["items"]), 10)
        self.assertEqual(len(two["items"]), 4)
        self.assertTrue(all(row["status"] == "confirmed" for row in one["items"] + two["items"]))
        self.assertTrue(all("2026-09-21" <= row["starts_at"][:10] <= "2026-09-27"
                            for row in one["items"] + two["items"]))
        self.assertTrue(all(row["id"] < 1000 for row in one["items"] + two["items"]))

    def test_appointment_date_boundaries(self):
        result = list_appointments(NORTH, {"start": "2026-09-27", "end": "2026-09-27"})
        ids = {row["id"] for row in result["items"]}
        self.assertIn(1, ids)
        self.assertIn(102, ids)
        self.assertNotIn(104, ids)

    def test_appointment_export_all_matches_and_csv_escaping(self):
        text = export_appointments(NORTH, {
            "start": "2026-09-21", "end": "2026-09-27", "status": "confirmed"})
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(list(rows[0]), ['id', 'name', 'email', 'starts_at', 'status'])
        self.assertGreater(len(rows), 10)
        special = next(row for row in rows if row["id"] == "101")
        self.assertEqual(special["name"], '张, "小明"\n同学')
        self.assertEqual(special["email"], 'x,"y"\n@example.test')
        self.assertNotIn("tenant_id", text)
        self.assertNotIn("private_note", text)
        self.assertNotIn("INTERNAL_DO_NOT_EXPORT", text)

    def test_empty_appointment_export_keeps_header(self):
        text = export_appointments(NORTH, {
            "start": "2020-01-01", "end": "2020-01-01", "status": "pending"})
        self.assertEqual(list(csv.reader(io.StringIO(text))), [
            ['id', 'name', 'email', 'starts_at', 'status']])

    def test_appointment_api_routes_share_filters(self):
        params = {"start": "2026-09-21", "end": "2026-09-27", "status": "confirmed"}
        kind, listing = dispatch("/api/appointments", params, NORTH)
        export_kind, text = dispatch("/api/appointments/export", params, NORTH)
        self.assertEqual(kind, "application/json")
        self.assertEqual(export_kind, "text/csv")
        self.assertEqual(json.loads(listing)["total"], len(list(csv.DictReader(io.StringIO(text)))))

    def test_invalid_appointment_filters(self):
        invalid = ({"start": "2026-09-21"},
                   {"start": "bad", "end": "bad"},
                   {"start": "2026-09-27", "end": "2026-09-21"},
                   {"status": "unknown"})
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                list_appointments(NORTH, params)
            with self.subTest(export=params), self.assertRaises(ValueError):
                export_appointments(NORTH, params)
