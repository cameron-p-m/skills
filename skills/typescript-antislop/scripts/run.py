#!/usr/bin/env python3
"""Run pinned anti-slop rules against an explicit Git file selection."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

COMMIT = '13909c9e07590f5a85d93c62712259fe14a883f7'
VERSION = '1.78.0'
SOURCE = 'https://github.com/dmmulroy/anti-slop.git'
EXTENSIONS = {'.ts', '.tsx', '.mts', '.cts'}
RULES = [
    'no-array-filter-map', 'no-reduce-accumulator-copy',
    'no-chained-type-assertions', 'no-conditional-empty-object-spread',
    'no-known-value-widening', 'no-module-mocking', 'no-object-parameters',
    'no-reflect-apply', 'no-reflect-get', 'no-runtime-typeof',
    'no-shape-in-symbol-names', 'no-unknown-parameters', 'no-unknown-returns',
    'no-unknown-type-aliases', 'no-unsafe-dictionary-type', 'no-widen-then-assert',
    'require-readable-spacing', 'require-safety-comment-for-type-assertion',
]
EFFECT_RULES = [
    'no-manual-effect-error-tag', 'no-manual-tag-comparison',
    'no-manual-tagged-construction', 'no-service-constructor-imports',
    'prefer-effect-match',
]


def command(args, cwd, capture=False):
    return subprocess.run(args, cwd=cwd, check=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def git_files(repo, args):
    return [os.fsdecode(p) for p in command(['git', *args], repo, True).split(b'\0') if p]


def select_files(args, repo):
    if args.mode == 'changed':
        # HEAD compares both staged and unstaged changes. Unborn branches use the index.
        head = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=repo,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        names = git_files(repo, ['diff', '--name-only', '--diff-filter=ACMR', '-z', 'HEAD', '--']) if head.returncode == 0 else git_files(repo, ['ls-files', '-z'])
        names += git_files(repo, ['ls-files', '--others', '--exclude-standard', '-z'])
    elif args.mode == 'pr':
        if not args.base:
            raise ValueError('pr requires --base with the actual PR base ref')
        # Resolve the ref first: no shell interpolation or option-like revision input.
        base = command(['git', 'rev-parse', '--verify', '--end-of-options', args.base + '^{commit}'], repo, True).decode().strip()
        names = git_files(repo, ['diff', '--name-only', '--diff-filter=ACMR', '-z', base + '...HEAD', '--'])
    else:
        names = args.paths
        if not names:
            raise ValueError('files requires at least one file path relative to --repo')
    selected = []
    for name in names:
        path = (repo / name).resolve()
        if not path.is_relative_to(repo):
            raise ValueError(f'File is outside the repository: {name}')
        if not path.is_file():
            if args.mode == 'files':
                raise ValueError(f'Not an existing regular file: {name}')
            continue
        if path.suffix in EXTENSIONS:
            selected.append(str(path))
    return sorted(set(selected))


def setup(cache):
    marker = cache / 'ready.json'
    expected = {'commit': COMMIT, 'oxlint': VERSION}
    binary = cache / 'node_modules/oxlint/bin/oxlint'
    if marker.exists() and json.loads(marker.read_text()) == expected and binary.exists():
        return binary
    cache.mkdir(parents=True, exist_ok=True)
    upstream = cache / 'upstream'
    if not upstream.exists():
        command(['git', 'init', str(upstream)], cache)
    command(['git', 'fetch', '--depth=1', SOURCE, COMMIT], upstream)
    command(['git', 'checkout', '--detach', COMMIT], upstream)
    (cache / 'package.json').write_text(json.dumps({
        'private': True, 'type': 'module',
        'dependencies': {'oxlint': VERSION, '@oxlint/plugins': VERSION},
    }, indent=2) + '\n')
    command(['npm', 'install', '--no-audit', '--no-fund'], cache)
    command(['node', str(binary), '--version'], cache)
    marker.write_text(json.dumps(expected) + '\n')
    return binary


def config(cache, effect):
    plugins = [{'name': 'anti-slop', 'specifier': str(cache / 'upstream/src/index.ts')}]
    rules = {'anti-slop/' + rule: 'error' for rule in RULES}
    rules['oxc/no-accumulating-spread'] = 'error'
    if effect:
        plugins.append({'name': 'anti-slop-effect', 'specifier': str(cache / 'upstream/src/effect/index.ts')})
        rules.update({'anti-slop-effect/' + rule: 'error' for rule in EFFECT_RULES})
    path = cache / ('effect.json' if effect else 'general.json')
    path.write_text(json.dumps({
        'categories': {'correctness': 'off'},
        'jsPlugins': plugins, 'rules': rules,
    }, indent=2) + '\n')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['setup', 'changed', 'pr', 'files'])
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--repo', default='.')
    parser.add_argument('--base')
    parser.add_argument('--cache', default=str(Path.home() / '.cache/typescript-antislop' / (COMMIT[:12] + '-' + VERSION)))
    parser.add_argument('--effect', action='store_true')
    args = parser.parse_intermixed_args()
    if args.paths and args.mode != 'files':
        parser.error('file paths are accepted only in files mode')
    if args.base and args.mode != 'pr':
        parser.error('--base is accepted only in pr mode')
    cache = Path(args.cache).expanduser().resolve()
    if args.mode == 'setup':
        setup(cache)
        return 0
    repo = Path(command(['git', 'rev-parse', '--show-toplevel'], Path(args.repo).resolve(), True).decode().strip()).resolve()
    files = select_files(args, repo)
    if not files:
        print('No existing TypeScript files selected; Oxlint was not run.')
        return 0
    print(f'Checking {len(files)} file(s), using current working-tree contents:', flush=True)
    for path in files:
        print('  ' + os.path.relpath(path, repo), flush=True)
    binary = setup(cache)
    settings = config(cache, args.effect)
    # Bound argv size; never invoke Oxlint with an empty path list.
    status = 0
    for offset in range(0, len(files), 50):
        result = subprocess.run(['node', str(binary), '--config', str(settings),
                                 '--disable-nested-config', '--deny-warnings', '--',
                                 *files[offset:offset + 50]], cwd=repo)
        status = max(status, result.returncode if result.returncode >= 0 else 1)
    return status


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'anti-slop: {error}', file=sys.stderr)
        sys.exit(2)
