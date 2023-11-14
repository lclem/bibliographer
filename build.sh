#!/bin/bash

#&& rsync -aP library docs/
python3 ./indexer.py
python3 ./generate_doi_links.py
pelican