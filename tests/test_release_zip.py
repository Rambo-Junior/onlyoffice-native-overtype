import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from publish_rc import verify_archive

class ZipVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.z=Path(self.tmp.name)/'source.zip'
        cfg=json.dumps({'version':'1.0.0-rc.1'}).encode()
        self.cfg=cfg
        self.manifest=(hashlib.sha256(cfg).hexdigest()+'  plugin/config.json\n').encode()
    def create(self,manifest=None,payload=None):
        with zipfile.ZipFile(self.z,'w') as z:
            z.writestr('SHA256SUMS',self.manifest if manifest is None else manifest)
            z.writestr('plugin/config.json',self.cfg if payload is None else payload)
    def test_correct_source_zip(self):
        self.create();verify_archive(self.z)
    def test_tampered_source_zip_rejected(self):
        self.create(payload=b'{"version":"1.0.0-rc.1","malicious":true}')
        with self.assertRaises(RuntimeError):verify_archive(self.z)
    def test_wrong_version_rejected(self):
        c=b'{"version":"0.9.0-beta.2"}'
        self.create(manifest=(hashlib.sha256(c).hexdigest()+'  plugin/config.json\n').encode(),payload=c)
        with self.assertRaises(RuntimeError):verify_archive(self.z)
    def test_missing_manifest_rejected(self):
        with zipfile.ZipFile(self.z,'w') as z:z.writestr('plugin/config.json',self.cfg)
        with self.assertRaises(RuntimeError):verify_archive(self.z)
    def test_archive_path_traversal_rejected(self):
        m=(hashlib.sha256(self.cfg).hexdigest()+'  ../plugin/config.json\n').encode()
        self.create(manifest=m)
        with self.assertRaises(RuntimeError):verify_archive(self.z)

if __name__=='__main__':unittest.main()
