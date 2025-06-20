#!/bin/sh

by_one="$( find . -path "./migrations" -prune -o -type f -name "*.py" -print  | \
   while read -r fn; do echo "$( grep -v -e '^\s*$' $fn | wc -l ) $fn"; done )"
echo "$by_one"
printf "total: %s\n" "$( echo "$by_one" | cut -d' ' -f1 | paste -sd+ | bc )"
