#!/bin/bash

bibfile=$1

# first make list of all entries for the loop
bib2bib -oc $1.lst  --no-comment $1

# then loop thru them
for xkey in $(cat $1.lst); do
  bibtool '--select{"^'$xkey'$"}' -i $1 -o "$xkey.bib" -- 'print.use.tab = {0}' -- 'print.line.length = {999999999}' 
done
