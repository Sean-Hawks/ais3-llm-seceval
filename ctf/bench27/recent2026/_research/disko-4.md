# disko-4

- **Category:** Forensics
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/disko-4/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
Recover a deleted flag file from a disk image. Unlike earlier DISKO challenges, the file has been deleted, so forensic recovery is required.

## Attack / Technique
Deleted File Recovery via Filesystem Forensics. Deleting clears filesystem metadata but data persists until overwritten; recover via filesystem-aware tools (residual metadata) or byte-level carving.

## Step-by-Step Solution
```bash
# 1. Decompress
gunzip disko-4.dd.gz
# 2. Verify filesystem
file disko-4.dd
fdisk -l disko-4.dd
# 3. List files including deleted (asterisk prefix)
fls -r -o 2048 disko-4.dd
# 4. Recover by inode
icat -o 2048 disko-4.dd <inode_number> > recovered_flag.txt
# 5. Bulk recovery
tsk_recover -o 2048 disko-4.dd output_dir/
# 6. Quick string search
strings disko-4.dd | grep picoCTF
```
Tools: The SleuthKit (fls, icat), tsk_recover, extundelete, plus strings/gunzip/file. Writeup includes a Python script automating multiple recovery methods with fallbacks. No concrete flag reproduced.

## Challenge Files
Provides a compressed disk image `disko-4.dd.gz`. Download via challenge platform (no explicit URL).

## needs_docker
NO — static file challenge; download image and analyze locally.
