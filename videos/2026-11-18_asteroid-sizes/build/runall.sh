#!/bin/bash
cd "$(dirname "$0")"
echo hook sand chel tung crater apophis global chix dart outro | tr ' ' '\n' | xargs -P 2 -I{} sh -c 'python3 render.py scene {} >> render.log 2>&1'
echo ALLDONE >> render.log
