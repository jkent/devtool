#!/bin/bash

if [ -z "${ENV}" ]; then
  echo "ENV not set!"
  exit 1;
fi

LOG=${ENV}/log.txt

echo "------------------------------------------------------------------------------" >> ${LOG}
echo `basename $0` - `date` >> ${LOG}
echo >> ${LOG}

task_begin() {
  echo "*** $1" >> ${LOG}
  echo -n "*** $1..." >&2
}

task_end() {
  echo "done" >&2
}

task_fail() {
  echo "failed"
  if [ -z "$1" ]; then
    echo "See log for details"
  else
    echo "$1" >> ${LOG}
    echo "$1" >&2
  fi
  exit 1
}

try() {
  echo "%" "$@" >> ${LOG}
  "$@" >> ${LOG} 2>&1 || task_fail
}

download() {
  task_begin "Downloading $1"
  echo "%" "wget --progress=dot \"$2\" -O \"$3\"" >> ${LOG}
  wget --progress=dot "$2" -O "$3" 2>&1 | grep --line-buffered "%" | \
    sed -u -e "s,\.,,g" | awk '{printf("%-4s\b\b\b\b", $2)}' >&2 || task_fail
  task_end
}

