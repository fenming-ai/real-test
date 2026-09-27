import csv
import io
import unittest

from app import dispatch
from services import export_appointments, list_appointments


NORTH = {"tenant_id": "north", "role": "organizer"}
VIEWER = {"tenant_id": "north", "role": "viewer"}


class AppointmentFilters(unittest.TestCase):
    def test_date_and_status_filter_list_and_paging(self):
        params = {"start": "2026-09-21", "end": "2026-09-27",
                  "status": "confirmed"}
        first = list_appointments(NORTH, params)
        second = list_appointments(NORTH, {**params, "page": "2"})
        self.assertEqual(first["total"], 14)
        self.assertEqual(len(first["items"]), 10)
        self.assertEqual(len(second["items"]), 4)
        for row in first["items"] + second["items"]:
            self.assertEqual(row["status"], "confirmed")
            self.assertLessEqual("2026-09-21", row["starts_at"][:10])
            self.assertLessEqual(row["starts_at"][:10], "2026-09-27")

    def test_export_is_all_matches_with_fixed_safe_columns(self):
        text = export_appointments(NORTH, {
            "start": "2026-09-21", "end": "2026-09-27",
            "status": "confirmed", "page": "2", "tenant_id": "south"})
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), 14)
        self.assertEqual(list(rows[0]), ["id", "name", "email", "starts_at", "status"])
        self.assertTrue(any(row["name"] == '张, "小明"\n同学' for row in rows))
        self.assertNotIn("tenant_id", text)
        self.assertNotIn("private_note", text)
        self.assertTrue(all(int(row["id"]) < 1000 for row in rows))

    def test_empty_export_keeps_header(self):
        text = export_appointments(NORTH, {"status": "pending",
                                            "start": "2025-01-01",
                                            "end": "2025-01-01"})
        self.assertEqual(list(csv.reader(io.StringIO(text))), [
            ["id", "name", "email", "starts_at", "status"]])

    def test_utc_day_boundaries_are_inclusive(self):
        rows = list(csv.DictReader(io.StringIO(export_appointments(NORTH, {
            "start": "2026-09-27", "end": "2026-09-27",
            "status": "confirmed"}))))
        ids = {row["id"] for row in rows}
        self.assertIn("102", ids)  # 23:59:59 on the end date
        self.assertNotIn("103", ids)  # 23:59:59 on the previous date
        self.assertNotIn("104", ids)  # 00:00:00 on the following date

    def test_invalid_filters(self):
        invalid = [
            {"start": "2026-09-21"},
            {"end": "2026-09-27"},
            {"start": "bad", "end": "2026-09-27"},
            {"start": "2026-09-28", "end": "2026-09-27"},
            {"status": "unknown"},
        ]
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                list_appointments(NORTH, params)
            with self.subTest(params=params), self.assertRaises(ValueError):
                export_appointments(NORTH, params)

    def test_permissions_and_route(self):
        for function in (list_appointments, export_appointments):
            with self.assertRaises(PermissionError):
                function(VIEWER, {})
        kind, text = dispatch("/api/appointments/export", {}, NORTH)
        self.assertEqual(kind, "text/csv")
        self.assertEqual(len(list(csv.DictReader(io.StringIO(text)))), 52)


if __name__ == "__main__":
    unittest.main()
