#!/bin/bash

#&& rsync -aP library docs/
# python3.10 ./indexer.py > /dev/null
# python3.10 ./generate_doi_links.py > /dev/null

python3 ./indexer.py > /dev/null
python3 ./generate_doi_links.py > /dev/null

pelican
