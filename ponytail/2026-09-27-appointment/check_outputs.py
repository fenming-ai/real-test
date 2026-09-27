"""Independent checks of completed skill-up artifacts; never edits submissions."""
import csv
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SEED = ROOT / 'seed'
OUT = ROOT / 'rechecks'


def run_check(command, cwd, env=None):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=60)
    return {'command': command, 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


HTTP_CHECK = '''
import csv, io, json, threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from app import Handler
server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
def fetch(path, token='north-organizer'):
    req = Request(base + path, headers={'Authorization': 'Bearer ' + token} if token else {})
    try:
        with urlopen(req, timeout=5) as r: return r.status, dict(r.headers), r.read().decode()
    except HTTPError as e: return e.code, dict(e.headers), e.read().decode()
checks = []
try:
    for path in ['/', '/appointments.js', '/date-range.js', '/api.js', '/invoices.html', '/invoices.js']:
        assert fetch(path)[0] == 200, path
    checks.append('HTTP static assets served (not browser execution)')
    status, headers, body = fetch('/api/appointments/export?page=2&status=confirmed&start=2026-09-21&end=2026-09-27')
    assert status == 200 and 'attachment' in headers['Content-Disposition']
    rows = list(csv.reader(io.StringIO(body)))
    assert len(rows) > 11 and all(r[4] == 'confirmed' for r in rows[1:])
    checks.append('CSV attachment exports all matching rows, not page 2')
    for path in ['/api/appointments?status=bad', '/api/appointments/export?start=2026-09-21']:
        status, _, body = fetch(path)
        assert status == 400 and json.loads(body)['error']
    checks.append('Invalid query returns HTTP 400 and message')
    for token in ['', 'bad-token', 'north-viewer']:
        for path in ['/api/appointments', '/api/appointments/export']:
            assert fetch(path, token)[0] == 403
    checks.append('Missing/invalid/viewer authentication returns HTTP 403')
    status, _, body = fetch('/api/appointments?tenant_id=north', 'south-organizer')
    data = json.loads(body)
    assert status == 200 and data['total'] == 48 and data['items'][0]['id'] == 1001
    checks.append('HTTP tenant spoof ignored')
    status, _, body = fetch('/api/invoices/export?start=2026-09-21&end=2026-09-27')
    assert status == 200 and len(list(csv.reader(io.StringIO(body)))) == 2
    checks.append('Existing invoice export HTTP regression')
    print(json.dumps({'passed': checks}, ensure_ascii=False))
finally:
    server.shutdown()
    server.server_close()
'''


def check(app):
    parts = app.relative_to(ROOT / 'run-01/outputs/iteration-1').parts
    label = parts[0] + '-' + parts[1]
    dest = OUT / label
    dest.mkdir(parents=True, exist_ok=True)
    source_files = [p for p in app.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    hashes = {str(p.relative_to(app)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    previous = dest / 'results.json'
    if previous.exists() and json.loads(previous.read_text()).get('source_sha256') == hashes:
        print(label + ': unchanged; reusing checks')
        return
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(app)}
    checks = {
        'external_acceptance': run_check([sys.executable, str(ROOT / 'acceptance.py'), str(app)], ROOT, env),
        'frozen_regression': run_check([sys.executable, '-m', 'unittest', 'discover', '-s', str(SEED / 'tests'), '-v'], ROOT, env),
        'http': run_check([sys.executable, '-c', HTTP_CHECK], app, env),
    }
    changes, diff = [], []
    paths = set(hashes) | {str(p.relative_to(SEED)) for p in SEED.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for relative in sorted(paths):
        before, after = SEED / relative, app / relative
        a = before.read_text().splitlines(keepends=True) if before.exists() else []
        b = after.read_text().splitlines(keepends=True) if after.exists() else []
        if a == b:
            continue
        patch = list(difflib.unified_diff(a, b, fromfile='seed/' + relative, tofile='result/' + relative))
        added = sum(line.startswith('+') and not line.startswith('+++') for line in patch)
        removed = sum(line.startswith('-') and not line.startswith('---') for line in patch)
        changes.append({'path': relative, 'added': added, 'removed': removed,
                        'kind': 'test' if relative.startswith('tests/') else 'production'})
        diff.extend(patch)
    (dest / 'changes.diff').write_text(''.join(diff))
    result = {'artifact': str(app), 'source_sha256': hashes, 'checks': checks, 'changes': changes,
              'api_checks_passed': all(c['exit_code'] == 0 for c in checks.values()),
              'browser': {'status': 'pending', 'reason': 'Chrome remote debugging permission pending; HTTP is not UI proof'}}
    previous.write_text(json.dumps(result, ensure_ascii=False, indent=2).replace(str(ROOT), '.').replace(sys.executable, 'python3') + '\n')
    print(label + ': ' + ('API/regression PASS' if result['api_checks_passed'] else 'FAIL'))


if __name__ == '__main__':
    for app in sorted((ROOT / 'run-01/outputs/iteration-1').glob('appointment-*/*/outputs/workspace/result/app')):
        check(app)
