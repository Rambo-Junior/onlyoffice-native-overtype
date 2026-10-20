"""Static release gates; these do NOT substitute for a real editor GUI test."""
from pathlib import Path
import json
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import portable

class ReleaseCandidateTests(unittest.TestCase):
    def test_explicit_rc_version(self):
        cfg=json.loads((ROOT/'plugin/config.json').read_text(encoding='utf-8'))
        self.assertEqual(cfg['version'], '1.0.0-rc.1')
    def test_pinned_editor_version(self):
        self.assertEqual(portable.VERSION, '9.4.0-129')
        self.assertEqual(portable.COMMIT, '75b53d504bfd81bfa35d59bb57dd9e56f7c9235d')
    def test_build_and_source_only(self):
        t=(ROOT/'tools/verify_sdkjs_build.py').read_text(encoding='utf8')
        self.assertIn('patch_compiled_word', t)
        self.assertIn('patch_compiled_min', t)
        self.assertNotIn('root_apply(', t)
    def test_ci_has_build(self):
        t=(ROOT/'.github/workflows/sdkjs-source-build.yml').read_text(encoding='utf8')
        self.assertIn('verify_sdkjs_build.py',t)
        self.assertIn('ubuntu-24.04',t)
    def test_existing_undo_group_and_about(self):
        js=(ROOT/'src/rc5_runtime.js').read_text(encoding='utf8')
        self.assertIn('pending.at - a.lastTime > 1800', js)
        ui=(ROOT/'plugin/about.html').read_text(encoding='utf8')
        self.assertIn('Ascensio System SIA',ui)
    def test_reversible_installer_not_overwritten(self):
        t=(ROOT/'portable.py').read_text(encoding='utf8')
        self.assertIn('def root_rollback():',t)
        self.assertIn('def root_apply():',t)
    def test_release_docs_do_not_claim_stable(self):
        t=(ROOT/'RELEASE_CANDIDATE_V1_EN.md').read_text(encoding='utf8')
        self.assertIn('NOT a stable',t)
        self.assertIn('29/29',t)

if __name__=='__main__': unittest.main()
