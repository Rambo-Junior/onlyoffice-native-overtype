#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if (( EUID==0 ));then echo 'Run as normal user, NOT with sudo.' >&2;exit 2;fi
exec /usr/bin/python3 "$HERE/portable.py" "$@"
