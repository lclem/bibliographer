#!/usr/bin/python3

import string, requests, re, subprocess, os
from termcolor import colored
from pathlib import Path
import bibtexparser as parser

doiPattern = "^10\.[0-9][0-9][0-9][0-9][0-9]*"

def doiValid(doi):
    return re.search(doiPattern, doi)

valid_characters = string.ascii_letters + string.digits

def sanitise(str):
    res = "".join(c for c in str if c in valid_characters)
    return res

def saveBibEntry(entry):

    key = entry.key
    key = key.encode('utf-8').decode("ascii", "ignore")
    key = sanitise(key)

    print(colored("KEY", "green"), f"{key}")

    directory = f"./entries/{key}"

    if os.path.exists(directory):
        print(colored("EXISTS", "red"), f"{directory}")

        # check whether we have this doi in the library / webpage
        # return True if we have it already
        # if not, change the key to a fresh one and add it

        return False
    
    Path(directory).mkdir(parents=True, exist_ok=True)

    fileName = f"{directory}/{key}.bib"
    library = parser.Library([entry])
    parser.write_file(fileName, library)

    print(f"GIT-ADD {fileName}")
    subprocess.run(["git", "add", fileName])

    return True

def fetchDoi(doi):

    # TODO: first check that we don't have this doi already in the repo / webpage

    doiUrl = f"https://dx.doi.org/{doi}"
    headers = {'Accept': 'application/x-bibtex; charset=utf-8'}

    response = requests.get(doiUrl, headers = headers, allow_redirects = True)

    if not response.status_code == 200:
        print(f"NO DOI {response}")
        return

    try: 
        response = response.content.decode().strip()
        print(f"DOI {doi}")
        print(response)

        library = parser.parse_string(response)
        for entry in library.entries:
            if not saveBibEntry(entry):
                return False

    except Exception as e:
        print(f"EXCEPT {e}")
        return False
    
    return True

doisWeHaveFileName = "doisWeHave.txt"
doisWeDontHaveFileName = "doisWeDontHave.txt"

doisWeHave = set()
doisWeDontHave = set()
# doisWeStillDontHave = set()

# load all known dois
with open(doisWeHaveFileName, "r") as f:
    for line in f:
        doi = line.strip()
        doisWeHave.add(doi)

# load all unknown dois
with open(doisWeDontHaveFileName, "r") as f:
    for line in f:
        doi = line.strip()
        if doi not in doisWeHave:
            doisWeDontHave.add(doi)

# get a bib for all unknown dois
for doi in doisWeDontHave:
    if doiValid(doi) and doi not in doisWeHave:
        if fetchDoi(doi):
            doisWeHave.add(doi)
            with open(doisWeHaveFileName, 'a') as f:
                f.write(f"{doi}\n")

# update the unknown dois based on what we found
with open(doisWeDontHaveFileName, 'w') as f:
    for doi in doisWeDontHave:
        if doi not in doisWeHave:
            f.write(f"{doi}\n")