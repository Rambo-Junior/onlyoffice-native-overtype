#!/usr/bin/env python3
"""Pinned ONLYOFFICE Desktop Editors 9.4.0-129 native overtype beta.

--check: read-only target checks
--build: clone pinned upstream & compile user-owned candidate (does not alter /opt)
--install: interactive install; backup-first root replacement; standalone plugin
--status: inspect installed bundles
--rollback: restore the exact original bundles and previous plugin, if any

Source distribution; never runs as root except --_root-apply / --_root-rollback.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
VERSION='9.4.0-129'
TAG='v9.4.0.129'
COMMIT='75b53d504bfd81bfa35d59bb57dd9e56f7c9235d'
DOC_BLOB='3b7d45fe3db44e9eab29ce9a2d69415971a5cd4d'
GIT='https://github.com/ONLYOFFICE/sdkjs.git'
VENDOR=Path('/opt/onlyoffice/desktopeditors')
REL=('editors/sdkjs/word/sdk-all.js','editors/sdkjs/word/sdk-all-min.js')
STATE=Path('/var/lib/onlyoffice-overtype-native-portable-940129')
CACHE_NAME='.cache/onlyoffice-overtype-native-940129'
USER_STATE_NAME='.local/state/onlyoffice-overtype-native-940129'
PLUGIN_SUB='.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}'
PLUGIN_SRC=HERE/'plugin'
MARKER='ONLYOFFICE_OVERTYPE_NATIVE_RC1_940129'
MARKER_RC5='OO_OVERTYPE_UNDO_RC5'
class Stop(RuntimeError):pass

def digest(x):
    h=hashlib.sha256()
    with Path(x).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def git_blob(content):return hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()

def plain(p,typ='file'):
    if p.is_symlink() or not getattr(p,'is_'+typ)():raise Stop(f'Missing or symlink {typ}: {p}')

def user_home():
    if os.geteuid()==0:
        u=os.environ.get('SUDO_USER','')
        if not u or u=='root':raise Stop('Root helper requires a real sudo user')
        return Path(pwd.getpwnam(u).pw_dir)
    return Path.home()

def path_set(home):
    cache=home/CACHE_NAME
    return cache,cache/'sdkjs',cache/'candidate',home/USER_STATE_NAME,home/PLUGIN_SUB

def run(cmd,**kwargs):
    print('$ '+' '.join(str(a) for a in cmd),flush=True)
    subprocess.run([str(c) for c in cmd],check=True,**kwargs)

def get(cmd,**kwargs):
    return subprocess.check_output([str(c) for c in cmd],text=True,stderr=subprocess.STDOUT,**kwargs).strip()

def version():
    try:v=get(['dpkg-query','-W','-f=${Version}','onlyoffice-desktopeditors'])
    except (OSError,subprocess.CalledProcessError) as exc:raise Stop('ONLYOFFICE dpkg version unavailable') from exc
    if v!=VERSION:raise Stop(f'Supported only {VERSION}; installed {v}')

def idle():
    try:p=subprocess.run(['pgrep','-x','DesktopEditors'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except OSError as e:raise Stop('pgrep unavailable') from e
    if p.returncode!=1:raise Stop('Close all ONLYOFFICE processes before proceeding')

def legacy():
    # No automatic manipulation of unrelated X11 helpers on fresh machines.
    auto= user_home()/'.config/autostart/onlyoffice-overtype-bridge.desktop'
    if auto.exists() or auto.is_symlink():raise Stop('Legacy X11 overtype autostart detected; disable/remove it first')
    try:
        with socket.create_connection(('127.0.0.1',39167),timeout=.35):
            raise Stop('Legacy overtype port 39167 is occupied; do not run native and X11 bridge together')
    except OSError:pass

def clean_vendor():
    plain(VENDOR,'dir')
    for rel in REL:
        p=VENDOR/rel;plain(p)
        with p.open('rb') as f: data=f.read()
        if MARKER.encode() in data or MARKER_RC5.encode() in data:
            raise Stop(f'An existing native overtype patch was detected: {p}. Use the original rollback, not this installer')
    if STATE.exists() or STATE.is_symlink():raise Stop('An existing portable root backup already exists')

def user_check(build=False):
    if os.geteuid()==0:raise Stop('Run as regular user, without sudo')
    if os.environ.get('XDG_SESSION_TYPE')!='x11' or not os.environ.get('DISPLAY'):
        raise Stop('Linux X11 desktop session required')
    for b in ('python3','node','git','dpkg-query','sudo','pgrep'):
        if not shutil.which(b):raise Stop('Missing dependency: '+b)
    version();idle();legacy();clean_vendor()
    cache,clone,candidate,user_state,plugin=path_set(user_home())
    if cache.is_symlink() or user_state.is_symlink():raise Stop('Unsafe user path')
    if user_state.exists():raise Stop('Previous portable user state exists; use --rollback')
    if plugin.exists() or plugin.is_symlink():raise Stop('Overtype plugin GUID already exists; do not overwrite another installation')
    if build and shutil.disk_usage(user_home()).free<4*1024**3:raise Stop('4 GiB free space required for source build')
    print('CHECK PASS: pinned version, X11, no editor, no X11 bridge, no existing plugin/native installation.')

def ensure_git_source(clone):
    cache=clone.parent
    if clone.is_symlink():raise Stop('Git source symlink refused')
    if not clone.exists():
        if cache.is_symlink():raise Stop('Cache symlink refused')
        cache.mkdir(parents=True,exist_ok=True)
        dl=cache/f'.sdkjs-download-{os.getpid()}'
        if dl.exists():raise Stop('Temporary clone already exists')
        try:
            run(['git','clone','--depth','1','--single-branch','--branch',TAG,GIT,dl])
            dl.rename(clone)
        finally:
            if dl.is_dir() and not dl.is_symlink():shutil.rmtree(dl)
    plain(clone,'dir');plain(clone/'.git','dir')
    if get(['git','remote','get-url','origin'],cwd=clone) not in (GIT,GIT[:-4]):
        raise Stop('Unexpected upstream Git origin')
    if get(['git','rev-parse','HEAD'],cwd=clone)!=COMMIT:raise Stop('Upstream Git commit mismatch')
    if get(['git','describe','--exact-match','--tags'],cwd=clone)!=TAG:raise Stop('Upstream Git tag mismatch')
    p=clone/'word/Editor/Document.js';plain(p)
    src=p.read_bytes()
    b=p.with_suffix('.js.overtype-clean-backup')
    import patches
    if b.exists() or b.is_symlink():
        plain(b)
        raw=b.read_bytes()
        if git_blob(raw)!=DOC_BLOB or p.read_text(encoding='utf8')!=patches.patch_document_source(raw.decode('utf8')):
            raise Stop('Existing modified SDKJS source differs from exact pinned patch')
        expected=b' M word/Editor/Document.js\0'
    else:
        if git_blob(src)!=DOC_BLOB:raise Stop('Upstream Document.js Git blob mismatch')
        expected=b''
    current=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=no'],cwd=clone)
    if current!=expected:raise Stop('Unexpected tracked Git modification; refusing build')
    if not b.exists():
        b.write_bytes(src);b.chmod(0o600)
        p.write_text(patches.patch_document_source(src.decode('utf8')),encoding='utf8')
    current=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=no'],cwd=clone)
    if current!=b' M word/Editor/Document.js\0':raise Stop('SDKJS Git status changed unexpectedly after patch')
    run(['git','diff','--check'],cwd=clone)
    return p

def atomic(p,content, *, existing=True):
    if existing:plain(p)
    if p.is_symlink():raise Stop('Symlink target refused: '+str(p))
    old=p.stat() if existing else None
    fd,temp=tempfile.mkstemp(prefix='.overtype-atomic-',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
        if old:
            os.chmod(temp,old.st_mode&0o777)
            if os.geteuid()==0:os.chown(temp,old.st_uid,old.st_gid)
        else:os.chmod(temp,0o600)
        os.replace(temp,p)
        d=os.open(p.parent,os.O_DIRECTORY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def source_build():
    user_check(build=True)
    cache,clone,candidate,state,plug=path_set(user_home())
    if candidate.exists() or candidate.is_symlink():raise Stop('Existing candidate; refusing to overwrite')
    ensure_git_source(clone)
    from patches import patch_compiled_word,patch_compiled_min
    env=os.environ.copy();env.update(PRODUCT_VERSION='9.4.0',BUILD_NUMBER='129')
    run([sys.executable,'build/build.py','--product','word','--desktop'],cwd=clone,env=env)
    srcs=[clone/'deploy/sdkjs/word'/Path(rel).name for rel in REL]
    for p in srcs:
        plain(p)
        if p.stat().st_size<100000:raise Stop('Built bundle unexpectedly small')
        run(['node','--check',p])
    raw=[p.read_text(encoding='utf8') for p in srcs]
    final=[patch_compiled_word(raw[0]),patch_compiled_min(raw[1])]
    if 'OO_OVERTYPE_UNDO_RC5' not in final[0] or 'pending.at - a.lastTime > 10000' not in final[0]:
        raise Stop('Missing RC5/10s patch')
    if 'pluginMethod_OOOvertypeToggle' not in final[1]:raise Stop('Missing native toolbar SDKJS method')
    candidate.mkdir(mode=0o700)
    try:
        for rel,content in zip(REL,final):
            f=candidate/Path(rel).name
            f.write_text(content,encoding='utf8');f.chmod(0o600)
            run(['node','--check',f])
        manifest={'version':VERSION,'source_git_commit':COMMIT,'source_git_tag':TAG,
            'source_document_blob':DOC_BLOB,'build':'native-rc5-10s-portable-beta',
            'source_vendor_sha256':{rel:digest(VENDOR/rel) for rel in REL},
            'candidate_sha256':{rel:digest(candidate/Path(rel).name) for rel in REL},
            'created_utc':datetime.now(timezone.utc).isoformat(),
            'test_status':'Source build / Node syntax verified; target GUI regression pending'}
        (candidate/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
        (candidate/'manifest.json').chmod(0o600)
    except BaseException:
        shutil.rmtree(candidate)
        raise
    print('BUILD PASS: reproducible source candidate staged in',candidate)
    print('NO VENDOR FILES WERE MODIFIED. Next --install after reviewing the README.')

def candidate_check(home):
    cache,clone,candidate,state,plugin=path_set(home)
    plain(candidate,'dir');plain(candidate/'manifest.json')
    manifest=json.loads((candidate/'manifest.json').read_text())
    if manifest.get('version')!=VERSION or manifest.get('source_git_commit')!=COMMIT or manifest.get('build')!='native-rc5-10s-portable-beta':
        raise Stop('Candidate provenance invalid')
    for rel in REL:
        f=candidate/Path(rel).name;plain(f)
        if digest(f)!=manifest['candidate_sha256'][rel]:raise Stop('Candidate SHA256 mismatch: '+rel)
        if digest(VENDOR/rel)!=manifest['source_vendor_sha256'][rel]:raise Stop('Original vendor SHA256 mismatch: '+rel)
    if (candidate/'sdk-all.js').read_bytes().count(b'OO_OVERTYPE_UNDO_RC5')!=1:
        raise Stop('RC5 candidate marker absent or duplicated')
    if (candidate/'sdk-all.js').read_bytes().count(b'pending.at - a.lastTime > 10000')!=1:
        raise Stop('10-second candidate missing')
    return candidate,manifest

def safe_plugin_tree(path):
    if path.is_symlink():raise Stop('Plugin path symlink refused')
    if path.exists():
        for p in path.rglob('*'):
            if p.is_symlink():raise Stop('Plugin contains symlink: '+str(p))

def stage_plugin(user_state,plugin):
    # The native toolbar is a standalone plugin (no old bridge installation required).
    safe_plugin_tree(PLUGIN_SRC)
    if plugin.exists() or plugin.is_symlink():raise Stop('Plugin GUID already occupied')
    if user_state.exists() or user_state.is_symlink():raise Stop('User state already exists')
    user_state.mkdir(parents=True,mode=0o700)
    plugin.parent.mkdir(parents=True,exist_ok=True)
    safe_plugin_tree(plugin.parent)
    shutil.copytree(PLUGIN_SRC,plugin,symlinks=False)
    data={'plugin_created':True,'plugin_path':str(plugin),
          'created_utc':datetime.now(timezone.utc).isoformat()}
    (user_state/'state.json').write_text(json.dumps(data,indent=2)+'\n')
    (user_state/'state.json').chmod(0o600)

def check_installed(home):
    candidate,manifest=candidate_check_skip_original(home)
    for rel in REL:
        if digest(VENDOR/rel)!=manifest['candidate_sha256'][rel]:return False
    return True

def candidate_check_skip_original(home):
    _,_,candidate,_,_=path_set(home)
    plain(candidate,'dir');plain(candidate/'manifest.json')
    manifest=json.loads((candidate/'manifest.json').read_text())
    if manifest.get('version')!=VERSION or manifest.get('source_git_commit')!=COMMIT:return (candidate,{})
    for rel in REL:
        f=candidate/Path(rel).name;plain(f)
        if digest(f)!=manifest['candidate_sha256'][rel]:raise Stop('Candidate hash differs')
    return candidate,manifest

def privileged_call(mode):
    # Source is unprivileged and visible; sudo runs the exact same executable in root mode.
    run(['sudo','/usr/bin/python3',HERE/'portable.py',mode])

def install():
    user_check();candidate,manifest=candidate_check(user_home())
    if not sys.stdin.isatty():raise Stop('Interactive terminal required')
    print('This will replace TWO ONLYOFFICE Word JS bundles under /opt, after root backup.')
    print('Beta passed 4/4 manual smoke checks on a second Mint 22.3 X11 machine (2026-10-11); complex DOCX remains untested.')
    if input('Confirm with TELEPITES: ').strip()!='TELEPITES':raise Stop('Installation declined')
    run(['sudo','-v'])
    user_state=None
    cache,clone,candidate,user_state,plugin=path_set(user_home())
    # Pre-create the standalone toolbar plugin before modifying the vendor.
    try:
        stage_plugin(user_state,plugin)
        privileged_call('--_root-apply')
        if not check_installed(user_home()):raise Stop('Installed bundle hashes mismatch')
        plain(plugin/'config.json');plain(plugin/'quick_action.js')
        print('INSTALL PASS: native RC5/10s active. Run disposable DOCX smoke test.')
        print('Rollback:',HERE/'run.sh','--rollback')
    except BaseException:
        # Root helper can have left STATE even if it exited nonzero. Attempt root restore first.
        if STATE.exists():
            try:privileged_call('--_root-rollback')
            except BaseException:
                print('CRITICAL: root rollback failed. Do not start ONLYOFFICE.',file=sys.stderr)
                raise
        if plugin.exists():shutil.rmtree(plugin)
        if user_state.exists():shutil.rmtree(user_state)
        raise

def root_apply():
    if os.geteuid()!=0:raise Stop('Root helper requires sudo')
    version();idle()
    home=user_home();cand,m=candidate_check(home)
    if STATE.exists() or STATE.is_symlink():raise Stop('A previous root backup exists')
    # Assemble a COMPLETE backup in a private temporary directory, verify every
    # file, then atomically publish the restore state before touching /opt.
    STATE.parent.mkdir(parents=True,exist_ok=True)
    temp=STATE.parent/('.overtype-portable-backup-'+str(os.getpid()))
    if temp.exists() or temp.is_symlink():raise Stop('Temporary root backup exists')
    temp.mkdir(mode=0o700)
    published=False
    try:
        for rel in REL:
            f=VENDOR/rel;plain(f)
            b=temp/Path(rel).name;shutil.copy2(f,b)
            if digest(b)!=m['source_vendor_sha256'][rel]:raise Stop('Backup verify failed')
        (temp/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
        os.chmod(temp/'manifest.json',0o600)
        temp.rename(STATE);published=True
        for rel in REL:
            f=VENDOR/rel
            atomic(f,(cand/Path(rel).name).read_bytes())
            if digest(f)!=m['candidate_sha256'][rel]:raise Stop('Installed digest mismatch: '+rel)
        print('ROOT INSTALL PASS: factory files backed up, both Word bundles replaced')
    except BaseException:
        if published:
            try:root_rollback()
            except BaseException:
                print('CRITICAL ROOT RESTORE FAILURE; do not start ONLYOFFICE.',file=sys.stderr)
        raise
    finally:
        if not published and temp.is_dir() and not temp.is_symlink():shutil.rmtree(temp)

def root_rollback():
    if os.geteuid()!=0:raise Stop('Root restore requires sudo')
    version();idle();plain(STATE,'dir');plain(STATE/'manifest.json')
    m=json.loads((STATE/'manifest.json').read_text())
    if m.get('version')!=VERSION or m.get('source_git_commit')!=COMMIT:raise Stop('Foreign backup state')
    for rel in REL:
        f=VENDOR/rel;b=STATE/Path(rel).name
        plain(f);plain(b)
        if digest(b)!=m['source_vendor_sha256'][rel]:raise Stop('Backup corrupted')
        if digest(f) not in (m['source_vendor_sha256'][rel],m['candidate_sha256'][rel]):
            raise Stop('Installed file was changed externally; manual review needed: '+rel)
    for rel in REL:
        f=VENDOR/rel;b=STATE/Path(rel).name
        if digest(f)!=m['source_vendor_sha256'][rel]:atomic(f,b.read_bytes())
    for rel in REL:
        if digest(VENDOR/rel)!=m['source_vendor_sha256'][rel]:raise Stop('Restore verification failed: '+rel)
    shutil.rmtree(STATE)
    print('ROOT ROLLBACK PASS: factory Word bundles restored')

def rollback():
    if os.geteuid()==0:raise Stop('Do not sudo this command')
    version();idle()
    if not STATE.exists():raise Stop('No portable root backup available')
    run(['sudo','-v'])
    privileged_call('--_root-rollback')
    _,_,_,state,plugin=path_set(user_home())
    plain(state,'dir');plain(state/'state.json')
    info=json.loads((state/'state.json').read_text())
    if info.get('plugin_created') is not True or info.get('plugin_path')!=str(plugin):
        raise Stop('Plugin state mismatch; vendor restored, plugin must be inspected manually')
    safe_plugin_tree(plugin)
    if plugin.exists():shutil.rmtree(plugin)
    shutil.rmtree(state)
    print('ROLLBACK PASS: factory Word and previous plugin state restored')

def status():
    version()
    home=user_home()
    _,_,candidate,state,plugin=path_set(home)
    m=None
    if (candidate/'manifest.json').is_file():
        try:_,m=candidate_check_skip_original(home)
        except (Stop,OSError,ValueError,KeyError):pass
    for rel in REL:
        p=VENDOR/rel
        if not p.exists():print(rel,'MISSING');continue
        h=digest(p)
        label=('PORTABLE RC5/10s' if m and h==m.get('candidate_sha256',{}).get(rel)
               else 'FACTORY / OTHER (not verified)')
        print(rel,label,h)
    print('root-backup:', 'present' if STATE.exists() else 'absent')
    print('plugin:', 'present' if plugin.exists() else 'absent')
    print('user-state:', 'present' if state.exists() else 'absent')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    for option in ('check','build','install','status','rollback','_root-apply','_root-rollback'):
        mode.add_argument('--'+option,action='store_true')
    a=p.parse_args()
    try:
        if a.check:user_check()
        elif a.build:source_build()
        elif a.install:install()
        elif a.status:status()
        elif a.rollback:rollback()
        elif getattr(a,'_root_apply'):root_apply()
        elif getattr(a,'_root_rollback'):root_rollback()
    except (Stop,RuntimeError,OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError,ImportError,KeyboardInterrupt) as ex:
        print('SAFE STOP:',ex,file=sys.stderr)
        return 2
    return 0
if __name__=='__main__':sys.exit(main())
