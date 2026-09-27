import csv
import io
import unittest
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
