import csv
import io
import unittest

from app import dispatch
from services import export_appointments, list_appointments


NORTH = {"tenant_id": "north", "role": "organizer"}
SOUTH = {"tenant_id": "south", "role": "organizer"}


class AppointmentFilters(unittest.TestCase):
    def test_date_range_is_inclusive_and_uses_utc_dates(self):
        result = list_appointments(NORTH, {
            "start": "2026-09-21", "end": "2026-09-27",
        })
        self.assertEqual(result["total"], 30)

        exported = list(csv.DictReader(io.StringIO(export_appointments(NORTH, {
            "start": "2026-09-21", "end": "2026-09-27",
        }))))
        self.assertEqual(len(exported), 30)
        exported_ids = {int(row["id"]) for row in exported}
        self.assertIn(101, exported_ids)
        self.assertIn(102, exported_ids)
        self.assertNotIn(103, exported_ids)
        self.assertNotIn(104, exported_ids)

    def test_status_combines_with_date_range_and_paginates(self):
        params = {
            "start": "2026-09-21", "end": "2026-09-27",
            "status": "confirmed",
        }
        first = list_appointments(NORTH, params)
        second = list_appointments(NORTH, {**params, "page": "2"})
        self.assertEqual(first["total"], 14)
        self.assertEqual(len(first["items"]), 10)
        self.assertEqual(len(second["items"]), 4)
        self.assertTrue(all(row["status"] == "confirmed"
                            for row in first["items"] + second["items"]))

    def test_empty_filters_mean_all_records(self):
        self.assertEqual(list_appointments(NORTH, {
            "start": "", "end": "", "status": "",
        })["total"], 52)

    def test_invalid_filters_are_rejected(self):
        invalid = (
            {"start": "2026-09-21", "end": ""},
            {"start": "", "end": "2026-09-27"},
            {"start": "2026-02-30", "end": "2026-09-27"},
            {"start": "2026-09-28", "end": "2026-09-27"},
            {"status": "unknown"},
        )
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                list_appointments(NORTH, params)
            with self.subTest(params=params), self.assertRaises(ValueError):
                export_appointments(NORTH, params)

    def test_export_has_fixed_columns_all_rows_and_correct_csv_escaping(self):
        text = export_appointments(NORTH, {
            "start": "2026-09-21", "end": "2026-09-21",
            "status": "confirmed", "page": "999", "tenant_id": "south",
        })
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), 5)
        escaped = next(row for row in rows if row["id"] == "101")
        self.assertEqual(escaped["name"], '张, "小明"\n同学')
        self.assertEqual(escaped["email"], 'x,"y"\n@example.test')
        self.assertEqual(list(escaped), ["id", "name", "email", "starts_at", "status"])
        self.assertNotIn("tenant_id", text)
        self.assertNotIn("private_note", text)
        self.assertNotIn("INTERNAL_DO_NOT_EXPORT", text)

    def test_empty_export_keeps_header(self):
        text = export_appointments(SOUTH, {
            "start": "2025-01-01", "end": "2025-01-01",
        })
        self.assertEqual(text, "id,name,email,starts_at,status\r\n")

    def test_client_tenant_parameter_cannot_cross_tenant(self):
        listed = list_appointments(NORTH, {"tenant_id": "south"})
        self.assertEqual(listed["total"], 52)
        self.assertTrue(all(row["id"] < 1000 for row in listed["items"]))

        text = export_appointments(NORTH, {"tenant_id": "south"})
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), 52)
        self.assertTrue(all(int(row["id"]) < 1000 for row in rows))

    def test_api_routes_use_the_same_filters(self):
        params = {
            "start": "2026-09-21", "end": "2026-09-27",
            "status": "cancelled", "page": "2",
        }
        list_kind, list_text = dispatch("/api/appointments", params, NORTH)
        export_kind, export_text = dispatch("/api/appointments/export", params, NORTH)
        self.assertEqual(list_kind, "application/json")
        self.assertEqual(export_kind, "text/csv")
        self.assertIn('"total": 8', list_text)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(export_text)))), 8)


if __name__ == "__main__":
    unittest.main()
