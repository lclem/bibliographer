#!/bin/bash

#&& rsync -aP library docs/
python ./indexer.py
python ./generate_doi_links.py
pelican
