import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patches

class PatchesTests(unittest.TestCase):
    def fixture(self):
        old=(patches.SRC/'native_logic_before.js').read_text()
        return ('// OO_OVERTYPE_V1_EXPERIMENTAL\n'
          +'// prelude\n'+old+'\n'
          +'CDocument.prototype.OnKeyDown = function(e)\n{\n\tthis.sendEvent("asc_onBeforeKeyDown", e);\n}\n'
          +'CDocument.prototype.OnMouseDown = function(e, X, Y, PageIndex)\n{\n}\n'
          +'CDocument.prototype.EnterText = function(value)\n{\n'
          +'\tthis.StartAction(AscDFH.historydescription_Document_AddLetter, null, null, codePoints);\n'
          +'\t\tthis._ooTryOvertypeOne();\n'
          +'\tthis.CheckLanguageOnTextAdd = false;\n\n\tthis.UpdateSelection();\n'
          +'\tthis.FinalizeAction();\n\n\treturn true;\n};\n')
    def test_reproduces_rc5_with_10s(self):
        result=patches.patch_compiled_word(self.fixture())
        self.assertEqual(result.count('OO_OVERTYPE_UNDO_RC5'),1)
        self.assertEqual(result.count('pending.at - a.lastTime > 10000'),1)
        self.assertEqual(result.count('CDocument.prototype._ooFinishOvertypeUndoRC3 = function ()'),1)
        self.assertIn('WeakMap()',result)
        self.assertIn('OO_OVERTYPE_UNDO_RC2',result)
        self.assertIn('OO_OVERTYPE_UNDO_RC3',result)
        self.assertNotIn('OO_OVERTYPE_UNDO_RC4',result)
        self.assertIn('if (this._ooTryOvertypeOne()) this._ooMarkOvertypeUndoPoint();',result)
    def test_refuses_second_patch(self):
        once=patches.patch_compiled_word(self.fixture())
        with self.assertRaises(patches.PatchError):patches.patch_compiled_word(once)
    def test_refuses_missing_anchor(self):
        with self.assertRaises(patches.PatchError):
            patches.patch_compiled_word(self.fixture().replace('this._ooTryOvertypeOne();','no_such_hook()'))
    def test_refuses_duplicate_anchor(self):
        with self.assertRaises(patches.PatchError):
            patches.patch_compiled_word(self.fixture()+'\n\tthis.sendEvent("asc_onBeforeKeyDown", e);')
    def test_plugin_sdkjs_api(self):
        result=patches.patch_compiled_min('abc\n'+patches.API_ANCHOR+' {}')
        self.assertIn('pluginMethod_OOOvertypeToggle',result)
        with self.assertRaises(patches.PatchError):patches.patch_compiled_min(result)

if __name__=='__main__':unittest.main()
