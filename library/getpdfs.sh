#!/bin/bash

find . -mindepth 2 -type f -name \*.bib -exec ./getpdf.sh {} \;