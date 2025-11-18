#!/usr/bin/env bash
set -e

Workspace="$(pwd)"

echo "Workspace: $Workspace"

level1="$(dirname "$Workspace")"

target="$level1/development_repos"

if [ ! -d "$target" ]; then
    echo "Creating folder: $target"
    mkdir -p "$target"
else
    echo "Folder already exists: $target"
fi

echo "Done."