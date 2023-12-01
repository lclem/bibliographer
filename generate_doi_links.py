#!/usr/bin/python3

# find all bib files in library/entries
# for each bib file with a DOI identifier of the form https://dx.doi.org/DOI,
# create a folder docs/doi/DOI containing a file called index.bib with the BIB contents

# one can then get the BIB contents by fetching https://lclem.github.io/bibliographer/doi/DOI

import os
import shutil
import contextlib
import bibtexparser as parser

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def getValue(dict, key, default):
    if key in dict:
        return dict[key].value
    else:
        return default

def writeBib(entry, bibFile):
    library = parser.Library([entry])
    parser.write_file(bibFile, library)

def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

def parseBib(bibFile):
    library = parser.parse_file(bibFile)

    result = []
    for entry in library.entries:
        fields = {k.lower(): v for k, v in entry.fields_dict.items()}
        doi = getValue(fields, 'doi', "").strip()

        if doi != "":
            doi = remove_prefix(doi, "https://dx.doi.org/")
            doi = remove_prefix(doi, "https://doi.org/")
            doi = remove_prefix(doi, "http://dx.doi.org/")
            doi = remove_prefix(doi, "http://doi.org/")

            result.append((entry, doi))

    return result

for root, dirs, _ in os.walk("./library/entries"):
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            # print(f"CWD {os.getcwd()}")
            # print(f"ROOT {root}, DIR {dir}")
            for _, _, files in os.walk("./"):
                for bibFile in files:
                    if bibFile.endswith(".bib"):
                        for entry, doi in parseBib(bibFile):

                            print(f"DOI {doi}")
                            dst = f"../../doi/{doi}/index.html"

                            dstfolder = os.path.dirname(dst)
                            if not os.path.exists(dstfolder):
                                os.makedirs(dstfolder)

                            shutil.copy(bibFile, dst)
