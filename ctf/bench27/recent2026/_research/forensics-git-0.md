# forensics-git-0

- **Category:** Forensics
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/forensics-git-0/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
Receive a disk image containing a git repository; find the flag in the disk image. Introductory challenge — no advanced recovery needed.

## Attack / Technique
Git history forensics — inspect git repos for hidden flags across commits, branches, tags, stashes, git objects.

## Step-by-Step Solution
```bash
# 1. Quick search
strings disk.img | grep "picoCTF{"
# 2. Mount (calculate offset = start_sector * 512 if partitioned)
sudo mount -o loop,ro disk.img /mnt/evidence
sudo mount -o loop,ro,offset=<offset> disk.img /mnt/evidence
# 3. Locate git repo
find /mnt/evidence -name ".git" -type d
# 4. Comprehensive inspection
cd /path/to/repo
git log --all -p | grep "picoCTF{"
git branch -a
git tag -l
git stash list
git log --all --format='%H %s'
# 5. Specific commit
git show <commit_hash>
git show <commit_hash>:<filename>
```
Writeup includes a Python3 solver with four methods: raw strings+grep, binary pattern matching, mount-based git inspection, 7z extraction. Searches git objects, pack files, commit diffs, branches, tags, stashes, working-tree files. No concrete flag reproduced.

## Challenge Files
Disk image file (.img/.dd/.raw). Download via challenge platform (no explicit URL).

## needs_docker
NO — static file analysis only.
