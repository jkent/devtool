#!/bin/bash

if [ -z "${ENV}" ]; then
  echo "ENV not set!"
  exit 1;
fi

kconfig_path="${ENV}/host-tools/kconfig"

if [ ! -x "${kconfig_path}/conf" ]; then
  task_begin "Setting up kconfig-frontends"
  try cd "${kconfig_path}"
  try make clean
  try make
  task_end
fi

export CFG="${ENV}/.config"
export PATH="${ENV}/scripts:${PATH}"

mconf() {
  "$kconfig_path/mconf" "$@"
}

tweak() {
  "$kconfig_path/tweak" "$@"
}

value() {
  if [ -f "${CFG}" ]; then
    tweak --file "${CFG}" -s "$1"
  fi
}

selected() {
  if [ ! -f "${CFG}" ]; then
    return 1
  fi

  if [ `tweak --file "${CFG}" -s "$1"` != y ]; then
    return 1
  fi
}

