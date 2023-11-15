#!/bin/bash

#&& rsync -aP library docs/
python3.10 ./indexer.py
python3.10 ./generate_doi_links.py
pelican
