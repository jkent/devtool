#!/bin/sh

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

