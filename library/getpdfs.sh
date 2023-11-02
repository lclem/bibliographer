#!/bin/bash

find . -type f -name \*.bib -exec ./getpdf.sh {} \;
