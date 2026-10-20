#!/usr/bin/env python3
"""Safely upload the CURRENT v1.0.0-rc.1 source ZIP to a GitHub draft release.

Requires both GitHub CI jobs to be completed SUCCESS on the exact HEAD commit.
Does not make a public stable release or write to installed ONLYOFFICE.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO='Rambo-Junior/onlyoffice-native-overtype'
TAG='v1.0.0-rc.1'
WORKFLOWS={'Source checks','Pinned SDKJS build'}


def cmd(*args):
    return subprocess.check_output([str(x) for x in args],cwd=ROOT,text=True,stderr=subprocess.STDOUT).strip()


def run(*args):
    print('$',*args,flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)


def verify_archive(archive:Path):
    if not archive.is_file():raise RuntimeError('Source ZIP missing: '+str(archive))
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise RuntimeError('Duplicate ZIP members')
        if 'SHA256SUMS' not in names:raise RuntimeError('Missing SHA256SUMS in ZIP')
        for line in z.read('SHA256SUMS').decode('utf8').splitlines():
            digest,rel=line.split('  ',1)
            if rel.startswith('/') or '..' in Path(rel).parts:raise RuntimeError('Unsafe path in ZIP manifest')
            if rel not in names:raise RuntimeError('Missing ZIP input: '+rel)
            if hashlib.sha256(z.read(rel)).hexdigest()!=digest:raise RuntimeError('ZIP hash mismatch: '+rel)
        cfg=json.loads(z.read('plugin/config.json'))
        if cfg['version']!='1.0.0-rc.1':raise RuntimeError('Incorrect source ZIP version')
    print('SOURCE ZIP PASS:',archive,'SHA256',hashlib.sha256(archive.read_bytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--publish-draft',action='store_true',help='Make existing draft public as a PRERELEASE; not stable')
    args=parser.parse_args()
    if cmd('git','branch','--show-current')!='main':raise RuntimeError('Expected main')
    if cmd('git','status','--porcelain'):raise RuntimeError('Uncommitted changes')
    if cmd('git','remote','get-url','origin')!='https://github.com/'+REPO+'.git':raise RuntimeError('Unexpected Git origin')
    head=cmd('git','rev-parse','HEAD')
    if cmd('git','ls-remote','origin','refs/heads/main').split('\t')[0]!=head:raise RuntimeError('Local HEAD != pushed main')
    if json.loads((ROOT/'plugin/config.json').read_text())['version']!='1.0.0-rc.1':raise RuntimeError('Version mismatch')
    archive=ROOT.parent/(f'onlyoffice-native-overtype-{TAG}-source.zip')
    verify_archive(archive)
    runs=json.loads(cmd('gh','run','list','-R',REPO,'--commit',head,'--limit','30',
                        '--json','workflowName,status,conclusion'))
    successful={r.get('workflowName') for r in runs if r.get('status')=='completed' and r.get('conclusion')=='success'}
    if not WORKFLOWS.issubset(successful):
        raise RuntimeError('GitHub CI incomplete/failed for HEAD. Success: '+repr(successful)+', required: '+repr(WORKFLOWS))
    print('CI PASS: Source checks + pinned SDKJS build on',head)
    if args.publish_draft:
        show=json.loads(cmd('gh','release','view',TAG,'-R',REPO,'--json','isDraft,isPrerelease,tagName,url'))
        if show['isDraft'] is not True or show['isPrerelease'] is not True:raise RuntimeError('Expected an existing draft prerelease')
        print('Publishing PRERELEASE (not a stable release).')
        run('gh','release','edit',TAG,'-R',REPO,'--draft=false')
        print('PUBLISHED PRERELEASE:',cmd('gh','release','view',TAG,'-R',REPO,'--json','url','--jq','.url'))
        return
    r=subprocess.run(['gh','release','view',TAG,'-R',REPO,'--json','isDraft'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if r.returncode==0:raise RuntimeError('Release tag already exists; inspect it rather than overwriting')
    if cmd('git','ls-remote','--tags','origin','refs/tags/'+TAG):raise RuntimeError('Remote tag already exists')
    run('git','tag','-a',TAG,'-m','Release candidate '+TAG)
    run('git','push','origin',TAG)
    run('gh','release','create',TAG,archive,'-R',REPO,'--title','Native Overtype '+TAG,
        '--notes-file','GITHUB_RELEASE_NOTES_V1_EN.md','--prerelease','--draft')
    print('DRAFT PRERELEASE CREATED: review then run --publish-draft. NOT a stable release.')

if __name__=='__main__':
    try:main()
    except (RuntimeError,subprocess.CalledProcessError,OSError,KeyError,ValueError,zipfile.BadZipFile) as ex:
        print('SAFE STOP:',ex,file=sys.stderr)
        sys.exit(2)
