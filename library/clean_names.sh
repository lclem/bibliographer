#!/bin/bash

find . -type d  -name \*:\* -exec ./clean_name.sh {} \;
