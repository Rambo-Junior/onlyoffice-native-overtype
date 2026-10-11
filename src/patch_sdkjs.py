#!/usr/bin/env python3
"""Opt-in research patch for ONLYOFFICE sdkjs/word/Editor/Document.js.

This is NOT a production plugin, package or installer. Do not patch vendor binaries.
Usage: python3 patch_sdkjs.py /path/to/sdkjs/word/Editor/Document.js [--apply]
Omit --apply to only inspect/preflight. --apply backs up file and edits source.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

TAG = 'OO_OVERTYPE_V1_EXPERIMENTAL'
ONKEY = '''CDocument.prototype.OnKeyDown = function(e)
{
\tthis.sendEvent("asc_onBeforeKeyDown", e);'''
ONKEY_REPLACEMENT = '''CDocument.prototype.OnKeyDown = function(e)
{
\tthis.sendEvent("asc_onBeforeKeyDown", e);
\t// OO_OVERTYPE_V1_EXPERIMENTAL: plain Insert toggles overtype for this document.
\t// Ctrl+Insert (copy) and Shift+Insert (paste) retain their native behavior.
\tif (e.KeyCode === 45 && !e.CtrlKey && !e.ShiftKey && !e.AltKey && !e.MetaKey)
\t{
\t\tthis._ooOvertypeEnabled = !this._ooOvertypeEnabled;
\t\treturn keydownresult_PreventAll;
\t}'''
BEGIN_ENTRY = 'CDocument.prototype.EnterText = function(value)\n{'
ACTION = '''\tthis.StartAction(AscDFH.historydescription_Document_AddLetter, null, null, codePoints);
\t
\tthis.DrawingDocument.TargetStart();'''
ACTION_REPLACEMENT = '''\tthis.StartAction(AscDFH.historydescription_Document_AddLetter, null, null, codePoints);
\t// OO_OVERTYPE_V1_EXPERIMENTAL: one delete within the same Undo action.
\t// Failed eligibility checks must insert normally without deleting anything.
\tif (this._ooOvertypeEnabled && !this.IsSelectionUse()
\t\t&& ((Array.isArray(codePoints) && codePoints.length === 1)
\t\t\t|| typeof codePoints === "number"))
\t\tthis._ooTryOvertypeOne();
\t
\tthis.DrawingDocument.TargetStart();'''


def patch(text: str, helper: str) -> str:
    if TAG in text:
        raise ValueError('Already patched; refusing to patch twice')
    if text.count(ONKEY) != 1 or text.count(BEGIN_ENTRY) != 1 or text.count(ACTION) != 1:
        raise ValueError('Upstream structure differs; no changes made')
    text = text.replace(ONKEY, ONKEY_REPLACEMENT, 1)
    text = text.replace(ACTION, ACTION_REPLACEMENT, 1)
    position = text.index(BEGIN_ENTRY)
    text = text[:position] + helper + '\n' + text[position:]
    return text


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('document_js', type=Path)
    arg.add_argument('--apply', action='store_true', help='Explicitly modify source and write .backup')
    args = arg.parse_args()
    source = args.document_js
    if not source.is_file():
        print(f'File missing: {source}', file=sys.stderr)
        return 2
    original = source.read_text(encoding='utf-8')
    helper = (Path(__file__).parent / 'native_logic.js').read_text(encoding='utf-8')
    try:
        output = patch(original, helper)
    except ValueError as exc:
        print(f'Preflight rejected: {exc}', file=sys.stderr)
        return 3
    if not args.apply:
        print('Preflight OK. No files changed. EXPERIMENTAL; not production-ready.')
        return 0
    backup = source.with_suffix(source.suffix + '.overtype-backup')
    if backup.exists():
        print('Backup already exists; refusing to overwrite.', file=sys.stderr)
        return 4
    backup.write_text(original, encoding='utf-8')
    source.write_text(output, encoding='utf-8')
    print(f'EXPERIMENTAL SOURCE PATCH saved: {source} (backup: {backup})')
    return 0

if __name__ == '__main__':
    sys.exit(main())
