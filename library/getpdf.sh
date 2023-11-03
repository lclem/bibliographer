#!/bin/bash

DIR="$(dirname "${1}")"
FILE="$(basename "${1}")"

echo "BIB $DIR - $FILE"
python3 ./getpdf.py $1 | while read pdf ; do echo PDF $pdf ; rsync -aP "/home/pi/nextcloud/files/Media/Library/Articles/$pdf" "$DIR/" ; done