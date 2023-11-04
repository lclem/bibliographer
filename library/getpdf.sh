#!/bin/bash

DIR="$(dirname "${1}")"
FILE="$(basename "${1}")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "BIB $DIR/$FILE"
python3 ./getpdf.py $1 | while read pdf ; do
    PDFFILE="/home/pi/nextcloud/files/Media/Library/Articles/$pdf"
    NEWPDFFILE="$DIR/$pdf"

    if [ -f "$PDFFILE" ] && ! [ -f "$NEWPDFFILE" ]; then
        printf "${GREEN}PDF${NC} $pdf\n" ;
        mv "$PDFFILE" "$DIR" ;
    elif [ -f "$NEWPDFFILE" ]; then
        printf "${YELLOW}SKIP${NC} $pdf\n" ;
    else
        printf "${RED}ERR${NC} $pdf\n" ;
        echo "$FILE - $pdf" >> getpdf.err ;
    fi
done