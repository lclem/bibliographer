import glob, os, sys
import contextlib
import bibtexparser as parser
import string

def parsebib(bibfile):
    library = parser.parse_file(bibfile)

    result = []
    for entry in library.entries:
        fields = entry.fields_dict

        if 'File' in fields:
            print(f"{fields['File'].value}")

            i = 2
            while ('file-' + str(i)) in fields:
                print(f"{fields['file-' + str(i)].value}")
                i += 1

bibfile = sys.argv[1]
#print(f"BIBFILE {bibfile}\n")

parsebib(bibfile)