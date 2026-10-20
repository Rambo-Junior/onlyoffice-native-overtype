#!/usr/bin/env python3
"""Build the exact pinned upstream SDKJS and verify source-only overtype patch.

CI build, not a desktop GUI or document-integrity test. Never writes to /opt.
"""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patches
import portable


def run(*args, cwd=None, env=None):
    print('$', ' '.join(map(str,args)), flush=True)
    subprocess.run([str(x) for x in args], cwd=cwd, env=env, check=True)


def output(*args, cwd=None):
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True).strip()


def main():
    with tempfile.TemporaryDirectory(prefix='overtype-verified-sdkjs-') as d:
        base = Path(d)
        sdk = base/'sdkjs'
        run('git','clone','--depth','1','--branch',portable.TAG,'--single-branch',portable.GIT,sdk)
        assert output('git','rev-parse','HEAD',cwd=sdk) == portable.COMMIT, 'Unexpected SDKJS commit'
        doc = sdk/'word/Editor/Document.js'
        original = doc.read_bytes()
        assert portable.git_blob(original) == portable.DOC_BLOB, 'Document.js blob mismatch'
        license_bytes = (sdk/'LICENSE').read_bytes()
        assert portable.git_blob(license_bytes) == '53bc62cde3c705aa2d03b895b966bd6250f389ae', 'LICENSE blob mismatch'
        doc.write_text(patches.patch_document_source(original.decode('utf-8')), encoding='utf-8')
        run('git','diff','--check',cwd=sdk)
        env = dict(os.environ, PRODUCT_VERSION='9.4.0', BUILD_NUMBER='129')
        run(sys.executable,'build/build.py','--product','word','--desktop',cwd=sdk,env=env)
        wd = sdk/'deploy/sdkjs/word'
        original_js = (wd/'sdk-all.js').read_text(encoding='utf-8')
        original_min = (wd/'sdk-all-min.js').read_text(encoding='utf-8')
        modified = (patches.patch_compiled_word(original_js), patches.patch_compiled_min(original_min))
        for filename, data in zip(('sdk-all.js','sdk-all-min.js'), modified):
            f = base/filename
            f.write_text(data,encoding='utf-8')
            run('node','--check',f)
        assert modified[0].count('OO_OVERTYPE_UNDO_RC5') == 1
        assert modified[0].count('pending.at - a.lastTime > 10000') == 1
        assert modified[1].count('pluginMethod_OOOvertypeToggle') >= 1
        print('PINNED SDKJS SOURCE BUILD PASS; edited ONLYOFFICE binaries were not installed.')
        print('NOT A GUI OR DOCX INTEGRITY TEST.')


if __name__ == '__main__':
    main()
