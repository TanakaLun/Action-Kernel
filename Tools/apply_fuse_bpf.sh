#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
kernel_tree=${1:?usage: apply_fuse_bpf.sh <kernel-tree>}
patch_file="$repo_root/Patches/fuse-bpf-backport.patch"

if [[ ! -d "$kernel_tree/fs/fuse" || ! -f "$kernel_tree/Makefile" ]]; then
  printf 'Not a kernel source tree: %s\n' "$kernel_tree" >&2
  exit 2
fi

if [[ ! -s "$patch_file" ]]; then
  printf 'Missing Fuse BPF patch: %s\n' "$patch_file" >&2
  exit 2
fi

printf 'Checking Fuse BPF backport against %s\n' "$kernel_tree"
patch --dry-run --batch --forward --fuzz=3 -p1 -d "$kernel_tree" < "$patch_file"
patch --batch --forward --fuzz=3 -p1 -d "$kernel_tree" < "$patch_file"
