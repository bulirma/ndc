#!/bin/sh

by_one="$( find . -name "*.py"  | \
   while read -r fn; do echo "$( grep -v -e '^\s*$' -e '^\s*#.*$' $fn | wc -l ) $fn"; done )"
echo "$by_one"
printf "total: %s\n" "$( echo "$by_one" | cut -d' ' -f1 | paste -sd+ | bc )"
