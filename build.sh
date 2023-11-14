#!/bin/bash

#&& rsync -aP library docs/
/usr/bin/python3 ./indexer.py
/usr/bin/python3 ./generate_doi_links.py
pelican
