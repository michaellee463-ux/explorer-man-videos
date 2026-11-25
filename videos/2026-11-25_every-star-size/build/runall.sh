#!/bin/bash
cd "$(dirname "$0")"
rm -f render.log
echo vy biggest heavy outro betel hook sun sirius arcturus aldebaran rigel antares | tr ' ' '\n' | xargs -P 2 -I{} sh -c 'python3 render.py scene {} >> render.log 2>&1'
echo ALLDONE >> render.log
