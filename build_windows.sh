#!/usr/bin/env bash
set -euo pipefail

echo "Building Windows executable using Docker image cdrx/pyinstaller-windows"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed. Install Docker or build on Windows." >&2
  exit 1
fi

ROOT_DIR=$(pwd)
mkdir -p "$ROOT_DIR/dist" "$ROOT_DIR/build"

docker pull cdrx/pyinstaller-windows:latest

# Run PyInstaller inside the container. This aims to produce a single-windowed exe.
docker run --rm -v "$ROOT_DIR":/src -w /src cdrx/pyinstaller-windows \
  pyinstaller --noconfirm --onefile --windowed main.py

echo "Build finished. Check the 'dist' directory for the .exe file."

echo "Note: PyQt6 apps may require extra Qt plugins/DLLs; test the produced exe on a Windows host." 
