#!/bin/python3

import string, requests, re, subprocess, os, contextlib
from termcolor import colored
from pathlib import Path
import bibtexparser as parser

# change things like
# DOI           = "10.1007/11417170\_5",
# into things like
# DOI           = {10.1007/11417170_5}

doiPattern = "^10\.[0-9][0-9][0-9][0-9][0-9]*"

def doiValid(doi):
    return re.search(doiPattern, doi) and not "\\" in doi

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
    # print(f"GITADD {bibFile}")
    # subprocess.run(["git", "add", bibFile])

def processBib(root, bibFile):

    try:
        print(f"BIB {root}/{bibFile}")

        layers = [ parser.middlewares.SortFieldsAlphabeticallyMiddleware(), parser.middlewares.SortFieldsCustomMiddleware(order = tuple(("doi",)), case_sensitive = False, allow_inplace_modification = True) ]
        library = parser.parse_file(bibFile, parse_stack = None, append_middleware = layers)

        for entry in library.entries:
            # fields = entry.fields_dict
            fields = {k.lower(): v for k, v in entry.fields_dict.items()}

            # newEntry = library.Entry()

            # for key in fields:
            #     lowerKey = key.lower()
            #     if lowerKey != key:
            #         print(f"KEY {key} --> {lowerKey}")
            #         entry.set_field(parser.model.Field(lowerKey, fields[key].value))
            #         del entry.fields_dict[key] # this may do nothing
            
            doi = getValue(fields, 'doi', "").strip()

            if doi == "":
                print(f"NO DOI | {bibFile}")

                if getValue(fields, 'DOI', "").strip() != "":
                    raise Exception("capitalisation problem")

            else:

                origDoi = doi
                doi = doi.removeprefix("https://dx.doi.org/")
                doi = doi.removeprefix("https://doi.org/")
                doi = doi.removeprefix("http://dx.doi.org/")
                doi = doi.removeprefix("http://doi.org/")
                doi = doi.removeprefix("http://doi.ieeecomputersociety.org/")
                doi = doi.removeprefix("https://doi.acm.org/")
                doi = doi.removeprefix("http://doi.acm.org/")

                doi = doi.replace("\\\\_", "_")
                doi = doi.replace("\\_", "_")

                if not doiValid(doi):
                    print(colored("INVALID", "red"), f"{doi} {root}/{bibFile}")
                else:
                    print(colored("VALID", "green"), f"{doi} {root}/{bibFile}")

                if doi != origDoi:
                    entry.set_field(parser.model.Field("doi", doi))
                    writeBib(entry, bibFile)

    except Exception as e:
        print(f"EXCEPT {root}/{bibFile} - {e}")

# def saveBibEntry(entry):

#     key = entry.key
#     key = key.encode('utf-8').decode("ascii", "ignore")
#     key = sanitise(key)

#     print(colored("KEY", "green"), f"{key}")

#     directory = f"./entries/{key}"

#     if os.path.exists(directory):
#         print(colored("EXISTS", "red"), f"{directory}")
#         return False
    
#     Path(directory).mkdir(parents=True, exist_ok=True)

#     fileName = f"{directory}/{key}.bib"
#     library = parser.Library([entry])
#     parser.write_file(fileName, library)

#     print(f"GIT-ADD {fileName}")
#     subprocess.run(["git", "add", fileName])

#     return True

for root, dirs, _ in os.walk("./entries"):
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            for _, _, files in os.walk("./"):
                for bibFile in files:
                    if bibFile.endswith(".bib"):
                        processBib(cwd, bibFile)