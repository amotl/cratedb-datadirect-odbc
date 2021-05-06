#!/bin/bash
#
# Sanitize and compare log files.
#
# https://stackoverflow.com/questions/44019/an-easy-way-to-diff-log-files-ignoring-the-time-stamps
#

driver=$1

# Unified diff format
#diff --unified --width=200 <(cat ${driver}-executemany-regular.log | ./sanitize.sh) <(cat ${driver}-executemany-fast.log | ./sanitize.sh)

# Side-by-side format
diff --side-by-side --width=200 <(cat ${driver}-executemany-regular.log | ./sanitize.sh) <(cat ${driver}-executemany-fast.log | ./sanitize.sh)
