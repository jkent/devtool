#!/bin/bash

if [ -z "${ENV}" ]; then
  echo "ENV not set!"
  exit 1;
fi

kconfig_path="${ENV}/tools/kconfig-frontends"

if [ ! -x "${kconfig_path}/bin/kconfig-conf" ]; then
  task_begin "Setting up kconfig-frontends"
  if [ ! -d "${ENV}/build/kconfig-frontends" ]; then
    try mkdir -p "${ENV}/build"
    try cd build
    try git clone git://ymorin.is-a-geek.org/kconfig-frontends
  fi
  try cd "${ENV}/build/kconfig-frontends"
  try git clean -dxf
  try git reset --hard HEAD
  try git pull
  try patch -p1 < "${ENV}/patches/kconfig-frontends.patch"
  try ./bootstrap
  try ./configure --prefix "${kconfig_path}"
  try make
  try make install
  task_end
fi

export CFG=${ENV}/.config
export PATH=${kconfig_path}/bin:${ENV}/scripts:${PATH}

kconfig() {
  kconfig-gconf "$1" || kconfig-mconf "$1"
  return $?
}

value() {
  if [ -f "${CFG}" ]; then
    kconfig-tweak --file "${CFG}" -s "$1"
  fi
}

selected() {
  if [ ! -f "${CFG}" ]; then
    return 1
  fi

  if [ `kconfig-tweak --file "${CFG}" -s "$1"` != y ]; then
    return 1
  fi
}

