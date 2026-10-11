"""Reproduce RC5/10s modifications from pinned ONLYOFFICE SDKJS 9.4.0.129.

No vendor installation paths are opened here. Anchors are exact, fail closed.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from patch_sdkjs import patch as patch_upstream_document

SRC=Path(__file__).resolve().parent/'src'
MARKER='ONLYOFFICE_OVERTYPE_NATIVE_RC1_940129'
API_ANCHOR='Api.prototype["pluginMethod_AddToolbarMenuItem"] = function(items)'
PLUGIN_METHOD='''// ONLYOFFICE_OVERTYPE_NATIVE_RC1_940129: internal plugin bridge, no X11 helper.
Api.prototype["pluginMethod_OOOvertypeToggle"] = function() {
    var doc = this.WordControl && this.WordControl.m_oLogicDocument;
    if (!doc) return null;
    doc._ooOvertypeEnabled = !doc._ooOvertypeEnabled;
    return !!doc._ooOvertypeEnabled;
};
'''
HELPER_ANCHOR='CDocument.prototype._ooTryOvertypeOne = function() {'
CALL_ANCHOR='\t\tthis._ooTryOvertypeOne();'
KEY_ANCHOR='\tthis.sendEvent("asc_onBeforeKeyDown", e);'
MOUSE_ANCHOR='CDocument.prototype.OnMouseDown = function(e, X, Y, PageIndex)\n{'
FINALIZE_ANCHOR='\tthis.CheckLanguageOnTextAdd = false;\n\n\tthis.UpdateSelection();\n\tthis.FinalizeAction();\n\n\treturn true;\n};'
OLD_TIMEOUT='pending.at - a.lastTime > 1800'
NEW_TIMEOUT='pending.at - a.lastTime > 10000'

class PatchError(RuntimeError):pass

def exact_replace(s, old, new, label):
    num=s.count(old)
    if num!=1:raise PatchError(f'{label}: expected exactly 1 anchor, found {num}')
    return s.replace(old,new,1)

def patch_document_source(clean):
    return patch_upstream_document(clean,(SRC/'native_logic.js').read_text(encoding='utf8'))

def patch_compiled_word(built):
    """Replay the sequence used in tested RC5: RC1 -> RC2 -> RC3 -> RC4 -> RC5 -> 10s."""
    old=(SRC/'native_logic_before.js').read_text(encoding='utf8')
    new=(SRC/'native_logic_after.js').read_text(encoding='utf8')
    if MARKER in built or 'OO_OVERTYPE_V1_EXPERIMENTAL' not in built:
        raise PatchError('Not an unmodified pinned experimental SDKJS Word bundle')
    s=exact_replace(built,old,'// '+MARKER+'\n'+new,'RC1 native selection fix')
    for needle in [HELPER_ANCHOR,CALL_ANCHOR,KEY_ANCHOR,MOUSE_ANCHOR,FINALIZE_ANCHOR]:
        if s.count(needle)!=1:raise PatchError(f'RC2/RC3 anchor missing or duplicate: {needle!r}')
    undo=(SRC/'undo_runtime.js').read_text(encoding='utf8')
    s=exact_replace(s,HELPER_ANCHOR,undo+'\n'+HELPER_ANCHOR,'RC2 runtime')
    s=exact_replace(s,CALL_ANCHOR,'\t\tif (this._ooTryOvertypeOne()) this._ooMarkOvertypeUndoPoint();','RC2 mark hook')
    marker='OO_OVERTYPE_UNDO_RC2'
    key=('\n\t// '+marker+': separate Undo groups after navigation/shortcuts.\n'
         '\tif (this._ooOvertypeEnabled && (e.CtrlKey || e.AltKey || e.MetaKey ||\n'
         '\t\t[8,9,13,27,33,34,35,36,37,38,39,40,45,46].includes(e.KeyCode)))\n'
         '\t\tthis._ooOvertypeUndoEpoch = (this._ooOvertypeUndoEpoch || 0) + 1;')
    s=exact_replace(s,KEY_ANCHOR,KEY_ANCHOR+key,'RC2 keyboard group break')
    mouse=('\n\t// '+marker+': mouse repositioning breaks continuous typing.\n'
           '\tif (this._ooOvertypeEnabled)\n'
           '\t\tthis._ooOvertypeUndoEpoch = (this._ooOvertypeUndoEpoch || 0) + 1;')
    s=exact_replace(s,MOUSE_ANCHOR,MOUSE_ANCHOR+mouse,'RC2 mouse group break')
    rc3=(SRC/'rc3_runtime.js').read_text(encoding='utf8')
    s=exact_replace(s,HELPER_ANCHOR,rc3+'\n'+HELPER_ANCHOR,'RC3 runtime')
    finalize=FINALIZE_ANCHOR.replace('\tthis.FinalizeAction();',
        '\tthis.FinalizeAction();\n\t// OO_OVERTYPE_UNDO_RC3: finalize a run only after the history point was committed.\n'
        '\tif (this._ooOvertypePendingRC3) this._ooFinishOvertypeUndoRC3();')
    s=exact_replace(s,FINALIZE_ANCHOR,finalize,'RC3 finalize hook')
    s=exact_replace(s,rc3,(SRC/'rc4_runtime.js').read_text(encoding='utf8'),'RC4 runtime replacement')
    s=exact_replace(s,(SRC/'rc4_runtime.js').read_text(encoding='utf8'),
                    (SRC/'rc5_runtime.js').read_text(encoding='utf8'),'RC5 WeakMap replacement')
    s=exact_replace(s,OLD_TIMEOUT,NEW_TIMEOUT,'10-second typing timeout')
    if s.count('OO_OVERTYPE_UNDO_RC5')!=1 or s.count(NEW_TIMEOUT)!=1:
        raise PatchError('RC5/10s identity check failed')
    return s

def patch_compiled_min(built):
    if MARKER in built or 'pluginMethod_OOOvertypeToggle' in built:
        raise PatchError('The SDKJS min bundle is already patched')
    return exact_replace(built,API_ANCHOR,PLUGIN_METHOD+'\n'+API_ANCHOR,'RC1 native toolbar method')
