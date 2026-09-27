"""Frozen external acceptance; not provided to coding agents."""
import csv
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv.pop(1)).resolve()))
from app import dispatch
from data import APPOINTMENTS

NORTH = {"tenant_id": "north", "role": "organizer"}
SOUTH = {"tenant_id": "south", "role": "organizer"}
FIELDS = ['id', 'name', 'email', 'starts_at', 'status']


def listing(params=None, actor=NORTH):
    kind, body = dispatch('/api/appointments', params or {}, actor)
    assert kind == 'application/json'
    return json.loads(body)


def exported(params=None, actor=NORTH):
    kind, body = dispatch('/api/appointments/export', params or {}, actor)
    assert kind.startswith('text/csv')
    return list(csv.reader(io.StringIO(body, newline='')))


def expected(params, tenant='north'):
    return sorted([r for r in APPOINTMENTS if r['tenant_id'] == tenant
        and (not params.get('start') or params['start'] <= r['starts_at'][:10] <= params['end'])
        and (not params.get('status') or r['status'] == params['status'])], key=lambda r: r['id'])


class Acceptance(unittest.TestCase):
    def test_filtered_paging(self):
        params = {'start': '2026-09-21', 'end': '2026-09-27', 'status': 'confirmed'}
        rows = expected(params)
        self.assertGreater(len(rows), 10)
        for page in (1, 2, 3):
            data = listing({**params, 'page': str(page)})
            self.assertEqual(data['total'], len(rows))
            self.assertEqual([r['id'] for r in data['items']], [r['id'] for r in rows[(page-1)*10:page*10]])
            self.assertEqual(data['page'], page)

    def test_export_all_not_current_page(self):
        for params in ({}, {'page': '2'}, {'start': '2026-09-21', 'end': '2026-09-27'},
                       {'status': 'pending'}, {'start': '2026-09-21', 'end': '2026-09-27', 'status': 'confirmed', 'page': '2'}):
            with self.subTest(params=params):
                rows = expected(params)
                self.assertEqual(exported(params), [FIELDS]+[[str(r[k]) for k in FIELDS] for r in rows])

    def test_inclusive_midnight_and_last_second(self):
        params = {'start': '2026-09-21', 'end': '2026-09-27'}
        ids = {int(r[0]) for r in exported(params)[1:]}
        self.assertTrue({101, 102} <= ids)
        self.assertFalse({103, 104} & ids)

    def test_special_characters(self):
        row = next(r for r in exported()[1:] if r[0] == '101')
        self.assertEqual(row[1], '张, "小明"\n同学')
        self.assertEqual(row[2], 'x,"y"\n@example.test')

    def test_empty_header_and_empty_list(self):
        params = {'start': '2020-01-01', 'end': '2020-01-02'}
        self.assertEqual(exported(params), [FIELDS])
        self.assertEqual(listing(params)['items'], [])
        self.assertEqual(listing(params)['total'], 0)

    def test_invalid_filter_rejected(self):
        cases = [{'start': '2026-09-21'}, {'end': '2026-09-27'},
                 {'start': '2026-09-27', 'end': '2026-09-21'},
                 {'start': '2026-02-30', 'end': '2026-03-01'},
                 {'start': 'not-a-date', 'end': 'not-a-date'}, {'status': 'unknown'}]
        for params in cases:
            for fn in (listing, exported):
                with self.subTest(params=params, function=fn.__name__), self.assertRaises(ValueError):
                    fn(params)

    def test_empty_filters(self):
        params = {'start': '', 'end': '', 'status': ''}
        self.assertEqual(listing(params)['total'], 52)
        self.assertEqual(len(exported(params)), 53)

    def test_tenant_spoof_and_private_columns(self):
        params = {'tenant_id': 'south'}
        rows = exported(params)
        self.assertEqual(rows[0], FIELDS)
        self.assertEqual(len(rows), 53)
        self.assertFalse(any(int(row[0]) >= 1000 for row in rows[1:]))
        self.assertNotIn('INTERNAL_DO_NOT_EXPORT', str(rows))
        self.assertEqual(len(exported({'tenant_id': 'north'}, SOUTH)), 49)
        for row in listing(params)['items']:
            self.assertEqual(set(row), set(FIELDS))

    def test_viewer_denied(self):
        for fn in (listing, exported):
            for params in ({}, {'start': '2020-01-01', 'end': '2020-01-02'}):
                with self.subTest(function=fn.__name__), self.assertRaises(PermissionError):
                    fn(params, {'tenant_id': 'north', 'role': 'viewer'})

    def test_no_mutation(self):
        before = json.dumps(APPOINTMENTS, sort_keys=True)
        listing({'status': 'pending'})
        exported({'status': 'pending'})
        self.assertEqual(json.dumps(APPOINTMENTS, sort_keys=True), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
