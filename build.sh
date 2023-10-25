#!/bin/bash

python3 ./indexer.py && pelican && rsync -aP library docs/