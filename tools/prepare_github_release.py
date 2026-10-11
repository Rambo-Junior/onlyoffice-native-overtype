#!/usr/bin/env python3
"""Copy exact upstream LICENSE from verified SDKJS git checkout; zip source release."""
import hashlib,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=Path.home()/'.cache/onlyoffice-overtype-native-940129/sdkjs'
COMMIT='75b53d504bfd81bfa35d59bb57dd9e56f7c9235d'
LICENSE_BLOB='53bc62cde3c705aa2d03b895b966bd6250f389ae'
if not (SRC/'.git').is_dir():sys.exit('SDKJS forrás hiányzik. Előbb: bash run.sh --build')
sha=subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip()
if sha!=COMMIT:sys.exit('Az SDKJS forráscommit eltér a rögzített v9.4.0.129 verziótól')
raw=subprocess.check_output(['git','-C',str(SRC),'show','HEAD:LICENSE'])
blob=subprocess.run(['git','hash-object','--stdin'],input=raw,stdout=subprocess.PIPE,check=True).stdout.decode().strip()
if blob!=LICENSE_BLOB:sys.exit('Az upstream LICENSE git-blob hash eltér; STOP')
(ROOT/'LICENSE').write_bytes(raw)
if b'Additional Terms' not in raw or b'Ascensio System SIA' not in raw:sys.exit('Upstream kiegészítések hiányoznak')
# Hash all inputs after final source prep; omit checksum itself.
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.pyc')
(ROOT/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files),encoding='utf8')
output=ROOT.parent/'onlyoffice-native-overtype-v0.9.0-beta.1-source.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted([*files,ROOT/'SHA256SUMS']):
        z.write(p,arcname=p.relative_to(ROOT).as_posix())
print('SOURCE RELEASE ARCHIVE:',output)
print('SHA256:',hashlib.sha256(output.read_bytes()).hexdigest())
print('LICENSE git blob verified:',blob)
