#!/bin/bash

SECONDS=0

mkdir -p ./docs

#&& rsync -aP library docs/
# python3.10 ./indexer.py > /dev/null
# python3.10 ./generate_doi_links.py > /dev/null

python3 ./indexer.py > /dev/null
python3 ./generate_doi_links.py > /dev/null

du -hs ./library | cut -d'.' -f1 | xargs | tr -d '\n' > ./themes/bootstrap2/templates/size.txt

pelican

duration=$SECONDS
echo "$(($duration / 60))m$(($duration % 60))s" > ./docs/elapsed.txt
