#!/usr/bin/env python3
"""Generate a dataset download manifest with integrity and license tracking.

Input is a JSON specification: a list or {"datasets": [...]} of records, each
with url, expected_checksum (sha256), license, and version. The script never
downloads anything unless --export is used to write a runnable script.

Modes
  default            emit a JSON manifest with download/verify commands.
  --verify           check local files against expected checksums (sha256).
  --export <path>    write a shell script that performs downloads with
                     integrity checks (curl/wget), license/terms recording,
                     and version pinning.

Output is protected: existing files require --force.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = '0.1.0'
SHA256_RE = __import__('re').compile(r'^[0-9a-fA-F]{64}$')


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _pick_downloader():
    if shutil.which('curl'):
        return 'curl'
    if shutil.which('wget'):
        return 'wget'
    return None


def _download_cmd(url, dest, downloader):
    if downloader == 'curl':
        return f'curl -fsSL -o \'{dest}\' \'{url}\''
    if downloader == 'wget':
        return f'wget -O \'{dest}\' \'{url}\''
    return f'# no curl/wget found; download manually: {url} -> {dest}'


def _verify_cmd(dest, expected, downloader):
    return f'echo \'{expected}  {dest}\' | sha256sum -c - 2>/dev/null || echo "checksum FAILED: {dest}" 1>&2'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('spec', help='dataset specification JSON (list or {"datasets": [...]})')
    p.add_argument('--verify', action='store_true',
                   help='check local files (spec must include "path") against expected checksums')
    p.add_argument('--export', help='write a runnable download script to PATH')
    p.add_argument('--force', action='store_true')
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    a = p.parse_args(argv)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    try:
        spec_path = Path(a.spec).resolve(strict=True)
        raw = json.loads(spec_path.read_text(encoding='utf-8'))
        rows = raw.get('datasets') if isinstance(raw, dict) else raw
        if not isinstance(rows, list):
            raise ValueError('spec must be a list or object with a datasets list')

        datasets = []
        warnings = []
        for idx, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise ValueError(f'record {idx} is not an object')
            url = str(row.get('url', '')).strip()
            checksum = str(row.get('expected_checksum', '')).strip()
            license_ = str(row.get('license', '')).strip()
            version = str(row.get('version', '')).strip()
            path = str(row.get('path', '')).strip()
            if not url:
                raise ValueError(f'record {idx}: missing url')
            if checksum and not SHA256_RE.fullmatch(checksum):
                raise ValueError(f'record {idx}: expected_checksum must be 64 hex chars')
            datasets.append({
                'url': url, 'expected_checksum': checksum or None,
                'license': license_ or None, 'version': version or None,
                'path': path or None,
            })

        manifest = {
            'schema_version': '1.0.0',
            'artifact_type': 'dataset-download-manifest',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'tool_version': VERSION,
            'source_spec': str(spec_path),
            'datasets': datasets,
            'warnings': warnings,
        }

        # --verify mode: check local files against expected checksums.
        if a.verify:
            verify_results = []
            all_ok = True
            for ds in datasets:
                if not ds['path'] or not ds['expected_checksum']:
                    continue
                p = Path(ds['path'])
                if not p.is_file():
                    verify_results.append({
                        'path': str(p), 'status': 'missing',
                        'expected': ds['expected_checksum'], 'actual': None,
                    })
                    all_ok = False
                    continue
                actual = sha256_file(p)
                ok = actual == ds['expected_checksum']
                if not ok:
                    all_ok = False
                verify_results.append({
                    'path': str(p), 'status': 'ok' if ok else 'mismatch',
                    'expected': ds['expected_checksum'], 'actual': actual,
                })
            manifest['verify'] = {'results': verify_results, 'all_ok': all_ok}
            if not all_ok:
                warnings.append('one or more local files failed checksum verification')

        # --export mode: write a runnable shell script.
        if a.export:
            out = Path(a.export).resolve()
            if out.exists() and not a.force:
                raise ValueError('export exists; use --force to overwrite')
            downloader = _pick_downloader()
            lines = [
                '#!/usr/bin/env sh',
                '# Auto-generated dataset download manifest.',
                '# Review URLs, licenses, and checksums before running.',
                'set -eu',
                f'cd "$(dirname "$0")"',
                '',
            ]
            for i, ds in enumerate(datasets, 1):
                dest = ds['path'] or f'dataset-{i}'
                lines.append(f'# dataset {i}: version={ds["version"] or "n/a"} license={ds["license"] or "n/a"}')
                lines.append(_download_cmd(ds['url'], dest, downloader))
                if ds['expected_checksum']:
                    lines.append(_verify_cmd(dest, ds['expected_checksum'], downloader))
                lines.append('')
            out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            try:
                out.chmod(0o755)
            except (OSError, NotImplementedError):
                pass
            manifest['exported_script'] = str(out)
            manifest['downloader'] = downloader

        if not datasets:
            warnings.append('no dataset records in spec')

        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
