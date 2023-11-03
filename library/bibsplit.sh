#!/bin/bash
bibfile=$1

# first make list of all entries for the loop
bib2bib -oc $1.lst  --no-comment $1

# then loop thru them
for xkey in $(cat $1.lst); do
  var=$(echo "$xkey" | tr '/' '_')
  set -o xtrace
  dir="./entries/$var"
  mkdir -p "$dir"
  bibtool -r biblatex --preserve.key.case=on --preserve.keys=on '--select{"^'$xkey'$"}' -i $1 -o "$dir/$var.bib" -- 'print.use.tab = {0}' -- 'print.line.length = {999999999}' -- 'new.entry.type {chapter}' -- 'new.entry.type {url}' -- 'new.entry.type {jurthesis}' -- 'new.entry.type {slides}' -- 'new.entry.type {bachelorthesis}' -- 'new.entry.type {paper}' -- 'new.entry.type {bibtex}'
  set +o xtrace
done