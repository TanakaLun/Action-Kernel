# Fuse BPF Dynamic Backport

`fuse-bpf-backport.patch` is applied only inside the disposable CI checkout.
It is not applied to or committed in the vendor kernel repository.

The patch is based on the final Fuse BPF implementation from
`ESK-Project/android12-5.10-gki`, including the follow-up correctness and ABI
fixes. It was checked against the local `ker` tree with GNU `patch`.

Apply it before configuration and compilation:

```sh
Tools/apply_fuse_bpf.sh kernel_workspace/kernel_platform/common
```

The script performs a dry run first and exits on failure. `--fuzz=3` is needed
because the vendor tree has small surrounding-context differences; it does not
silently ignore failed hunks.

The CI option is disabled by default. Enable `fuse_bpf` only after reviewing
the target source and userspace ABI requirements. The patch also requires
`CONFIG_BPF=y` and `CONFIG_FUSE_BPF=y` in the generated kernel configuration.
