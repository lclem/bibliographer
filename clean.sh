#!/bin/bash
find ./library -name \*.md -exec rm -f {} \;
rm -fr docs
rm -fr library/doi