#!/usr/bin/env python3
"""Create a review-only least-privilege plan for running an untrusted repository.

Additive extension: --generate-script writes a runnable shell (.sh) or batch
(.bat) script that implements the isolation plan with safety checks.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = '0.1.0'


def _escape_shell(value):
    return value.replace("'", "'\\''")


def _generate_venv_script(repo, run_dir, command, network, mounts):
    mounts_lines = []
    for m in mounts:
        if sys.platform == 'win32':
            host = m['host'].replace('/', '\\')
            mounts_lines.append(f'if not exist "{host}" (echo "error: mount missing: {host}" 1>&2 & exit 1)')
        else:
            mounts_lines.append(f'test -e \'{_escape_shell(m["host"])}\' || {{ echo "error: mount missing: {m["host"]}" 1>&2; exit 1; }}')
    mounts_text = '\n'.join(mounts_lines)
    network_warn = ''
    if network == 'allow':
        network_warn = ('\necho "warning: network is enabled; review the command before running" 1>&2')
    if sys.platform == 'win32':
        return (
            f'@echo off\n'
            f'setlocal enabledelayedexpansion\n'
            f'set REPO={repo}\n'
            f'set RUN={run_dir}\n'
            f'if "%REPO%"=="%RUN%" (echo error: run-dir must not equal repo 1>&2 & exit /b 1)\n'
            f'if exist "%RUN%" (echo error: run-dir already exists: %RUN% 1>&2 & exit /b 1)\n'
            f'mkdir "%RUN%"\n'
            f'set HOME=%RUN%\\home\n'
            f'set TMPDIR=%RUN%\\tmp\n'
            f'mkdir "%HOME%"\n'
            f'mkdir "%TMPDIR%"\n'
            f'{mounts_text}\n'
            f'python -m venv "%RUN%\\venv"\n'
            f'call "%RUN%\\venv\\Scripts\\activate.bat"\n'
            f'{command}\n'
        )
    return (
        f'#!/usr/bin/env sh\n'
        f'set -eu\n'
        f'REPO=\'{_escape_shell(str(repo))}\'\n'
        f'RUN=\'{_escape_shell(str(run_dir))}\'\n'
        f'case "$RUN" in\n'
        f'  "$REPO"|"$REPO"/*) echo "error: run-dir must not equal or be under repo" 1>&2; exit 1;;\n'
        f'esac\n'
        f'{mounts_text}\n'
        f'mkdir -p "$RUN"\n'
        f'export HOME="$RUN/home"\n'
        f'export TMPDIR="$RUN/tmp"\n'
        f'mkdir -p "$HOME" "$TMPDIR"\n'
        f'python3 -m venv "$RUN/venv"\n'
        f'. "$RUN/venv/bin/activate"\n'
        f'{network_warn}\n'
        f'{_escape_shell(command)}\n'
    )


def _generate_docker_script(repo, run_dir, command, network, mounts):
    vols_list = []
    for m in mounts:
        vols_list.append('-v "{}:{}:{}"'.format(m['host'], m['container'], m['mode'][:2]))
    vols = ' '.join(vols_list)
    net = 'none' if network == 'none' else 'bridge'
    if sys.platform == 'win32':
        escaped_cmd = command.replace('"', '\\"')
        return (
            '@echo off\n'
            'docker run --rm --network ' + net + ' ' + vols + ' -w /workspace/run <image> sh -lc "' + escaped_cmd + '"\n'
        )
    return (
        '#!/usr/bin/env sh\n'
        'set -eu\n'
        'docker run --rm --network ' + net + ' ' + vols + ' -w /workspace/run <image> sh -lc \'' + _escape_shell(command) + '\'\n'
    )


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repo')
    p.add_argument('--command', required=True, help='proposed command; this script never executes it')
    p.add_argument('--run-dir', required=True)
    p.add_argument('--network', choices=['none', 'allow'], default='none')
    p.add_argument('--data', action='append', default=[])
    p.add_argument('--out')
    p.add_argument('--force', action='store_true')
    p.add_argument('--generate-script', help='write runnable script to PATH (.sh or .bat by extension)')
    p.add_argument('--backend', choices=['venv', 'docker'], default='venv', help='isolation backend for --generate-script')
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    a = p.parse_args(argv)
    try:
        repo = Path(a.repo).resolve(strict=True)
        run = Path(a.run_dir).resolve()
        if repo == run or repo in run.parents:
            raise ValueError('--run-dir must not be the repository or its parent')
        data = [str(Path(x).resolve(strict=True)) for x in a.data]
        mounts = (
            [{'host': str(repo), 'container': '/workspace/repo', 'mode': 'read-only'},
             {'host': str(run), 'container': '/workspace/run', 'mode': 'read-write'}] +
            [{'host': x, 'container': f'/workspace/data/{i}', 'mode': 'read-only'} for i, x in enumerate(data)]
        )
        plan = {
            'schema_version': '1.0.0', 'artifact_type': 'isolation-plan',
            'created_at': datetime.now(timezone.utc).isoformat(), 'tool_version': VERSION,
            'status': 'review-required', 'repository': str(repo), 'run_dir': str(run),
            'command': a.command, 'network': a.network, 'mounts': mounts,
            'prohibitions': [
                'Do not mount host home directories, credential stores, SSH keys, or cloud configuration.',
                'Do not execute this plan until the user confirms environment and command.',
                'Do not write into the repository; keep patches under run_dir/patches/.',
            ],
            'suggested_docker_command': 'docker run --rm --network ' + ('none' if a.network == 'none' else 'bridge') +
                ' -v "<repo>:/workspace/repo:ro" -v "<run-dir>:/workspace/run" <image> sh -lc "' + a.command.replace('"', '\\"') + '"',
        }
        if a.generate_script:
            script_path = Path(a.generate_script).resolve()
            if script_path.exists() and not a.force:
                raise ValueError('script output exists; use --force to overwrite')
            if a.backend == 'docker':
                script = _generate_docker_script(repo, run, a.command, a.network, mounts)
            else:
                script = _generate_venv_script(repo, run, a.command, a.network, mounts)
            script_path.write_text(script, encoding='utf-8')
            plan['generated_script'] = str(script_path)
            plan['backend'] = a.backend
        payload = json.dumps(plan, ensure_ascii=False, indent=2)
        if a.out:
            out = Path(a.out).resolve()
            if out.exists() and not a.force:
                raise ValueError('output exists; use --force only for a derived plan')
            out.write_text(payload + '\n', encoding='utf-8')
        print(payload)
        return 0
    except (OSError, ValueError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
