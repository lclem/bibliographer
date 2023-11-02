#!/bin/bash

bibfile=$1

# first make list of all entries for the loop
#bib2bib -oc $1.lst  --no-comment $1

# then loop thru them
for xkey in $(cat $1.lst); do
  mkdir -p "$xkey.bib"
  bibtool -r biblatex '--select{"^'$xkey'$"}' -i $1 -o "./$xkey.bib/$xkey.bib" -- 'print.use.tab = {0}' -- 'print.line.length = {999999999}' -- 'new.entry.type {chapter}' -- 'new.entry.type {url}' -- 'new.entry.type {jurthesis}' -- 'new.entry.type {slides}' -- 'new.entry.type {bachelorthesis}' -- 'new.entry.type {paper}' -- 'new.entry.type {bibtex}'
done
