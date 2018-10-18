#!/bin/bash

MACHINE_TYPE=`uname -m`

if [ ${MACHINE_TYPE} == 'X86_64']; then
  # 64-bit stuff here
  ARCH=64
else
  ARCH=32
fi 

MONKEY_FILE = monkey-
echo $MACHINE_TYPE