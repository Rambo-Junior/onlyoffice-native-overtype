"""Version-profile tests (9.4.0-129 and 10.0.0-169). Offline; the real build is covered by tools/verify_sdkjs_build.py."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patches
import portable as p

class ProfileTests(unittest.TestCase):
    def tearDown(self):p.select_profile(p.DEFAULT_PROFILE)

    def test_default_profile_is_the_validated_9_4(self):
        self.assertEqual((p.VERSION,p.TAG,p.COMMIT),('9.4.0-129','v9.4.0.129','75b53d504bfd81bfa35d59bb57dd9e56f7c9235d'))
        self.assertEqual(p.ADDONS,())
        self.assertTrue(str(p.STATE).endswith('portable-940129'))

    def test_profile_pins_are_well_formed_and_isolated(self):
        self.assertEqual(set(p.PROFILES),{'9.4.0-129','10.0.0-169'})
        seen=set()
        for name,q in p.PROFILES.items():
            self.assertRegex(q['commit'],r'^[0-9a-f]{40}$');self.assertRegex(q['doc_blob'],r'^[0-9a-f]{40}$')
            self.assertEqual(q['tag'],'v'+name.replace('-','.'))
            self.assertEqual(f"{q['product_version']}-{q['build_number']}",name)
            for key in ('state','cache','user_state'):
                self.assertNotIn(q[key],seen,'profiles must not share backup/cache/state paths');seen.add(q[key])
            for addon in q['addons']:
                self.assertRegex(addon['commit'],r'^[0-9a-f]{40}$');self.assertEqual(addon['tag'],q['tag'])

    def test_select_profile_binds_every_pin(self):
        p.select_profile('10.0.0-169')
        self.assertEqual(p.TAG,'v10.0.0.169');self.assertEqual(p.COMMIT,'3679e0375a758d7dc59d31337a45461be3525ed8')
        self.assertEqual(p.DOC_BLOB,'91a9135c4ca45358d15d38ba309a03ed71fb2d90')
        self.assertEqual((p.PRODUCT_VERSION,p.BUILD_NUMBER),('10.0.0','169'))
        self.assertEqual([a['name'] for a in p.ADDONS],['sdkjs-forms'])
        self.assertTrue(str(p.STATE).endswith('portable-1000169'))
        self.assertIn('NOT done',p.VALIDATION)

    def test_installed_version_selects_profile_and_unknown_is_refused(self):
        with patch.object(p,'get',return_value='10.0.0-169'):
            p.version();self.assertEqual(p.VERSION,'10.0.0-169')
        for bad in ('10.0.0-170','10.0.1-1','9.4.0-130','8.3.3-18'):
            with patch.object(p,'get',return_value=bad),self.assertRaises(p.Stop):p.version()

    def test_candidate_provenance_includes_addons(self):
        with tempfile.TemporaryDirectory() as t:
            home=Path(t);p.select_profile('10.0.0-169')
            _,_,cand,_,_=p.path_set(home);cand.mkdir(parents=True)
            vendor=home/'v'
            m={'version':p.VERSION,'source_git_commit':p.COMMIT,'build':p.BUILD_ID,'candidate_sha256':{},'source_vendor_sha256':{}}
            for rel in p.REL:
                f=cand/Path(rel).name;f.write_bytes(b'x OO_OVERTYPE_UNDO_RC5 pending.at - a.lastTime > 10000')
                (vendor/rel).parent.mkdir(parents=True,exist_ok=True);(vendor/rel).write_bytes(b'orig')
                m['candidate_sha256'][rel]=p.digest(f);m['source_vendor_sha256'][rel]=p.digest(vendor/rel)
            def check(manifest):
                (cand/'manifest.json').write_text(json.dumps(manifest))
                with patch.object(p,'VENDOR',vendor):return p.candidate_check(home)
            with self.assertRaises(p.Stop):check(m)                                   # addon pin missing
            with self.assertRaises(p.Stop):check({**m,'addons':{'sdkjs-forms':'0'*40}})  # wrong addon commit
            check({**m,'addons':{a['name']:a['commit'] for a in p.ADDONS}})            # exact pins accepted

    def test_tag_identity_survives_several_tags_on_one_commit(self):
        # Upstream tags v10.0.0.167..170 share one commit; `git describe` then names only one of them.
        with tempfile.TemporaryDirectory() as t:
            g=lambda *a:subprocess.check_output(['git','-c','user.name=t','-c','user.email=t@t',*a],cwd=t,text=True).strip()
            g('init','-q');g('commit','--allow-empty','-q','-m','x')
            for tag in ('v10.0.0.167','v10.0.0.169','v10.0.0.170'):g('tag',tag)
            self.assertNotEqual(g('describe','--exact-match','--tags'),'v10.0.0.169')   # the old check would stop here
            self.assertIn('v10.0.0.169',g('tag','--points-at','HEAD').split())          # the installer's check
        src=(ROOT/'portable.py').read_text(encoding='utf8')
        self.assertIn("'tag','--points-at','HEAD'",src);self.assertNotIn("'describe','--exact-match'",src)

class EngineApiTests(unittest.TestCase):
    def test_examples_match_their_own_patterns(self):
        for example,pattern in patches.ENGINE_API:self.assertRegex(example,pattern)
    def test_complete_bundle_passes(self):
        bundle='\n'.join(e for e,_ in patches.ENGINE_API)
        self.assertEqual(patches.check_engine_api(bundle),len(patches.ENGINE_API))
    def test_each_missing_api_is_detected(self):
        for example,_ in patches.ENGINE_API:
            bundle='\n'.join(e for e,_ in patches.ENGINE_API if e!=example)
            with self.assertRaises(patches.PatchError,msg=example):patches.check_engine_api(bundle)

class PluginConfigTests(unittest.TestCase):
    def test_plugin_runs_as_autostart_background_plugin(self):
        # ONLYOFFICE maps an unknown "type" string to Background; the explicit value keeps that behaviour and
        # 10.x honours "autostart" (older editors ignore it).
        cfg=json.loads((ROOT/'plugin/config.json').read_text(encoding='utf8'))
        var=cfg['variations'][0]
        self.assertEqual(var['type'],'background');self.assertIs(var['autostart'],True)
        self.assertEqual(var['EditorsSupport'],['word'])
        self.assertIn('10.0.0-169',cfg['description']);self.assertIn('9.4.0-129',cfg['description'])

if __name__=='__main__':unittest.main()
