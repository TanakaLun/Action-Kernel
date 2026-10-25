#!/bin/bash
# 打包 nftables LKM 模块集（net_generic 版）：
#   从已完成的 O=out 构建提取 .ko，按 modules.dep 拓扑序生成安装脚本，
#   输出 nft-lkm.tar.gz（模块 + install-nftables.sh）。
# 用法:
#   bash package_nft_lkm.sh <common_dir> <out_dir> <artifact_dir>
# 例: bash package_nft_lkm.sh kernel_workspace/kernel_platform/common \
#       kernel_workspace/kernel_platform/common/out "$GITHUB_WORKSPACE"
set -euo pipefail

COMMON="${1:?common dir}"
OUT="${2:?out dir}"
ART="${3:?artifact dir}"
STAGE="$OUT/nft-lkm-stage"
REL="$(cat "$OUT/include/config/kernel.release")"

cd "$COMMON"
make -j"$(nproc --all)" LLVM_IAS=1 LLVM=1 ARCH=arm64 \
  CROSS_COMPILE=aarch64-linux-gnu- CC="ccache clang" LD=ld.lld HOSTLD=ld.lld \
  O="$OUT" INSTALL_MOD_PATH="$STAGE" modules_install
depmod -b "$STAGE" "$REL"

STRIP="$(find ../prebuilts-master/clang/host/linux-x86 -name llvm-strip 2>/dev/null | head -1)"
STRIP="${STRIP:-/usr/bin/strip}"

python3 - "$STAGE" "$ART" <<'PY'
import os, glob, sys

stage = glob.glob(sys.argv[1] + "/lib/modules/*/")[0]
art = sys.argv[2]
dep = os.path.join(stage, "modules.dep")
deps, path_of = {}, {}
for line in open(dep):
    left, _, right = line.strip().partition(":")
    name = os.path.basename(left)[:-3]
    path_of[name] = left
    deps[name] = [os.path.basename(x)[:-3] for x in right.split() if x]
deps = {k: [d for d in v if d in deps] for k, v in deps.items()}

order, seen = [], set()
def visit(n):
    if n in seen:
        return
    seen.add(n)
    for d in deps.get(n, []):
        visit(d)
    order.append(n)
for n in sorted(deps):
    visit(n)

moddir = os.path.join(art, "nft-lkm")
os.makedirs(moddir, exist_ok=True)
for n, p in path_of.items():
    os.system('cp -f "%s" "%s/%s.ko"' % (os.path.join(stage, p), moddir, n))

loads = "\n".join("load %s" % m for m in order)
unloads = "\n".join("unload %s" % m for m in reversed(order))
script = f'''#!/system/bin/sh
# nftables LKM 安装脚本 — net_generic 版（纯 insmod，内核零改动）
# OnePlus Ace 2 (sm8475), kernel 5.10.236-android12-9-Mortis
set -u
MODDIR="${{1:-/data/adb/nft-lkm}}"
ACTION="${{2:-load}}"
[ "$(id -u)" = "0" ] || {{ echo "!! 需要 root"; exit 1; }}
command -v insmod >/dev/null 2>&1 || {{ echo "!! 找不到 insmod"; exit 1; }}
loaded() {{ grep -q "^$1 " /proc/modules 2>/dev/null; }}
load() {{
    m="$1"
    if loaded "$m"; then echo "  = $m (已加载)"; return 0; fi
    if [ ! -f "$MODDIR/$m.ko" ]; then echo "  ! 缺少 $m.ko"; return 1; fi
    if insmod "$MODDIR/$m.ko" 2>/dev/null; then
        echo "  + $m"
    else
        echo "  !! insmod $m 失败: $(insmod "$MODDIR/$m.ko" 2>&1 | tail -1)"
        return 1
    fi
}}
unload() {{
    m="$1"
    if ! loaded "$m"; then echo "  = $m (未加载)"; return 0; fi
    if rmmod "$m" 2>/dev/null; then echo "  - $m"; else echo "  ! $m 正在使用，跳过"; fi
}}
case "$ACTION" in
load)
    echo ">> 加载 nftables 模块 (dir=$MODDIR)"
{loads}
    echo ">> 完成。已加载:"
    grep -E '^(nf_tables|nft_|nf_log)' /proc/modules | awk '{{print "   "$1}}'
    ;;
unload)
    echo ">> 卸载 nftables 模块 (逆序)"
{unloads}
    ;;
*)
    echo "用法: sh $0 [模块目录] [load|unload]"; exit 1;;
esac
'''
open(os.path.join(art, "install-nftables.sh"), "w").write(script)
os.chmod(os.path.join(art, "install-nftables.sh"), 0o755)
print("generated install-nftables.sh, %d modules" % len(order))
PY

echo "--- strip debug ---"
for f in "$ART"/nft-lkm/*.ko; do
    "$STRIP" --strip-debug "$f"
done

cd "$ART"
tar czf nft-lkm.tar.gz nft-lkm install-nftables.sh
sha256sum nft-lkm.tar.gz
echo "NFT_LKM_PACKAGED: $ART/nft-lkm.tar.gz ($(tar tzf nft-lkm.tar.gz | grep -c '\.ko$') modules)"
