import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import portable as p

class InstallerTests(unittest.TestCase):
 def setUp(self):
    self.temp=tempfile.TemporaryDirectory(prefix='portable-tests-');self.addCleanup(self.temp.cleanup)
    self.tmp=Path(self.temp.name);self.home=self.tmp/'testuser';self.home.mkdir()
    self.vendor=self.tmp/'factory';self.vendor.mkdir()
    for rel in p.REL:
        f=self.vendor/rel;f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(('pristine-'+rel).encode())
    self.state=self.tmp/'root-state'
    self.patches=[patch.object(p,'VENDOR',self.vendor),patch.object(p,'STATE',self.state),
                  patch.object(p,'user_home',return_value=self.home),patch.object(p.os,'geteuid',return_value=0),
                  patch.object(p,'version'),patch.object(p,'idle')]
    for x in self.patches:x.start();self.addCleanup(x.stop)
    self.orig={rel:(self.vendor/rel).read_bytes() for rel in p.REL}
    self.cache,self.clone,self.candidate,_,_=p.path_set(self.home);self.candidate.mkdir(parents=True)
    m={'version':p.VERSION,'source_git_commit':p.COMMIT,'build':'native-rc5-10s-portable-beta',
        'source_vendor_sha256':{rel:p.digest(self.vendor/rel) for rel in p.REL},
        'candidate_sha256':{}}
    for rel in p.REL:
        f=self.candidate/Path(rel).name;f.write_bytes(('patched-'+rel).encode() + (b' OO_OVERTYPE_UNDO_RC5 pending.at - a.lastTime > 10000' if rel==p.REL[0] else b''))
        m['candidate_sha256'][rel]=p.digest(f)
    (self.candidate/'manifest.json').write_text(json.dumps(m))
    self.manifest=m
 def test_root_apply_restore(self):
    p.root_apply()
    for rel in p.REL:self.assertEqual(p.digest(self.vendor/rel),self.manifest['candidate_sha256'][rel])
    self.assertTrue(self.state.is_dir())
    p.root_rollback()
    for rel in p.REL:self.assertEqual((self.vendor/rel).read_bytes(),self.orig[rel])
    self.assertFalse(self.state.exists())
 def test_second_install_refused(self):
    p.root_apply()
    with self.assertRaises(p.Stop):p.root_apply()
 def test_backup_integrity_guards_restore(self):
    p.root_apply()
    (self.state/'sdk-all.js').write_bytes(b'corrupt')
    with self.assertRaises(p.Stop):p.root_rollback()
    self.assertTrue(self.state.exists())
 def test_external_modification_blocks_restore(self):
    p.root_apply()
    (self.vendor/p.REL[0]).write_bytes(b'external-change')
    with self.assertRaises(p.Stop):p.root_rollback()
 def test_state_restores_after_interrupted_single_file_change(self):
    p.root_apply()
    (self.vendor/p.REL[1]).write_bytes(self.orig[p.REL[1]])
    p.root_rollback()
    self.assertEqual((self.vendor/p.REL[0]).read_bytes(),self.orig[p.REL[0]])
 def test_plugin_standalone_install(self):
    plugin=self.home/p.PLUGIN_SUB;us=self.home/p.USER_STATE_NAME
    p.stage_plugin(us,plugin)
    self.assertEqual(json.loads((plugin/'config.json').read_text())['guid'],'asc.{A360C0D9-711B-4C90-BFB4-58AC023074E6}')
    self.assertTrue((plugin/'resources/icon.png').exists())
    with self.assertRaises(p.Stop):p.stage_plugin(us,plugin)
 def test_missing_candidate_refused(self):
    (self.candidate/'sdk-all.js').unlink()
    with self.assertRaises(p.Stop):p.root_apply()

if __name__=='__main__':unittest.main()
