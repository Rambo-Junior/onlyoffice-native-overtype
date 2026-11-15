#!/usr/bin/env python3
"""Qualify a NEW ONLYOFFICE Desktop Editors build and print a portable.PROFILES entry for it.

Usage: python3 tools/probe_profile.py 10.0.0-170        (the dpkg version of the installed package)

Clones the matching upstream tags, derives commit/blob pins, then runs the full verify (source patch anchors,
engine API canary, build, compiled-bundle patch, node syntax check). It proves only that the patch applies and the
build works; a GUI regression on the real editor is still required before trusting the profile.
Whether the official package also ships sdkjs-forms must be checked against the installed bundle
(e.g. `grep -c signRequest /opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all.js` > 0).
"""
from __future__ import annotations
import pprint
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tools'))
import portable
import verify_sdkjs_build as v


def remote_commit(url, tag):
    out = subprocess.check_output(['git','ls-remote','--tags',url,tag,tag+'^{}'], text=True).splitlines()
    refs = {l.split('\t')[1]: l.split('\t')[0] for l in out}
    return refs.get(f'refs/tags/{tag}^{{}}') or refs.get(f'refs/tags/{tag}')


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'\d+\.\d+\.\d+-\d+', sys.argv[1]):
        sys.exit(__doc__)
    version = sys.argv[1]
    tag = 'v' + version.replace('-', '.')
    commit = remote_commit(portable.GIT, tag)
    if not commit:
        sys.exit(f'Upstream tag {tag} not found in {portable.GIT}')
    with tempfile.TemporaryDirectory(prefix='overtype-probe-') as d:
        v.checkout(portable.GIT, tag, commit, Path(d)/'sdkjs')
        blob = portable.git_blob((Path(d)/'sdkjs/word/Editor/Document.js').read_bytes())
    short = ''.join(version.replace('-', '.').split('.'))
    product, build = version.split('-')
    forms = remote_commit(portable.FORMS_GIT, tag)
    profile = dict(
        tag=tag, commit=commit, doc_blob=blob, product_version=product, build_number=build,
        state=f'/var/lib/onlyoffice-overtype-native-portable-{short}',
        cache=f'.cache/onlyoffice-overtype-native-{short}',
        user_state=f'.local/state/onlyoffice-overtype-native-{short}',
        addons=(dict(name='sdkjs-forms', git=portable.FORMS_GIT, tag=tag, commit=forms),) if forms else (),
        validation=f'{version} profile: source patch, engine API and build verified; GUI regression on this version is NOT done yet.')
    v.verify(version, profile)
    print('\nAdd to portable.PROFILES (drop the sdkjs-forms addon if the official bundle does not contain OFORM):\n')
    print(f'    {version!r}: ' + pprint.pformat(profile, width=110, sort_dicts=False) + ',')


if __name__ == '__main__':
    main()
