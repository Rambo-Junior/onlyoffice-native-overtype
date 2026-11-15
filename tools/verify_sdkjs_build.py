#!/usr/bin/env python3
"""Build the exact pinned upstream SDKJS and verify the source-only overtype patch, per version profile.

CI build, not a desktop GUI or document-integrity test. Never writes to /opt.
Usage: python3 tools/verify_sdkjs_build.py [--profile 9.4.0-129 --profile 10.0.0-169]   (default: all profiles)
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patches
import portable

LICENSE_BLOB = '53bc62cde3c705aa2d03b895b966bd6250f389ae'


def run(*args, cwd=None, env=None):
    print('$', ' '.join(map(str,args)), flush=True)
    subprocess.run([str(x) for x in args], cwd=cwd, env=env, check=True)


def output(*args, cwd=None):
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True).strip()


def checkout(url, tag, commit, dest):
    run('git','clone','--depth','1','--branch',tag,'--single-branch',url,dest)
    assert output('git','rev-parse','HEAD',cwd=dest) == commit, f'Unexpected commit for {url}@{tag}'
    # several upstream tags may share one commit, so `git describe` is not a reliable identity check
    assert tag in output('git','tag','--points-at','HEAD',cwd=dest).split(), f'Tag {tag} not at HEAD of {url}'


def verify(label, q):
    """q: a portable.PROFILES-style dict (the probe tool passes a freshly derived one)."""
    with tempfile.TemporaryDirectory(prefix='overtype-verified-sdkjs-') as d:
        base = Path(d)
        sdk = base/'sdkjs'
        checkout(portable.GIT, q['tag'], q['commit'], sdk)
        doc = sdk/'word/Editor/Document.js'
        original = doc.read_bytes()
        assert portable.git_blob(original) == q['doc_blob'], 'Document.js blob mismatch'
        assert portable.git_blob((sdk/'LICENSE').read_bytes()) == LICENSE_BLOB, 'LICENSE blob mismatch'
        addon_args = []
        for addon in q['addons']:
            path = base/addon['name']
            checkout(addon['git'], addon['tag'], addon['commit'], path)
            addon_args += ['--addon', path]
        doc.write_text(patches.patch_document_source(original.decode('utf-8')), encoding='utf-8')
        run('git','diff','--check',cwd=sdk)
        env = dict(os.environ, PRODUCT_VERSION=q['product_version'], BUILD_NUMBER=q['build_number'])
        run(sys.executable,'build/build.py','--product','word','--desktop',*addon_args,cwd=sdk,env=env)
        wd = sdk/'deploy/sdkjs/word'
        original_js = (wd/'sdk-all.js').read_text(encoding='utf-8')
        original_min = (wd/'sdk-all-min.js').read_text(encoding='utf-8')
        print('ENGINE API CHECK PASS:', patches.check_engine_api(original_js), 'patterns')
        modified = (patches.patch_compiled_word(original_js), patches.patch_compiled_min(original_min))
        for filename, data in zip(('sdk-all.js','sdk-all-min.js'), modified):
            f = base/filename
            f.write_text(data,encoding='utf-8')
            run('node','--check',f)
        assert modified[0].count('OO_OVERTYPE_UNDO_RC5') == 1
        assert modified[0].count('pending.at - a.lastTime > 10000') == 1
        assert modified[1].count('pluginMethod_OOOvertypeToggle') >= 1
        print(f'PINNED SDKJS SOURCE BUILD PASS [{label}]; edited ONLYOFFICE binaries were not installed.')
        print('NOT A GUI OR DOCX INTEGRITY TEST.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', action='append', choices=sorted(portable.PROFILES))
    names = ap.parse_args().profile or sorted(portable.PROFILES)
    for name in names:
        verify(name, portable.PROFILES[name])


if __name__ == '__main__':
    main()
