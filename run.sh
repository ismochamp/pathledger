#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p runtime
if [ ! -x runtime/pathledger ] || [ src/pathledger.cpp -nt runtime/pathledger ]; then
  "${CXX:-c++}" -std=c++17 -O2 -Wall -Wextra -Wpedantic src/pathledger.cpp -o runtime/pathledger
fi
exec python3 server.py
