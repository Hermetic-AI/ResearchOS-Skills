#!/usr/bin/env python3
"""Read-only Git, submodule, remote, tag, and Git-LFS evidence for reproduction.

Additive extensions:
  --lfs-fetch-check   dry-run `git lfs fetch --all` and report missing files.
  --submodule-check   report submodule SHAs vs expected and init/clean state.
  --tag <tag>         check alignment with a specific release tag (not just
                      exact-match at HEAD).
All Git operations are read-only; lfs-fetch-check uses --dry-run.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

VERSION = '0.1.0'


def run(repo, *args):
    r = subprocess.run(
        ['git', '-C', str(repo), *args],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def parse_submodule_status(lines):
    """Parse `git submodule status --recursive` output into records.

    Format: [+- ]<sha> <path> (<describe>). Leading '-' = not initialized,
    '+' = initialized but SHA differs from expected, ' ' = clean.
    """
    records = []
    for raw in lines:
        if not raw:
            continue
        flag = raw[0]
        rest = raw[1:]
        parts = rest.split()
        if len(parts) < 2:
            continue
        sha, path = parts[0], parts[1]
        describe = ''
        if len(parts) >= 3:
            describe = ' '.join(parts[2:]).strip('()')
        records.append({
            'sha': sha, 'path': path, 'describe': describe,
            'initialized': flag != '-',
            'clean': flag == ' ',
        })
    return records


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repo')
    p.add_argument('--expected-commit', help='paper/release commit to compare (full hash or prefix)')
    p.add_argument('--lfs-fetch-check', action='store_true',
                   help='dry-run git lfs fetch --all and report missing files')
    p.add_argument('--submodule-check', action='store_true',
                   help='report submodule SHAs, init state, and clean/dirty status')
    p.add_argument('--tag', help='release tag to check alignment against (not just exact-match at HEAD)')
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    a = p.parse_args(argv)
    try:
        repo = Path(a.repo).resolve(strict=True)
        code, head, error = run(repo, 'rev-parse', 'HEAD')
        if code:
            raise ValueError(error or 'not a Git repository')
        _, tag, _ = run(repo, 'describe', '--tags', '--exact-match')
        _, remote, _ = run(repo, 'remote', 'get-url', 'origin')
        _, submodules_raw, _ = run(repo, 'submodule', 'status', '--recursive')
        _, lfs, _ = run(repo, 'lfs', 'ls-files')

        submodules = [x for x in submodules_raw.splitlines() if x]
        lfs_files = [x for x in lfs.splitlines() if x]

        payload = {
            'repository': str(repo), 'head': head,
            'expected_commit': a.expected_commit,
            'commit_match': None if not a.expected_commit else head.startswith(a.expected_commit),
            'exact_tag': tag or None, 'origin': remote or None,
            'submodules': submodules, 'lfs_files': lfs_files, 'warnings': [],
        }

        # --tag alignment: check if HEAD is an ancestor of (or equal to) the tag.
        tag_name = a.tag
        tag_aligned = None
        tag_target = None
        if tag_name:
            c, out, _ = run(repo, 'rev-parse', f'{tag_name}^{{commit}}')
            if c == 0 and out:
                tag_target = out
                c2, _, _ = run(repo, 'merge-base', '--is-ancestor', head, tag_name)
                tag_aligned = (c2 == 0) or (head == out)
            else:
                tag_aligned = False
            payload['tag'] = tag_name
            payload['tag_commit'] = tag_target
            payload['tag_aligned'] = tag_aligned

        # --submodule-check: detailed per-submodule state.
        submodule_details = None
        if a.submodule_check:
            submodule_details = parse_submodule_status(submodules)
            payload['submodule_details'] = submodule_details
            for rec in submodule_details:
                if not rec['initialized']:
                    payload['warnings'].append(
                        f"submodule not initialized: {rec['path']} ({rec['sha']})")
                elif not rec['clean']:
                    payload['warnings'].append(
                        f"submodule initialized but SHA differs from expected: {rec['path']}")

        # --lfs-fetch-check: dry-run fetch and parse missing files.
        lfs_missing = None
        if a.lfs_fetch_check:
            c, out, err = run(repo, 'lfs', 'fetch', '--all', '--dry-run')
            missing = []
            for line in (out.splitlines() + err.splitlines()):
                line = line.strip()
                if not line:
                    continue
                # Typical dry-run lines: "fetch <sha> <path>" or "(0 of N)".
                if line.startswith('fetch ') or line.startswith('Fetching') or line.startswith('* '):
                    missing.append(line)
                elif 'download' in line.lower() and ('missing' in line.lower() or 'need' in line.lower()):
                    missing.append(line)
            lfs_missing = missing
            payload['lfs_fetch_check'] = {
                'returncode': c, 'missing_reports': missing,
                'missing_count': len(missing),
            }
            if missing:
                payload['warnings'].append(
                    f"git lfs fetch dry-run reports {len(missing)} missing item(s); fetch before execution.")

        if a.expected_commit and not payload['commit_match']:
            payload['warnings'].append(
                'HEAD does not match the supplied paper/release commit; do not call this an exact reproduction.')
        if not payload['exact_tag']:
            payload['warnings'].append('HEAD is not exactly at a tag.')
        if tag_name and tag_aligned is False:
            payload['warnings'].append(
                f"HEAD is not aligned with tag {tag_name}; do not call this a tagged release reproduction.")
        if submodules and not a.submodule_check:
            payload['warnings'].append(
                'Submodules are present; record their SHAs and initialize only after review.')
        if lfs_files and not a.lfs_fetch_check:
            payload['warnings'].append(
                'Git LFS files are present; verify fetch status and data licensing before execution.')

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
