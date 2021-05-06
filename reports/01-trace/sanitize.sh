#!/bin/bash
#
# Sanitize log files for comparison.
#
# https://stackoverflow.com/questions/44019/an-easy-way-to-diff-log-files-ignoring-the-time-stamps
#

# Trim empty lines
sed -r '/^\s*$/d' | \

# Trim comment lines
sed -r '/^#.*$/d' | \

# Trim timestamps
#cut -b26- # | \

# Trim timestamps and unnecessary prefix
#cut -b42- # | \

# Trim all metadata, only display messages
cut -b69- # | \


# Mitigate tokens like `ST55B7A1F2E910` or `_PLAN0x56441b49d8e0`
# => Maybe not a good idea?
#sed "s/ST55[0-9A-Z]*//"
#sed "s/ST55//"
#sed "s/_PLAN0x[0-9a-z]*//"
